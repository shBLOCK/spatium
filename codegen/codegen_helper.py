import traceback

import regex
from typing import Any, Self, Sequence
from types import UnionType
import time


def from_template(template: str, params: dict[str, Any] = None, _globals=None) -> str:
    def apply_params(in_line: str) -> str:
        if params is not None:
            for k, v in params.items():
                in_line = in_line.replace(f"_{k}_", str(v))
        return in_line

    out = ""
    began = False
    ignore_next = False
    if_depth = 0
    skip_if_depth = 0
    keep_if_clause = False
    for line in template.splitlines(keepends=False):
        if ignore_next:
            ignore_next = False
            continue

        # Apply params
        line = apply_params(line)

        # If/Else
        if "<ENDIF>" in line:
            if if_depth == skip_if_depth:
                skip_if_depth = 0
            if_depth -= 1
            if keep_if_clause:
                out += f"{line}\n"
                keep_if_clause = False
            assert if_depth >= 0, if_depth
            continue
        if mat := regex.search(r"<IF>:\s*(?P<statement>.*)", line):
            if_depth += 1
            stat = mat.group("statement")
            try:
                result = bool(eval(stat))
            except Exception as e:
                out += f"{line} #<ERR>: {e}\n"
                keep_if_clause = True
                continue
            else:
                if not result:
                    skip_if_depth = if_depth
                continue
        if keep_if_clause:
            out += f"{line}\n"
            continue
        if skip_if_depth > 0:
            continue

        # Begin/End
        if "<TEMPLATE_BEGIN>" in line:
            began = True
            continue
        if not began:
            continue
        if "<TEMPLATE_END>" in line:
            break

        # Ignore
        if "<IGNORE>" in line:
            continue
        if "<IGNORE_NEXT>" in line:
            ignore_next = True
            continue

        # Handle empty line
        if line == "":
            out += "\n"
            continue

        out += line + "\n"

    generated = True
    while generated:
        last_out = out
        out = ""
        generated = False
        for line in last_out.splitlines(keepends=False):
            # Lines generation
            if "<GEN>:" in line:
                gen_pos = line.index("#<GEN>:")
                prefix = line[:gen_pos]
                expr = line[gen_pos + 7 :]
                try:
                    result = eval(
                        expr,
                        (
                            globals()
                            if _globals is None
                            else globals().copy().update(_globals)
                        ),
                    )
                    generated = True
                except Exception as e:
                    if isinstance(e, AssertionError):
                        traceback.print_exception(e)
                        raise e
                    out += f"{line} #<ERR>: {e}\n"
                else:
                    for gen_line in str(result).splitlines(keepends=False):
                        out += prefix
                        out += apply_params(gen_line)
                        out += "\n"
            else:
                out += f"{line}\n"

    return out


class _Func:
    def __init__(self, name: str, c_params: tuple[str], c_ret: str):
        self.name = name
        self.c_params = c_params
        self.c_ret = c_ret

        self.params = []
        for p in c_params:
            match p:
                case "float" | "double" | "py_float":
                    self.params.append(float | int)
                case "int" | "long" | "py_int":
                    self.params.append(int)
                case "self":
                    self.params.append(Self)
                case _:
                    self.params.append(p)
        self.params = tuple(self.params)

        match c_ret:
            case None | "" | "void":
                self.ret = None
            case "float" | "double" | "py_float":
                self.ret = float
            case "int" | "long" | "py_int":
                self.ret = int
            case _:
                self.ret = c_ret


