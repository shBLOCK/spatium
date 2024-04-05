from itertools import count
from typing import Sequence, Optional

import regex

#TODO: docstring

def convert_type(org: str) -> str:
    types = []
    for raw in map(str.strip, org.split("|")):
        match raw:
            case "float" | "double" | "py_float":
                types.append("(float | int)")
            case "int" | "long" | "py_int":
                types.append("int")
            case "None" | "void":
                types.append("None")
            case "object":
                types.append("Any")
            case _:
                types.append(f'"{raw}"')
    return types[0] if len(types) == 1 else f"Union[{', '.join(types)}]"

class StubProperty:
    def __init__(self, name: str, ptype: str, mutable: bool = True):
        self.name = name
        self.type = ptype
        self.mutable = mutable

    def stub(self) -> list[str]:
        # if self.mutable:
        #     return [f"{self.name}: {self.type}"]
        # else:
        #     return [
        #         "@property",
        #         f"def {self.name}(self) -> {self.type}: ..."
        #     ]
        stub = [
            "@property",
            f"def {self.name}(self) -> {self.type}: ..."
        ]
        if self.mutable:
            stub.append(f"@{self.name}.setter")
            stub.append(f"def {self.name}(self, value: {self.type}) -> None: ...")
        return stub


class StubMethod:
    class Param:
        def __init__(self, name: str, ptype: str, default: Optional[str] = None, const_mapping: dict[str, str] = None):
            self.name = name
            self.ptype = ptype
            self.default = default
            self.const_mapping = const_mapping

        def stub(self) -> str:
            stub = f"{self.name}: {self.ptype}"
            if self.default is not None:
                default = self.default
                if self.const_mapping:
                    default = self.const_mapping.get(default, default)
                stub += f" = {default}"
            return stub

    def __init__(self, name: str, rtype: str, params: Sequence[Param | str], is_cdef: bool, is_static: bool):
        self.name = name
        self.rtype = rtype
        self.params = params
        self.is_cdef = is_cdef
        self.is_static = is_static

    def stub(self, name_override: Optional[str] = None) -> list[str]:
        stub = []
        if self.is_static:
            stub.append("@staticmethod")

        param_list = [] if self.is_static else ["self"]
        for p in self.params:
            if type(p) is str:
                param_list.append(p)
            else:
                param_list.append(p.stub())

        stub.append(f"def {name_override or self.name}({', '.join(param_list)}) -> {self.rtype}: ...")
        return stub

class StubClass:
    def __init__(self, name: str):
        self.name = name
        self.properties: dict[str, StubProperty] = {}
        self.methods: dict[str, StubMethod] = {}

    def stub(self) -> list[str]:
        def indent(src: list[str]) -> list[str]:
            for i, line in enumerate(src):
                src[i] = " " * 4 + line
            return src

        stub = [
            "# noinspection SpellCheckingInspection",
            f"class {self.name}:"
        ]

        for prop in self.properties.values():
            stub.extend(indent(prop.stub()))

        stub.append("")

        methods = self.methods.copy()
        while methods:
            _, method = methods.popitem()
            if not method.is_cdef:
                # Overloaded
                if f"_{method.name}_0" in methods:
                    for i in count():
                        ol_name = f"_{method.name}_{i}"
                        if ol_method := methods.get(ol_name):
                            del methods[ol_name]
                            assert ol_method.is_cdef
                            stub.extend(indent(["@overload"]))
                            stub.extend(indent(ol_method.stub(name_override=method.name)))
                        else:
                            break
                # Not Overloaded
                else:
                    stub.extend(indent(method.stub()))

        return stub


