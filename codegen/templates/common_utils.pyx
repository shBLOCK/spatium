#<TEMPLATE_BEGIN>
from libc.math cimport fabs, isfinite

DEF DEFAULT_RELATIVE_TOLERANCE = 1e-5
DEF DEFAULT_ABSOLUTE_TOLERANCE = 1e-14

cdef inline bint is_close(double a, double b, double rel_tol = DEFAULT_RELATIVE_TOLERANCE, double abs_tol = DEFAULT_ABSOLUTE_TOLERANCE):
    cdef double diff = fabs(a - b)
    if a == b:
        return True
    if not isfinite(a) or not isfinite(b):
        return False
    return diff <= fabs(rel_tol * a) or diff <= fabs(rel_tol * b) or diff <= fabs(abs_tol)
#<TEMPLATE_END>