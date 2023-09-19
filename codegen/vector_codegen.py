from itertools import product
from typing import Type, Any, Iterator

from codegen_helper import from_template, process_overloads
import codegen_helper as codegen


DIMS = ("x", "y", "z", "w")
LENS = (2, 3, 4)
SPECIAL_SWIZS = ("o", "l")


def get_c_type(vtype: Type) -> str:
    if vtype is float:
        return f"double"
    elif vtype is int:
        return f"int"
    else:
        assert False


def get_vec_class_name(dims: int, vtype: Type) -> str:
    if vtype is float:
        return f"Vec{dims}"
    elif vtype is int:
        return f"Vec{dims}i"
    else:
        assert False


def gen_var_decls(dims: int, vtype_c: str) -> str:
    return f"cdef public {vtype_c} {', '.join(DIMS[:dims])}"


def gen_single_value_constructor(dims: int, value: Any) -> str:
    return " = ".join(f"self.{d}" for d in DIMS[:dims]) + " = " + str(value)


def gen_type_conversion_constructor(dims: int, vtype: Type) -> str:
    assert vtype is int or vtype is float
    from_type = float if vtype is int else int
    out = "#<OVERLOAD>\n"
    out += f"cdef void __init__(self, {get_vec_class_name(dims, from_type)} vec) noexcept:\n"
    for dim in DIMS[:dims]:
        out += f"    self.{dim} = <{get_c_type(vtype)}>vec.{dim}\n"
    return out


def _combination_constructors(dims: int) -> Iterator[tuple[int]]:
    for l in range(1, dims + 1):
        for con in product(range(1, dims + 1), repeat=l):
            if sum(con) == dims:
                yield con


def gen_combination_constructors(dims: int, vtype: Type) -> str:
    funcs = []
    for combination in _combination_constructors(dims):
        param_types = []
        param_names = []
        assigns = []

        # Generate params
        self_dim = 0
        for in_dims in combination:
            param_types.append(f"{get_c_type(vtype) if in_dims == 1 else get_vec_class_name(in_dims, vtype)}")
            param_name = ""
            for in_dim in range(in_dims):
                param_name += DIMS[self_dim]
                self_dim += 1
            param_names.append(param_name)

        # Generate assigns
        self_dim = 0
        for in_dims, param_name in zip(combination, param_names):
            for in_dim in range(in_dims):
                if in_dims == 1:
                    assigns.append(f"self.{DIMS[self_dim]} = {param_name}")
                else:
                    assigns.append(f"self.{DIMS[self_dim]} = {param_name}.{DIMS[in_dim]}")
                self_dim += 1

        func = "#<OVERLOAD>\n"
        func += (f"cdef void __init__(self, "
                 f"{', '.join(f'{t} {n}' for t, n in zip(param_types, param_names))}) noexcept:\n")
        for assign in assigns:
            func += f"    {assign}\n"
        func = func[:-1]  # remove last \n
        funcs.append(func)

    return "\n\n".join(funcs)


def _swizzles(dims: int) -> Iterator[str]:
    for l in LENS:
        for swizs in product(DIMS[:dims] + SPECIAL_SWIZS, repeat=l):
            if all(s in SPECIAL_SWIZS for s in swizs):
                continue
            yield "".join(swizs)


def _gen_swizzle_get(swizzle: str, vtype: Type) -> str:
    out = "@property\n"
    vec_cls = get_vec_class_name(len(swizzle), vtype)
    out += f"def {swizzle}(self) -> {vec_cls}:\n"
    out += f"    cdef {vec_cls} vec = {vec_cls}.__new__({vec_cls})\n"
    for i, swiz in enumerate(swizzle):
        if swiz in DIMS:
            val = f"self.{swiz}"
        elif swiz == "o":
            val = str(vtype(0))
        elif swiz == "l":
            val = str(vtype(1))
        else:
            assert False
        out += f"    vec.{DIMS[i]} = {val}\n"
    out += "    return vec\n"
    return out


def _gen_swizzle_set(swizzle: str, vtype: Type):
    out = f"@{swizzle}.setter\n"
    out += f"def {swizzle}(self, {get_vec_class_name(len(swizzle), vtype)} vec) -> None:\n"
    for i, swiz in enumerate(swizzle):
        assert swiz in DIMS
        out += f"    self.{swiz} = vec.{DIMS[i]}\n"
    return out


def _swizzle_has_setter(swizzle: str, dims: int) -> bool:
    if len(swizzle) != dims:
        return False
    for swiz in swizzle:
        if swiz not in DIMS:
            return False
    if len(set(swizzle)) != len(swizzle):
        return False
    return True


def gen_swizzle_properties(dims: int, vtype: Type) -> str:
    out = ""
    for swizzle in _swizzles(dims):
        out += _gen_swizzle_get(swizzle, vtype)
        out += "\n"

        if _swizzle_has_setter(swizzle, dims):
            out += _gen_swizzle_set(swizzle, vtype)
            out += "\n"
    out = out[:-1]  # remove last \n
    return out


def gen_for_each_dim(template: str, dims: int, join="\n") -> str:
    out = ""
    for dim in range(dims):
        out += template.format_map({
            "dim": DIMS[dim]
        })
        if dim != dims - 1:
            out += join
    return out


def gen_repr(dims: int, vtype: Type) -> str:
    out = 'f"'
    out += get_vec_class_name(dims, vtype)
    out += "("
    dim_formats = []
    for dim in DIMS[:dims]:
        dim_formats.append(f"{{self.{dim}}}")
    out += ", ".join(dim_formats)
    out += ')"'
    return out

def gen_common_binary_and_inplace_op(op: str, name: str) -> str:
    return from_template(open("templates/common_binary_and_inplace_op.pyx").read(), {"Op": op, "OpName": name})

def gen_item_op(dims: int, op: str) -> str:
    out = ""
    for dim in range(dims):
        out += "if " if dim == 0 else "elif "
        out += f"key == {dim}:\n"
        out += f"    {op.format(dim=DIMS[dim])}\n"
    out += "else:\n"
    out += "    raise KeyError(f\"_VecClassName_ index out of range: {key}\")"
    return out

def gen_iterator_next(dims: int) -> str:
    out = ""
    for dim in range(dims):
        out += "if " if dim == 0 else "elif "
        out += f"self.index == {dim}:\n"
        out += f"    self.index += 1\n"
        out += f"    return self.{DIMS[dim]}\n"
    out += "raise StopIteration"
    return out


def gen_vec_class(dims: int, vtype: Type) -> str:
    params = {
        "Dims": dims,
        "vType": vtype.__name__,
        "vTypeC": get_c_type(vtype),
        "VecClassName": get_vec_class_name(dims, vtype),
    }

    cls = from_template(open("templates/vec_class.pyx").read(), params)
    cls = process_overloads(cls)
    return cls


if __name__ == '__main__':
    import shutil
    codegen.step_generate("vector.pyx", _globals=globals())

    shutil.copy("output/vector.pyx", "../src/gdmath/vector.pyx")

    # codegen.step_cythonize("vector")
    # codegen.step_move_to_dest("../sim/math/", "vector", ".pyd")
