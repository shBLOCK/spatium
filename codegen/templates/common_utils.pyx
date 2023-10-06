#<TEMPLATE_BEGIN>
from libc.math cimport fabsl, isfinite
# from libcpp.bit cimport bit_cast, rotl


ctypedef long long py_int
ctypedef long double py_float


DEF DEFAULT_RELATIVE_TOLERANCE = 1e-09
DEF DEFAULT_ABSOLUTE_TOLERANCE = 1e-15


cdef inline bint is_close(py_float a, py_float b, py_float rel_tol = DEFAULT_RELATIVE_TOLERANCE, py_float abs_tol = DEFAULT_ABSOLUTE_TOLERANCE) noexcept:
    cdef py_float diff = fabsl(a - b)
    if a == b:
        return True
    if not isfinite(a) or not isfinite(b):
        return False
    return diff <= fabsl(rel_tol * a) or diff <= fabsl(rel_tol * b) or diff <= fabsl(abs_tol)


# cdef inline py_int bitcast_float(py_float d) noexcept:
#     return bit_cast[py_int, py_float](d)
#
# cdef inline py_int rotl_ratio(py_int num, int i, int total) noexcept:
#     return rotl[py_int](num, 64 // total * i)

cdef union _bitcaster:
    py_float f
    py_int i

cdef inline py_int bitcast_float(py_float f) noexcept:
    return _bitcaster(f=f).i

cdef inline py_int rotl_ratio(py_int num, int i, int total) noexcept:
    cdef int shift = (sizeof(py_int)*8) / total * i
    return (num << shift) | (num >> (sizeof(py_int)*8 - shift))
#<TEMPLATE_END>