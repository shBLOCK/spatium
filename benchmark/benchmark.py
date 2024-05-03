import sys
import timeit
import enum
from collections import OrderedDict
from numerize.numerize import numerize

# Get rid of pygame import message
import pygame
print()

class Subject(enum.Enum):
    PurePython = "Pure Python", "tab:blue", "from pure_python_impl import Vec3"
    Pygame = "Pygame", "tab:green", "from pygame import Vector3"
    Numpy = "Numpy", "tab:orange", "import numpy as np; array = np.array"
    GdMath = "GdMath", "tab:purple", "from gdmath import Vec3"

    def __init__(self, label: str, color: str, setup: str):
        self.label = label
        self.color = color
        self.setup = setup


BASELINE = Subject.PurePython
RUNS_TO_GET_MIN_TIME = 30
STMT_BATCH_SIZE = 10000

class TestCase:
    def __init__(self, subject: Subject, setup: str, stmt: str, number = None):
        self.subject = subject
        self.setup = setup
        self.stmt = stmt
        self.number = number
        self._times = []

    @property
    def time(self) -> float:
        return min(self._times)

    @property
    def per_sec(self) -> float:
        return self.number / self.time

    @property
    def per_sec_text(self) -> str:
        return numerize(self.per_sec, 1)

    def run(self):
        self._times.append(timeit.timeit(
            stmt=(self.stmt+"\n") * STMT_BATCH_SIZE,
            setup=self.subject.setup + "\n" + self.setup,
            number=self.number // STMT_BATCH_SIZE
        ))

benchmarks: OrderedDict[str, tuple[TestCase]] = OrderedDict()

def benchmark(name: str, number: int, *cases: TestCase):
    print(f"##### {name} #####")
    for case in cases:
        case.number = case.number or number
    for _ in range(RUNS_TO_GET_MIN_TIME):
        for case in cases:
            case.run()
        print(".", end="")
    print("\b"*RUNS_TO_GET_MIN_TIME, end="")

    benchmarks[name] = cases
    for case in cases:
        print(f"{case.subject.name}: {numerize(case.number, 0)} in {case.time:.3f}s - {case.per_sec_text}/s")

    print()


def main():
    benchmark(
        "Instantiation",
        3_000_000,
        TestCase(Subject.PurePython, "", "Vec3(1.0, 2.0, 3.0)"),
        TestCase(Subject.Pygame, "", "Vector3(1.0, 2.0, 3.0)"),
        TestCase(Subject.Numpy, "tp = (1.0, 2.0, 3.0)", "array(tp)"),
        TestCase(Subject.GdMath, "", "Vec3(1.0, 2.0, 3.0)")
    )

    iab123_py = "a = Vec3(1, 2, 3); b = Vec3(3, 2, 1)"
    iab123_pg = "a = Vector3(1, 2, 3); b = Vector3(3, 2, 1)"
    iab123_np = "a = array((1.0, 2.0, 3.0)); b = array((3.0, 2.0, 1.0))"
    iab123_gd = "a = Vec3(1, 2, 3); b = a.zyx"

    benchmark(
        "Copy",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "+a"),
        TestCase(Subject.Pygame, iab123_pg, "a.copy()"),
        TestCase(Subject.Numpy, iab123_np, "a.copy()"),
        TestCase(Subject.GdMath, iab123_gd, "+a")
    )

    benchmark(
        "Addition",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "a + b"),
        TestCase(Subject.Pygame, iab123_pg, "a + b"),
        TestCase(Subject.Numpy, iab123_np, "a + b"),
        TestCase(Subject.GdMath, iab123_gd, "a + b")
    )

    benchmark(
        "Inplace Addition",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "a += b"),
        TestCase(Subject.Pygame, iab123_pg, "a += b"),
        TestCase(Subject.Numpy, iab123_np, "a += b"),
        TestCase(Subject.GdMath, iab123_gd, "a += b")
    )

    benchmark(
        "Dot Product",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "a @ b"),
        TestCase(Subject.Pygame, iab123_pg, "a.dot(b)"),
        TestCase(Subject.Numpy, iab123_np, "a.dot(b)"),
        TestCase(Subject.GdMath, iab123_gd, "a @ b")
    )

    benchmark(
        "Cross Product",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "a ^ b"),
        TestCase(Subject.Pygame, iab123_pg, "a.cross(b)"),
        TestCase(Subject.Numpy, iab123_np + "; cross = np.cross", "cross(a, b)", number=30_000),
        TestCase(Subject.GdMath, iab123_gd, "a ^ b")
    )

    benchmark(
        "Equality",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "a == b"),
        TestCase(Subject.Pygame, iab123_pg, "a == b"),
        TestCase(Subject.Numpy, iab123_np, "a == b"),
        TestCase(Subject.GdMath, iab123_gd, "a == b")
    )

    benchmark(
        "Iteration",
        2_000_000,
        TestCase(Subject.PurePython, iab123_py, "tuple(a)"),
        TestCase(Subject.Pygame, iab123_pg, "tuple(a)"),
        TestCase(Subject.Numpy, iab123_np, "tuple(a)"),
        TestCase(Subject.GdMath, iab123_gd, "tuple(a)")
    )

    benchmark(
        "Length",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "a.length"),
        TestCase(Subject.Pygame, iab123_pg, "a.length()"),
        TestCase(Subject.GdMath, iab123_gd, "a.length")
    )

    benchmark(
        "Normalize",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "a.normalized"),
        TestCase(Subject.Pygame, iab123_pg, "a.normalize()"),
        TestCase(Subject.Numpy, iab123_np + "; norm = np.linalg.norm", "norm(a)"),
        TestCase(Subject.GdMath, iab123_gd, "a.normalized")
    )

    benchmark(
        "Get Item",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "a[1]"),
        TestCase(Subject.Pygame, iab123_pg, "a[1]"),
        TestCase(Subject.Numpy, iab123_np, "a[1]"),
        TestCase(Subject.GdMath, iab123_gd, "a[1]")
    )

    benchmark(
        "Set Item",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "a[1] = 4"),
        TestCase(Subject.Pygame, iab123_pg, "a[1] = 4"),
        TestCase(Subject.Numpy, iab123_np, "a[1] = 4"),
        TestCase(Subject.GdMath, iab123_gd, "a[1] = 4")
    )

    benchmark(
        "Swizzle Get",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "a.zxy"),
        TestCase(Subject.Pygame, iab123_pg, "a.zxy"),
        TestCase(Subject.GdMath, iab123_gd, "a.zxy")
    )

    benchmark(
        "Swizzle Set",
        3_000_000,
        TestCase(Subject.PurePython, iab123_py, "a.zxy = b"),
        TestCase(Subject.Pygame, iab123_pg, "a.zxy = b"),
        TestCase(Subject.GdMath, iab123_gd, "a.zxy = b")
    )

    gen_plot()


