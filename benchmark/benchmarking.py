import inspect
import json
import math
import time
# noinspection PyPep8Naming
from datetime import datetime as DateTime
import itertools
from pathlib import Path
from types import FunctionType
from typing import Self, Callable, Dict, overload, Iterable, Sequence, Optional, Generator, Any

import colorama

from utils import *

__all__ = (
    "Subject",
    "Benchmark",
    "run_benchmarks",
    "TestCaseResult",
    "BenchmarkResult",
    "serialize",
    "deserialize",
    "save_result",
    "load_result",
    "clear_env",
    "Path",
    "numerize",
    "log",
    "temp_log",
    "indent_log"
)

TIMER = time.perf_counter_ns
BenchmarkFunc = Callable[[int, Callable[[], int]], int]
AUTO_NUMBER_TARGET_TIME = 0.5e9
# AUTO_NUMBER_TARGET_TIME = 0.005e9

class Subject:
    """
    Define a benchmark subject. (e.g. spatium, Numpy, ...)
    This is a function decorator,
    the decorated function will become the common setup procedure of this subject.
    (e.g. `from spatium import Vec3`)
    """
    instances: list["Subject"] = []
    get_instance = classmethod(_instance_from_id)

    def __init__(self, name: str, *, color: str = None, identifier: str = None, sort: int = None):
        self.setup: SourceLines = None
        self.id: str = identifier
        self.name = name
        self.color = color
        self.sort = sort if sort is not None else len(Subject.instances)
        Subject.instances.append(self)

    def __call__(self, setup: FunctionType) -> Self:
        self.id = setup.__name__
        self.setup = extract_and_validate_source(
            setup,
            f"<Subject {self.id} setup routine>"
        )
        return self

    def __repr__(self):
        return f"<Subject {self.id}>"

    def to_json(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "setup": self.setup,
            "sort": self.sort
        }

    @classmethod
    def from_json(cls, data: Dict) -> Self:
        inst = cls(
            name=data["name"],
            color=data["color"],
            identifier=data["id"],
            sort=data["sort"]
        )
        inst.setup = tuple(data["setup"])
        return inst