def gen_stub(source: str) -> str:
    const_mapping = {}
    decorators = []
    classes = []
    clazz = None

    print("gen_stub: reading source...")
    source_lines = source.splitlines(keepends=False)
    for line_no, line in enumerate(source_lines):
        # Class
        if m := regex.match(r"cdef\s+class\s+(?P<name>\w+)\s*:", line):
            if clazz is not None:
                classes.append(clazz)
            clazz = StubClass(m.group("name"))
            decorators.clear()
        # Property
        elif m := regex.match(r"\s+cdef\s+public\s+(?P<type>\w+)\s+(?P<names>\w+)(?:\s*,\s*(?P<names>\w+))*", line):
            ptype = convert_type(m.group("type"))
            for pname in m.captures("names"):
                clazz.properties[pname] = StubProperty(pname, ptype)
            decorators.clear()
        # Method (including @property)
        elif (
                (cdef_m := regex.match( # cdef methods can not be static, self always present
                    r"\s+cdef\s+"
                    r"(?:inline\s+)?"
                    r"(?P<return>\w+)?\s+"
                    r"(?P<name>\w+)\s*"
                    r"\(\s*"
                    r"(?:self\s*)?"
                    r"(?:,\s*(?P<params>\w+\s+\w+)\s*)*"
                    r"\)\s*"
                    r"(?:noexcept)?\s*"
                    r":",
                    line
                ))
                or
                (def_m := regex.match(
                    r"\s+def\s+"
                    r"(?P<name>\w+)\s*"
                    r"\(\s*"
                    r"(?:(?:self\s*)|(?&_param))?"
                    r"(?:,\s*(?P<_param>(?P<params>\w+\s+\w+(?:\s*=\s*[^,)]+)?)|(?P<params>/))\s*)*"
                    r"\)\s*"
                    r"(?:->\s*(?P<return>[^:]+))?\s*"
                    r":",
                    line
                ))
            ):
            m = cdef_m or def_m
            is_cdef = cdef_m is not None
            name = m.group("name")

            assert "classmethod" not in decorators
            # property getter
            if "property" in decorators:
                assert name not in clazz.properties
                clazz.properties[name] = StubProperty(name, convert_type(m.group("return")), mutable=False)
            # proeprty setter
            elif setter_dec := [d for d in decorators if d.endswith(".setter")]:
                assert len(setter_dec) == 1
                pname = setter_dec[0].split(".")[0]
                clazz.properties[pname].mutable = True
            # normal method
            else:
                rtype = convert_type(m.group("return") or "object")
                if source_lines[line_no + 1].strip() == "#<RETURN_SELF>":
                    rtype = "Self"

                params = []
                for param in m.captures("params"):
                    if param == "/":
                        params.append(param)
                        continue
                    if is_cdef:
                        # default values are not supported for cdef methods yet
                        pm = regex.fullmatch(r"(?P<type>\w+)\s+(?P<name>\w+)", param)
                        assert pm is not None
                        params.append(StubMethod.Param(pm.group("name"), convert_type(pm.group("type")), const_mapping=const_mapping))
                    else:
                        pm = regex.fullmatch(r"(?P<type>\w+)\s+(?P<name>\w+)(?:\s*=\s*(?P<default>[^,]+))?", param)
                        assert pm is not None
                        params.append(StubMethod.Param(pm.group("name"), convert_type(pm.group("type")), pm.group("default"), const_mapping=const_mapping))

                clazz.methods[name] = StubMethod(
                    name,
                    rtype,
                    params,
                    is_cdef,
                    is_static="staticmethod" in decorators
                )

            decorators.clear()
        # Decorator
        elif m := regex.match(r"\s+@\s*(?P<decorator>\w[\w.]*)", line):
            decorators.append(m.group("decorator"))
        # DEF
        elif m := regex.match(r"DEF\s+(?P<name>\w+)\s*=\s*(?P<value>.+)", line):
            const_mapping[m.group("name")] = m.group("value")
        else:
            # if ("cdef" in line or "def" in line) and ":" in line:
            #     print(f"Warning: ignored def or cdef line: {line}")
            pass

    if clazz is not None:
        classes.append(clazz)

    out_lines = [
        "from typing import overload, Self, Any, Union",
        ""
    ]
    for cls in classes:
        print(f"gen_stub: generating class {cls.name}")
        out_lines.extend(cls.stub())
        out_lines.append("")
    return "".join(f"{line}\n" for line in out_lines)


if __name__ == '__main__':
    result = gen_stub(open("output/_gdmath.pyx", encoding="utf8").read())
    with open("output/_gdmath.pyi", "w") as f:
        f.write(result)