class _Overload:
    def __init__(self, name: str):
        self.name = name
        self._funcs: list[_Func] = []
        self._possible_param_types_cache = None

    def add(self, func: _Func):
        if len(self._funcs) > 0:
            assert (Self in self._funcs[0].params) == (
                Self in func.params
            ), "function/method mismatch"
        self._funcs.append(func)
        self._possible_param_types_cache = None

    def __len__(self):
        return len(self._funcs)

    def __getitem__(self, item: int):
        return self._funcs[item]

    @property
    def max_params(self) -> int:
        return max(len(f.params) for f in self._funcs)

    @property
    def min_params(self) -> int:
        return min(len(f.params) for f in self._funcs)

    @property
    def possible_param_types(self) -> Sequence[Sequence]:
        if self._possible_param_types_cache is not None:
            return self._possible_param_types_cache

        self._possible_param_types_cache = [[] for _ in range(self.max_params)]
        for f in self._funcs:
            for i, param in enumerate(f.params):
                if isinstance(param, UnionType):
                    ps = param.__args__
                else:
                    ps = (param,)
                for p in ps:
                    if p not in self._possible_param_types_cache[i]:
                        self._possible_param_types_cache[i].append(p)

        for optional_param in self._possible_param_types_cache[self.min_params :]:
            optional_param.append(None)

        self._possible_param_types_cache = tuple(
            tuple(ts) for ts in self._possible_param_types_cache
        )

        return self._possible_param_types_cache

    @property
    def is_method(self) -> bool:
        assert len(self._funcs) > 0
        return self._funcs[0].params[0] is Self

    @property
    def param_names(self) -> tuple[str]:
        ps = []
        if self.is_method:
            ps.append("self")
        for i in range(self.max_params - 1 if self.is_method else self.max_params):
            ps.append(f"p{i}")
        return tuple(ps)

    @staticmethod
    def _type_check_expression(*types):
        if float in types and int in types:  # py_float
            assert len(types) == 2, "py_float type should be a discrete branch!"
            # Insignificant optimization
            # return "(PyFloat_CheckExact({value}) or PyLong_CheckExact({value}))"
            return "(PyFloat_Check({value}) or PyLong_Check({value}))"
        elif int in types:  # py_int
            assert len(types) == 1, "py_int type should be a discrete branch!"
            # Insignificant optimization
            # return "PyLong_CheckExact({value})"
            return "PyLong_Check({value})"
        else:
            out = ""
            for i, t in enumerate(types):
                if type(t) is str:
                    out += f"isinstance({{value}}, {t})"
                elif t is None:
                    out += "{value} is None"
                elif t is Self:
                    assert False
                elif isinstance(t, type):
                    out += f"isinstance({{value}}, {t.__name__})"
                else:
                    assert False

                if i != len(types) - 1:
                    out += " or "
            return out

    @staticmethod
    def _type_str(t):
        if type(t) is str:
            return t
        if t is Self:
            return "self"
        if t is None:
            return "None"
        if isinstance(t, type):
            return t.__name__
        assert False

    def _func_from_params(self, params: Sequence) -> Sequence[_Func]:
        match_funcs = []
        for func in self._funcs:
            for i, param in enumerate(params):
                if len(func.params) <= i:
                    if param is not None:
                        break
                elif isinstance(func.params[i], UnionType):
                    if all(fp != param for fp in func.params[i].__args__):
                        break
                else:
                    if param != func.params[i]:
                        break
            else:
                match_funcs.append(func)

        return match_funcs

    def _gen_type_no_match_exception(self, param_types: tuple[tuple]) -> str:
        type_strs = []
        for pts in param_types:
            if len(pts) == 1:
                type_strs.append(self._type_str(pts[0]))
            else:
                type_strs.append(f"({' | '.join(map(self._type_str, pts))})")
        text = (
            f'raise TypeError("No matching overload function for parameter types: '
            f"{', '.join(type_strs)}"
        )
        if len(param_types) != self.max_params:
            text += ", ..."
        text += '")'
        return text

    def _gen_type_cast(self, var_name: str, var_types: tuple):
        multiple_type_err = "A branch should have only one general(cast-able) type!"
        if float in var_types and int in var_types:  # py_float
            assert len(var_types) == 2, multiple_type_err
            # Insignificant optimization
            # return f"PyFloat_AS_DOUBLE({var_name}) if PyFloat_CheckExact({var_name}) else PyLong_AsDouble({var_name})"
            return f"PyFloat_AsDouble({var_name})"
        elif int in var_types:  # py_int
            assert len(var_types) == 1, multiple_type_err
            return f"PyLong_AsLongLong({var_name})"
        else:
            assert len(var_types) == 1, multiple_type_err
            assert isinstance(
                var_types[0], str
            ), f"Don't know how to cast to {var_types[0]}."
            return f"<{var_types[0]}> {var_name}"

    def _gen_dispatch_tree(
        self, params_types: tuple = None
    ) -> tuple[Sequence[str], bool]:
        """Generate overload dispatch tree recursively."""
        if params_types is None:
            params_types = ((Self,),) if self._funcs[0].params[0] is Self else ()
        params_first_types = tuple(ps[0] for ps in params_types)

        if len(params_types) == self.max_params:
            funcs = self._func_from_params(params_first_types)
            if len(funcs) == 0:
                return [self._gen_type_no_match_exception(params_types)], False
            if len(funcs) > 1:
                assert (
                    False
                ), f"Multiple matching functions for: {', '.join(str(p) for p in params_first_types)}"
            func = funcs[0]

            out = [
                f"{'self.' if self.is_method else ''}"
                f"{func.name}"
                f"({', '.join(self._gen_type_cast(pn, pts) for pts,pn in zip(params_types, self.param_names) if pn != 'self' and None not in pts)})"
            ]
            if func.ret is None:
                out.append("return")
            else:
                out[0] = f"return {out[0]}"
            return out, True
        else:
            if len(self._func_from_params(params_first_types)) == 0:
                return self._gen_type_no_match_exception(params_types), False

            out = []
            possible_types = self.possible_param_types[len(params_types)]
            # Merge branches with the same endpoint
            branches = []
            for t in possible_types:
                matches = self._func_from_params(params_first_types + (t,))
                if len(matches) == 0:
                    continue
                for branch in branches:
                    if set(matches) == set(
                        self._func_from_params(params_first_types + (branch[0],))
                    ):
                        branch.append(t)
                        break
                else:
                    branches.append([t])

            # Prioritize py_float and py_int branches
            branches.sort(key=lambda ts: 0 if int in ts or float in ts else 1)

            any_hit = False
            for i, t in enumerate(branches):
                out.append(
                    f"{'if' if i == 0 else 'elif'} "
                    f"{self._type_check_expression(*t).format(value=self.param_names[len(params_types)])}:"
                )
                branch_params = params_types + (t,)
                dt, hit = self._gen_dispatch_tree(branch_params)
                if hit:
                    any_hit = True
                if hit:
                    for l in dt:
                        out.append(f"    {l}")
                else:
                    out.append(
                        "    " + self._gen_type_no_match_exception(branch_params)
                    )
            out.append("else:")
            expected_type_strs = [self._type_str(t) for t in possible_types]
            expected_types_str = " | ".join(expected_type_strs)
            out.append(
                f'    raise TypeError(f"The {len(params_first_types) + 1}th parameter expected {expected_types_str}, '
                f'got {{{self.param_names[len(params_first_types)]}}}")'
            )

            return out, any_hit

    def gen_dispatcher(self) -> Sequence[str]:
        params = self.param_names
        param_strs = []
        for i, param in enumerate(params):
            if param == "self":
                param_strs.append(param)
            else:
                if None in self.possible_param_types[i]:
                    param_strs.append(f"{param}=None")
                else:
                    param_strs.append(param)

        ret_types = list(set(_Overload._type_str(f.ret) for f in self._funcs))

        lines = [
            f"def {self.name}({', '.join(('object ' if i > 0 else '') + p for i,p in enumerate(param_strs))}, /) -> {' | '.join(ret_types)}:"
        ]
        disp_lines, _ = self._gen_dispatch_tree()
        lines += [f"    {dl}" for dl in disp_lines]
        return lines