class Benchmark:
    """
    Represents a benchmark, can have multiple test cases for multiple subject.
    Best be instantiated in a class as a class property, so that id can be automatically assigned.
    """
    instances: list["Benchmark"] = []
    get_instance = classmethod(_instance_from_id)

    def __init__(self, name: str, identifier: str = None):
        self.name = name
        self.id: str = identifier
        self.testcases: dict[Subject, TestCase] = {}

        if self.id is None:
            # infer id from call site
            import re
            line = inspect.stack()[1].code_context[0]
            pattern = r"\s*(?P<name>\w+)\s*=\s*Benchmark\s*\("
            mat = re.match(pattern, line)
            if mat is not None:
                self.id = mat.group("name")
            else:
                raise SyntaxError(f"Benchmark id infer failed: only instantiation source line matching the regex \"{pattern}\" supports inferring.")

        Benchmark.instances.append(self)

    def __set_name__(self, owner, name):
        self.id = name

    def _check(self):
        assert self.id is not None, f"Benchmark '{self.name}' was not assigned an id!"

    def _get_or_create_case(self, subject: Subject) -> "TestCase":
        if subject not in self.testcases:
            self.testcases[subject] = TestCase(self, subject)
        return self.testcases[subject]

    def setup(self, subject: Subject) -> Callable[[FunctionType], None]:
        """Function decorator. Set the setup routine of a test case."""
        self._check()
        def inner(func: FunctionType):
            case = self._get_or_create_case(subject)
            case.setup_src = extract_source(func)
            case.update()
        return inner

    @overload
    def __call__(self, func: FunctionType) -> Subject:
        """
        Decorate a function to add a test case.
        The function name needs to match the id of a subject.
        Specifically, if the function name is "_all_",
        test cases will be added for all subjects that have been instantiated before.
        :return: The subject

        The setup routine must be set first if needed!
        """
    @overload
    def __call__(self, *subjects: Subject, number: int = None) -> Callable[[FunctionType], None]:
        """
        Decorate a function to add test cases for multiple subjects.
        The decorator returns None.

        The setup routine must be set first if needed!
        """

    def __call__(self, *args, **kwargs):
        self._check()
        assert args, "No arguments."
        func = None
        number = kwargs.get("number", None)
        if isinstance(args[0], Subject):
            subjects = args
        elif isinstance(args[0], FunctionType):
            func = args[0]
            assert len(args) == 1, "Invalid arguments."
            if func.__name__ == "_all_":
                subjects = tuple(Subject.instances)
            else:
                subjects = (Subject.get_instance(func.__name__),)
                assert subjects[0] is not None, f"No subject with id {func.__name__}."
        else:
            raise TypeError

        def inner(i_func: FunctionType):
            # is "@benchmark_name()" (not "@benchmark_name")
            if func is None:
                if not all(c == "_" for c in i_func.__name__):
                    raise NameError("Function name must only consist of underscores "
                                    "if subjects are specified via arguments.")

            for subject in subjects:
                case = self._get_or_create_case(subject)
                case.main_src = extract_source(i_func)
                case.number = number
                case.is_auto_number = number is None
                case.update()
            return None

        if func is not None:
            inner(func)
            return subjects[0]
        return inner

    def run(self, order_permutations: bool = False, min_runs_per_case: int = 100) -> list["TestCaseResult"]:
        log(f"Benchmark - {self.id}:")
        with indent_log():
            all_results = []
            results_by_subject = {s:[] for s in self.testcases.keys()}
            permutations: Sequence[Sequence[TestCase]]
            if order_permutations:
                # noinspection PyTypeChecker
                permutations = tuple(itertools.permutations(self.testcases.values()))
                if order_permutations:
                    log(f"Order permutations: {len(permutations)}")
            else:
                # noinspection PyTypeChecker
                permutations = (tuple(self.testcases.values()),)
            repeats = math.ceil(min_runs_per_case / len(permutations))
            log(f"Total runs: {len(permutations) * repeats}")

            # Auto number
            if any(case.is_auto_number for case in self.testcases.values()):
                log("Auto Number:")
                with indent_log():
                    for case in self.testcases.values():
                        if not case.is_auto_number:
                            continue
                        log(f"{case.subject.id}: ", False)
                        with temp_log():
                            runtime = case.auto_number()
                        log(f"{numerize(case.number)} ({runtime / 1e9 :.3f}s)", False)
                        log()

            # Test cases
            log("Run: ", False)
            begin = time.perf_counter()
            with temp_log(), indent_log():
                for i, cases in enumerate(permutations):
                    with temp_log():
                        log(f"Sequence[{i+1}/{len(permutations)}]: ", False)
                        with NoGC:
                            for _ in range(repeats):
                                for case in cases:
                                    result = case.run()
                                    result.sequence = cases
                                    all_results.append(result)
                                    results_by_subject[case.subject].append(result)
            log(f"completed in {time.perf_counter() - begin:.1f}s")

            log("Results:")
            with indent_log():
                for subject, results in results_by_subject.items():
                    times = tuple(r.runtime for r in results)
                    log(f"{subject.id}({len(results)} runs): "
                        f"Min {min(times)/1e9:.3f}s, "
                        f"Avg {sum(times)/len(times)/1e9:.3f}s, "
                        f"Max {max(times)/1e9:.3f}s")

        log()

        return all_results

    def __repr__(self):
        return f"<Benchmark {self.id}>"

    def to_json(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "testcases": tuple(c.to_json() for c in self.testcases.values())
        }

    @classmethod
    def from_json(cls, data: Dict) -> Self:
        inst = cls(
            name=data["name"],
            identifier=data["id"]
        )
        for case_dat in data["testcases"]:
            case = TestCase.from_json(case_dat)
            inst.testcases[case.subject] = case
        return inst