def gen_plot():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(
        figsize=(12, 4),
        layout="constrained"
    )
    ax.set_title(f"Benchmark - {BASELINE.label} Implementation as Baseline\nOperations Per Second")
    ax.margins(x=0.02, y=0.2)

    ax.axhline(
        y=1,
        color=BASELINE.color,
        linestyle="--",
        label="Baseline"
    )

    x_ticks = []
    pos = 0
    for bm_name, cases in benchmarks.items():
        x_ticks.append((pos + (len(cases) - 1) / 2, bm_name))

        baseline = [c for c in cases if c.subject == BASELINE]
        assert len(baseline) == 1, "Baseline data not found or duplicate"
        baseline = baseline[0]

        for case in cases:
            rect = ax.bar(
                x = pos,
                height = case.per_sec / baseline.per_sec,
                width = 1,
                label = case.subject.label,
                color = case.subject.color
            )
            ax.bar_label(
                rect,
                padding=3,
                labels=[case.per_sec_text],
                fontsize=10,
                rotation=90
            )
            pos += 1

        pos += 1.5

    ax.set_xticks(*zip(*x_ticks), rotation=15)

    ax.yaxis.set_major_formatter(lambda x, pos: f"{x}x")

    handles, labels = plt.gca().get_legend_handles_labels()
    temp = {k: v for k, v in zip(labels, handles)}
    ax.legend(
        temp.values(), temp.keys(),
        loc="upper left"
    )

    plt.savefig("chart.png")
    import shutil
    shutil.copyfile("chart.png", "history_charts/")

    plt.show()


def prepare():
    import platform
    if platform.system() != "Windows":
        print("Warning: Not on windows, not doing benchmark prep!", file=sys.stderr)
        return

    import psutil
    proc = psutil.Process()
    print("Prep: Setting process priority to realtime class.")
    proc.nice(psutil.REALTIME_PRIORITY_CLASS)
    print("Prep: Setting CPU affinity to [1].")
    proc.cpu_affinity([1])
    import subprocess
    ps = "powershell -Command "
    cfg_proc = "powercfg -setacvalueindex scheme_current sub_processor "
    print("Prep: set powercfg")
    subprocess.run(ps + cfg_proc + "procthrottlemax 100", capture_output=True)
    subprocess.run(ps + cfg_proc + "procthrottlemin 100", capture_output=True)
    # subprocess.run(ps + cfg_proc + "idledisable 1", capture_output=True)
    subprocess.run(ps + "powercfg -setactive scheme_current", capture_output=True)

def cleanup():
    import subprocess
    print("Cleanup: reset powercfg")
    subprocess.run("powershell -Command powercfg -setacvalueindex scheme_current sub_processor idledisable 0", capture_output=True)
    subprocess.run("powershell -Command powercfg -setactive scheme_current", capture_output=True)


if __name__ == '__main__':
    try:
        prepare()
        main()
    finally:
        cleanup()