def process_overloads(file: str) -> str:
    import regex

    overloads = {}

    lines = file.splitlines(keepends=False)

    is_overload_func = False
    for i, line in enumerate(lines):
        if "<OVERLOAD>" in line:
            assert not is_overload_func
            is_overload_func = True
            continue
        if is_overload_func:
            is_overload_func = False
            m = regex.search(
                r"cdef\s+"
                r"(?:inline\s+)?"
                r"(?P<return>\w+)?\s+"
                r"(?P<name>\w+)\s*"
                r"\("
                r"\s*(?:(?P<params>\w+\s+\w+|self)(?:\s*,\s*(?P<params>\w+\s+\w+))*)?\s*"
                r"\)",
                line,
            )
            assert m is not None, line
            name = m.group("name")
            c_ret = m.group("return")
            c_params = tuple(m.captures("params"))
            c_params = tuple(regex.match(r"\w+", p).group() for p in c_params)
            if name not in overloads:
                overloads[name] = _Overload(name)
            overload = overloads[name]
            new_name = f"_{name}_{len(overload):d}"
            name_span = m.span("name")
            lines[i] = line[: name_span[0]] + new_name + line[name_span[1] :]
            overload.add(_Func(new_name, c_params, c_ret))

    lines = [line for line in lines if "<OVERLOAD>" not in line]

    while True:
        for i, line in enumerate(lines):
            if "<OVERLOAD_DISPATCHER>:" in line:
                m = regex.match(
                    r"(?P<prefix>\s*)#(?:\s|#)*<OVERLOAD_DISPATCHER>:(?P<name>\w+)",
                    line,
                )
                assert m is not None
                prefix = m.group("prefix")
                name = m.group("name")
                assert name in overloads
                disp_lines = overloads[name].gen_dispatcher()
                disp_lines = [prefix + disp_line for disp_line in disp_lines]
                lines[i : i + 1] = disp_lines
                break
        else:
            break

    return "".join(f"{line}\n" for line in lines)


