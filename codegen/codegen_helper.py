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
                expr = line[gen_pos + 7:]
                try:
                    result = eval(expr, globals() if _globals is None else globals().copy().update(_globals))
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
                case "float" | "double":
                    self.params.append(float | int)
                case "int" | "long":
                    self.params.append(int)
                case "self":
                    self.params.append(Self)
                case _:
                    self.params.append(p)
        self.params = tuple(self.params)

        match c_ret:
            case None | "" | "void":
                self.ret = None
            case _:
                self.ret = c_ret

class _Overload:
    def __init__(self, name: str):
        self.name = name
        self._funcs: list[_Func] = []
        self._possible_param_types_cache = None

    def add(self, func: _Func):
        if len(self._funcs) > 0:
            assert (Self in self._funcs[0].params) == (Self in func.params), \
                "function/method mismatch"
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

        for optional_param in self._possible_param_types_cache[self.min_params:]:
            optional_param.append(None)

        self._possible_param_types_cache = tuple(tuple(ts) for ts in self._possible_param_types_cache)

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
    def _type_check_expression(t):
        if type(t) is str:
            return f"isinstance({{}}, {t})"
        if t is None:
            return "{} is None"
        if t is Self:
            assert False
        if isinstance(t, type):
            return f"isinstance({{}}, {t.__name__})"
        assert False

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

    def _func_from_params(self, params: Sequence) -> _Func | None:
        assert len(params) == self.max_params
        match_func = None
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
                assert match_func is None, f"Multiple matching functions for: {', '.join(str(p) for p in params)}"
                match_func = func

        return match_func

    def _gen_dispatch_tree(self, params: tuple = None) -> Sequence[str]:
        if params is None:
            params = (Self,) if self._funcs[0].params[0] is Self else ()
        if len(params) == self.max_params:
            func = self._func_from_params(params)
            if func is None:
                return [f"raise TypeError(\"No matching overload function for parameter types: "
                        f"{', '.join(self._type_str(pt) for pt in params)}\")"]

            out = [f"{'self.' if self.is_method else ''}"
                   f"{func.name}"
                   f"({', '.join(pn for pt,pn in zip(params, self.param_names) if pn != 'self' and pt is not None)})"]
            if func.ret is None:
                out.append("return")
            else:
                out[0] = f"return {out[0]}"
            return out
        else:
            out = []
            possible_types = self.possible_param_types[len(params)]
            for i, t in enumerate(possible_types):

                out.append(f"{'if' if i == 0 else 'elif'} "
                           f"{self._type_check_expression(t).format(self.param_names[len(params)])}:")
                dt = self._gen_dispatch_tree(params + (t,))
                for l in dt:
                    out.append(f"    {l}")
            out.append("else:")
            expected_type_strs = [self._type_str(t) for t in possible_types]
            expected_types_str = " | ".join(expected_type_strs)
            out.append(f"    raise TypeError(f\"The {len(params) + 1}th parameter expected {expected_types_str}, "
                       f"got {{{self.param_names[len(params)]}}}\")")

            return out

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

        lines = [f"def {self.name}({', '.join(param_strs)}, /):"]
        disp_lines = self._gen_dispatch_tree()
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
                r"cdef\s*"
                r"(?P<return>\w+)?\s+"
                r"(?P<name>\w+)\s*"
                r"\("
                r"\s*(?:(?P<first_param>\w+\s+\w+|self)(?:\s*,\s*(?P<remaining_params>\w+\s+\w+))*)?\s*"
                r"\)",
                line
            )
            assert m is not None
            name = m.group("name")
            c_ret = m.group("return")
            c_params = (*m.captures("first_param"), *m.captures("remaining_params"))
            c_params = tuple(regex.match(r"\w+", p).group() for p in c_params)
            if name not in overloads:
                overloads[name] = _Overload(name)
            overload = overloads[name]
            new_name = f"_{name}_{len(overload):d}"
            name_span = m.span("name")
            lines[i] = line[:name_span[0]] + new_name + line[name_span[1]:]
            overload.add(_Func(new_name, c_params, c_ret))

    lines = [line for line in lines if "<OVERLOAD>" not in line]

    while True:
        for i, line in enumerate(lines):
            if "<OVERLOAD_DISPATCHER>:" in line:
                m = regex.match(r"(?P<prefix>\s*)#(?:\s|#)*<OVERLOAD_DISPATCHER>:(?P<name>\w+)", line)
                assert m is not None
                prefix = m.group("prefix")
                name = m.group("name")
                assert name in overloads
                disp_lines = overloads[name].gen_dispatcher()
                disp_lines = [prefix + disp_line for disp_line in disp_lines]
                lines[i:i + 1] = disp_lines
                break
        else:
            break

    return "".join(f"{line}\n" for line in lines)


def step_generate(template_file: str, output_file: str, params: dict = None, _globals: dict = None):
    print("########## Generate ##########")

    import os
    if not os.path.exists("output"):
        os.mkdir("output")

    with open(f"output/{output_file}", "w") as output:
        template = open(f"templates/{template_file}").read()
        t = time.perf_counter()
        globals().update(_globals)
        result = from_template(template, params)
        for i, line in enumerate(result.splitlines(keepends=False)):
            if "<ERR>" in line:
                raise Exception(f"Unresolved generation error in line: {i+1}\n{line}")
        print(f"Generation completed in {time.perf_counter() - t:.3f}s")
        output.write(result)


def step_cythonize(file: str):
    import sys
    import subprocess

    print("########## Cythonize ##########")
    proc = subprocess.Popen((
        "cythonize.exe",
        "-a",
        "-i",
        f"output/{file}.pyx"
    ), stdout=sys.stdout, stderr=sys.stderr)
    t = time.perf_counter()
    proc.wait()
    print(
        f"Cythonize finished in {time.perf_counter() - t}s with exit code {proc.returncode}",
        file=sys.stdout if proc.returncode == 0 else sys.stderr
    )


def step_move_to_dest(final_dest: str, file_prefix: str, file_suffix: str):
    print("########## Move To Dest ##########")

    import os
    import shutil

    for file in os.listdir("output"):
        if file.startswith(file_prefix) and file.endswith(file_suffix):
            path = os.path.join("output", file)
            dest = os.path.join(final_dest, file)
            shutil.copy(path, dest)
            print(f"Coping {file} to {dest}")