class TestCase:
    def __init__(self, benchmark: Benchmark, subject: Subject):
        self.benchmark = benchmark
        self.subject = subject
        self.setup_src: SourceLines = ()
        self.main_src: Optional[SourceLines] = None
        self.benchmark_func: Optional[BenchmarkFunc] = None
        self.is_auto_number = True
        self.number: Optional[int] = None

    def _generate_benchmark_func(self):
        src = ["def _benchmark(_number: int, _timer) -> float:"]
        src.extend(self.subject.setup)
        src.extend(self.setup_src)
        src.extend((
            "from itertools import repeat as _repeat",
            "_it = _repeat(None, _number)",
            "_begin = _timer()",
            "for _i in _it:",
        ))
        src.extend(indent(self.main_src))
        src.extend((
            "return _timer() - _begin",
        ))
        src[1:] = indent(tuple(src[1:]))

        try:
            ls = {}
            exec(compile_src(src, f"<Test case {self.subject.name} {self.benchmark.name}>"), {}, ls)
            self.benchmark_func = ls["_benchmark"]
        except Exception as e:
            raise RuntimeError("Benchmark function generation failed.") from e

        try:
            self.benchmark_func(1, time.perf_counter_ns)
        except Exception as e:
            raise RuntimeError("Benchmark function validation failed.") from e

    def update(self):
        name = f"<Test case {self.subject.name} {self.benchmark.name} %s routine>"
        if self.main_src is not None:
            validate_source(
                self.subject.setup + self.setup_src + self.main_src,
                name % "full"
            )
            self._generate_benchmark_func()
        else:
            validate_source(
                self.subject.setup + self.setup_src,
                name % "setup"
            )

    def auto_number(self) -> int:
        assert self.is_auto_number
        for expo in itertools.count(3):
            for n in (1, 2, 5):
                self.number = n * 10**expo
                runtime = self.run().runtime
                if runtime > AUTO_NUMBER_TARGET_TIME:
                    return runtime

    def run(self) -> "TestCaseResult":
        log(".", False)
        assert self.benchmark_func is not None, "Benchmark function not generated."
        assert self.number is not None, "Number of runs not set."
        datetime = utc_now()
        with NoGC:
            return TestCaseResult(self, self.benchmark_func(self.number, TIMER), datetime)

    def __repr__(self):
        return f"<TestCase of {self.subject.id} in {self.benchmark.id}>"

    def to_json(self, id_only=False) -> Dict:
        data = {
            "benchmark_id": self.benchmark.id,
            "subject_id": self.subject.id
        }
        if not id_only:
            data.update({
                "setup_src": self.setup_src,
                "main_src": self.main_src,
                "is_auto_number": self.is_auto_number,
                "number": self.number
            })
        return data

    @classmethod
    def from_json(cls, data: Dict, *, data_only=True, id_only=False) -> Self:
        """
        :param data_only: if the update() method (validate & compile source) should not be run
        """
        benchmark = Benchmark.get_instance(data["benchmark_id"])
        subject = Subject.get_instance(data["subject_id"])
        if id_only:
            return benchmark.testcases[subject]
        else:
            assert subject not in benchmark.testcases, f"TestCase of subject {subject} already exists in benchmark {benchmark}."
            inst = cls(benchmark, subject)
            inst.setup_src = tuple(data["setup_src"])
            inst.main_src = tuple(data["main_src"])
            inst.is_auto_number = data["is_auto_number"]
            inst.number = data["number"]
            if not data_only:
                inst.update()
        return inst


class TestCaseResult:
    def __init__(self, testcase: TestCase, runtime: int, datetime: DateTime, sequence: Sequence[TestCase] = None):
        self.testcase = testcase
        self.runtime = runtime
        self.datetime = datetime
        self.sequence = sequence

    def __repr__(self):
        return f"<TestCaseResult of {self.testcase}>"

    def to_json(self) -> Dict:
        return {
            **self.testcase.to_json(id_only=True),
            "runtime": self.runtime,
            "timestamp": self.datetime.timestamp(),
            "sequence": ([case.to_json(id_only=True) for case in self.sequence]
                         if self.sequence is not None else None)
        }

    @classmethod
    def from_json(cls, data: Dict) -> Self:
        return cls(
            testcase=TestCase.from_json(data, id_only=True),
            runtime=data["runtime"],
            datetime=from_utc_stamp(data["timestamp"]),
            sequence=(tuple(TestCase.from_json(d, id_only=True) for d in data["sequence"])
                      if data["sequence"] is not None else None)
        )