def step_generate(
    template_file: str,
    output_file: str = None,
    write_file: bool = False,
    params: dict = None,
    _globals: dict = None,
    overload: bool = False,
):
    print(f"Step Generate: {template_file}")

    if output_file is None:
        output_file = template_file

    import os

    if not os.path.exists("output"):
        os.mkdir("output")

    template = open(f"templates/{template_file}", encoding="utf8").read()
    t = time.perf_counter()
    if _globals is not None:
        old_globals = globals().copy()
        globals().update(_globals)
    result = from_template(template, params)
    if _globals is not None:
        globals().clear()
        # noinspection PyUnboundLocalVariable
        globals().update(old_globals)
    for i, line in enumerate(result.splitlines(keepends=False)):
        if "<ERR>" in line:
            raise Exception(f"Unresolved generation error in line {i+1}: {line}")
    if overload:
        result = process_overloads(result)
    print(f"Step Generate: {template_file} completed in {time.perf_counter() - t:.3f}s")
    if write_file:
        with open(f"output/{output_file}", "w", encoding="utf8") as output:
            output.write(result)
    else:
        return result


def step_gen_stub(source_file: str, output_file: str):
    import stub_generator

    source = open(f"output/{source_file}", encoding="utf8").read()
    t = time.perf_counter()
    result = stub_generator.gen_stub(source)
    print(
        f"Step Gen Stub: {source_file} -> {output_file} completed in {time.perf_counter() - t:.3f}s"
    )
    with open(f"output/{output_file}", "w", encoding="utf8") as output:
        output.write(result)


def step_cythonize(file: str):
    import sys
    import subprocess

    print("########## Cythonize ##########")
    proc = subprocess.Popen(
        ("cythonize.exe", "-a", "-i", f"output/{file}.pyx"),
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    t = time.perf_counter()
    proc.wait()
    print(
        f"Cythonize finished in {time.perf_counter() - t}s with exit code {proc.returncode}",
        file=sys.stdout if proc.returncode == 0 else sys.stderr,
    )


def step_move_to_dest(final_dest: str, file_prefix: str, file_suffix: str):
    import os
    import shutil

    for file in os.listdir("output"):
        if file.startswith(file_prefix) and file.endswith(file_suffix):
            path = os.path.join("output", file)
            dest = os.path.join(final_dest, file)
            shutil.copy(path, dest)
            print(f"Coping {file} to {dest}")