class BenchmarkMetadata:
    def __init__(self):
        log("Getting metadata...")
        with indent_log():
            import platform, cpuinfo, os
            self.system = platform.system()
            log(f"System: {self.system}")
            self.ci = CI
            log(f"CI: {self.ci}")
            try:
                cpu = cpuinfo.get_cpu_info()
                self.arch = cpu["arch"]
                log(f"Arch: {self.arch}")
                self.cpu = cpu["brand_raw"]
                log(f"CPU: {self.cpu}")
            except Exception as e:
                log(f"Failed to get accurate CPU info: {e}")
                self.arch = platform.machine()
                log(f"Arch: {self.arch}")
                self.cpu = platform.processor()
                log(f"CPU: {self.cpu}")

            self.py_impl = platform.python_implementation()
            self.py_ver = platform.python_version()
            log(f"Python: {self.py_impl} {self.py_ver}")
        log()

    def to_json(self) -> Dict:
        return {
            "system": self.system,
            "ci": self.ci,
            "arch": self.arch,
            "cpu": self.cpu,
            "py_impl": self.py_impl,
            "py_ver": self.py_ver
        }

    @classmethod
    def from_json(cls, data: Dict) -> Self:
        inst = cls.__new__(cls)
        inst.system = data["system"]
        inst.ci = data["ci"]
        inst.arch = data["arch"]
        inst.cpu = data["cpu"]
        inst.py_impl = data["py_impl"]
        inst.py_ver = data["py_ver"]
        return inst

class BenchmarkResult:
    def __init__(self, datetime: DateTime, metadata: BenchmarkMetadata = None):
        self.datetime = datetime
        self.metadata = metadata or BenchmarkMetadata()
        self.raw_results: list[TestCaseResult] = []

    def add_results(self, *results: TestCaseResult):
        self.raw_results.extend(results)

    @property
    def benchmarks(self) -> Iterable[Benchmark]:
        return iter_identity(r.testcase.benchmark for r in self.raw_results)

    def get_results(self, *, testcase: TestCase = None, subject: Subject = None) -> Generator[TestCaseResult, None, None]:
        for result in self.raw_results:
            if testcase is not None and result.testcase != testcase:
                continue
            if subject is not None and result.testcase.subject != subject:
                continue
            yield result

    def to_json(self) -> Dict:
        return {
            "timestamp": self.datetime.timestamp(),
            "metadata": self.metadata.to_json(),
            "raw_results": tuple(r.to_json() for r in self.raw_results)
        }

    @classmethod
    def from_json(cls, data: Dict) -> Self:
        inst = cls(
            datetime=from_utc_stamp(data["timestamp"]),
            metadata=BenchmarkMetadata.from_json(data["metadata"])
        )
        inst.add_results(*(TestCaseResult.from_json(rd) for rd in data["raw_results"]))
        return inst


def run_benchmarks(*benchmarks: Benchmark, **kwargs) -> BenchmarkResult:
    begin = time.perf_counter()
    try:
        if not benchmarks:
            benchmarks = tuple(Benchmark.instances)

        result = BenchmarkResult(utc_now())
        for benchmark in benchmarks:
            result.add_results(*benchmark.run(**kwargs))
    except KeyboardInterrupt:
        log()
        log("Terminated", color="red")
        exit(0)

    log(f"All completed in {time.perf_counter() - begin:.1f}s")

    return result


def serialize(result: BenchmarkResult) -> Dict:
    return {
        "subjects": tuple(s.to_json() for s in Subject.instances),
        "benchmarks": tuple(b.to_json() for b in Benchmark.instances),
        "result": result.to_json()
    }

def deserialize(data: Dict) -> BenchmarkResult:
    assert not Benchmark.instances or not Subject.instances, "Deserialization prohibited: environment not clean."

    for d in data["subjects"]:
        Subject.from_json(d)
    for d in data["benchmarks"]:
        Benchmark.from_json(d)
    return BenchmarkResult.from_json(data["result"])

def clear_env():
    Benchmark.instances.clear()
    Subject.instances.clear()

def save_result(result: BenchmarkResult, file: Path):
    """Save the result and the current environment to a json file."""
    log(f"Saving to {file}...")
    with file.open("w", encoding="utf8") as f:
        json.dump(serialize(result), f, indent=4, ensure_ascii=False)

def load_result(file: Path) -> BenchmarkResult:
    """Restore the result and the environment from a json file."""
    log(f"Loading from {file}...")
    with file.open("r", encoding="utf8") as f:
        result = deserialize(json.load(f))
        return result
