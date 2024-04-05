cimport cython
from libc.math cimport sqrtl

# Dummy types for the IDE
ctypedef _VecClassName_
ctypedef _vTypeC_
ctypedef _vType_
ctypedef Vec2
ctypedef Vec3
ctypedef Vec4
ctypedef Vec2i
ctypedef Vec3i
ctypedef Vec4i
ctypedef Transform2D
ctypedef Transform3D
ctypedef py_int
ctypedef py_float

DEF DEFAULT_RELATIVE_TOLERANCE = 0 # Dummy Value
DEF DEFAULT_ABSOLUTE_TOLERANCE = 0 # Dummy Value

#<TEMPLATE_BEGIN>
# noinspection SpellCheckingInspection
@cython.auto_pickle(True)
@cython.freelist(4096)
@cython.no_gc
@cython.final
cdef class _VecClassName_:
    #<GEN>: gen_var_decls(_Dims_, "_vTypeC_")


    #<OVERLOAD>
    cdef void __init__(self) noexcept:
        #<GEN>: gen_single_value_constructor(_Dims_, _vType_(0))
        pass #<IGNORE>

    #<OVERLOAD>
    cdef void __init__(self, _vTypeC_ value) noexcept:
        #<GEN>: gen_single_value_constructor(_Dims_, "value")
        pass #<IGNORE>

    #<GEN>: gen_type_conversion_constructor(_Dims_, _vType_)

    #<GEN>: gen_combination_constructors(_Dims_, _vType_)

    #<OVERLOAD_DISPATCHER>:__init__


    def __repr__(self) -> str:
        return #<GEN>: gen_repr(_Dims_, _vType_)

    def __eq__(self, object other) -> bool:
        if not isinstance(other, _VecClassName_):
            return False
        return #<GEN>: gen_for_each_dim("self.{dim} == other.{dim}", _Dims_, join=" and ")

    def __ne__(self, object other) -> bool:
        if not isinstance(other, _VecClassName_):
            return True
        return #<GEN>: gen_for_each_dim("self.{dim} != other.{dim}", _Dims_, join=" or ")

    def is_close(self, _VecClassName_ other, /, py_float rel_tol = DEFAULT_RELATIVE_TOLERANCE, py_float abs_tol = DEFAULT_ABSOLUTE_TOLERANCE) -> bool:
        return #<GEN>: gen_for_each_dim("is_close(<py_float> self.{dim}, <py_float> other.{dim}, rel_tol, abs_tol)", _Dims_, join=" and ")

    def __bool__(self) -> bool:
        return #<GEN>: gen_for_each_dim("self.{dim} == 0", _Dims_, join=" and ")

    #TODO: Better hashing
    #<IF>: _vType_ is int
    def __hash__(self) -> py_int:
        cdef py_int h = 0
        #<GEN>: gen_for_each_dim("h ^= rotl_ratio(self.{dim}, {index}, _Dims_)", _Dims_, join="\n")
        return h
    #<ENDIF>
    #<IF>: _vType_ is float
    def __hash__(self) -> py_int:
        cdef py_int h = 0
        #<GEN>: gen_for_each_dim("h ^= rotl_ratio(bitcast_float(self.{dim}), {index}, _Dims_)", _Dims_, join="\n")
        return h
    #<ENDIF>

    def __pos__(self) -> _VecClassName_:
        cdef _VecClassName_ vec = _VecClassName_.__new__(_VecClassName_)
        #<GEN>: gen_for_each_dim("vec.{dim} = self.{dim}", _Dims_)
        return vec

    def __neg__(self) -> _VecClassName_:
        cdef _VecClassName_ vec = _VecClassName_.__new__(_VecClassName_)
        #<GEN>: gen_for_each_dim("vec.{dim} = -self.{dim}", _Dims_)
        return vec

    #<GEN>: gen_common_binary_and_inplace_op("+", "add")

    #<GEN>: gen_common_binary_and_inplace_op("-", "sub")

    #<GEN>: gen_common_binary_and_inplace_op("*", "mul")
    #<IF>: _Dims_ == 2
    #<OVERLOAD>
    cdef Vec2 __mul__(self, Transform2D t):
        cdef Vec2 vec = Vec2.__new__(Vec2)
        cdef py_float x = self.x - t.ox
        cdef py_float y = self.y - t.oy
        vec.x = t.xx * x + t.xy * y
        vec.y = t.yx * x + t.yy * y
        return vec
    #<ENDIF>
    #<IF>: _Dims_ == 3
    #<OVERLOAD>
    cdef Vec3 __mul__(self, Transform3D t):
        cdef Vec3 vec = Vec3.__new__(Vec3)
        cdef py_float x = self.x - t.ox
        cdef py_float y = self.y - t.oy
        cdef py_float z = self.z - t.oz
        vec.x = t.xx * x + t.xy * y + t.xz * z
        vec.y = t.yx * x + t.yy * y + t.yz * z
        vec.z = t.zx * x + t.zy * y + t.zz * z
        return vec
    #<ENDIF>

    #<GEN>: gen_common_binary_and_inplace_op("/", "truediv")


    def __matmul__(self, _VecClassName_ other) -> _vTypeC_:
        """Vector dot product"""
        return #<GEN>: gen_for_each_dim("self.{dim} * other.{dim}", _Dims_, join=" + ")
    #<IF>: _Dims_ == 3

    def __xor__(self, _VecClassName_ other) -> _VecClassName_:
        """Vector cross product"""
        cdef _VecClassName_ vec = _VecClassName_.__new__(_VecClassName_)
        vec.x = self.y * other.z - self.z * other.y
        vec.y = self.z * other.x - self.x * other.z
        vec.z = self.x * other.y - self.y * other.x
        return vec
    #<ENDIF>


    def __len__(self) -> int:
        _Dims_ = 0  #<IGNORE>
        return _Dims_

    def __getitem__(self, int key) -> _vTypeC_:
        #<GEN>: gen_item_op(_Dims_, "return self.{dim}")
        pass  #<IGNORE>

    def __setitem__(self, int key, _vTypeC_ value) -> None:
        #<GEN>: gen_item_op(_Dims_, "self.{dim} = value")
        pass  #<IGNORE>

    def __iter__(self) -> __VecClassName_iterator:
        cdef __VecClassName_iterator iterator = __VecClassName_iterator.__new__(__VecClassName_iterator)
        #<GEN>: gen_for_each_dim("iterator.{dim} = self.{dim}", _Dims_)
        # iterator.vec = self
        return iterator


    #<IGNORE_NEXT>
    # noinspection PyTypeChecker
    @property
    def length(self) -> py_float:
        return #<GEN>: f"sqrtl({gen_for_each_dim('<py_float> (self.{dim} * self.{dim})', _Dims_, join=' + ')})"

    #<IGNORE_NEXT>
    # noinspection PyTypeChecker
    @property
    def length_sqr(self) -> py_float:
        return #<GEN>: gen_for_each_dim("self.{dim} * self.{dim}", _Dims_, join=" + ")

    #<IGNORE_NEXT>
    # noinspection PyTypeChecker
    def __or__(self, _VecClassName_ other) -> py_float:
        """Equivalent to distance_to()"""
        #<GEN>: gen_for_each_dim("cdef _vTypeC_ d{dim} = self.{dim} - other.{dim}", _Dims_)
        return #<GEN>: f"sqrtl(<py_float> ({gen_for_each_dim('d{dim} * d{dim}', _Dims_, join=' + ')}))"

    #<IGNORE_NEXT>
    # noinspection PyTypeChecker
    def distance_to(self, _VecClassName_ other, /) -> py_float:
        #<GEN>: gen_for_each_dim("cdef _vTypeC_ d{dim} = self.{dim} - other.{dim}", _Dims_)
        return #<GEN>: f"sqrtl(<py_float> ({gen_for_each_dim('d{dim} * d{dim}', _Dims_, join=' + ')}))"

    #<IGNORE_NEXT>
    # noinspection PyTypeChecker
    def distance_sqr_to(self, _VecClassName_ other, /) -> py_float:
        #<GEN>: gen_for_each_dim("cdef _vTypeC_ d{dim} = self.{dim} - other.{dim}", _Dims_)
        return #<GEN>: f"<py_float> ({gen_for_each_dim('d{dim} * d{dim}', _Dims_, join=' + ')})"
    #<IF>: _vType_ is float

    @property
    def normalized(self) -> _VecClassName_:
        cdef py_float l = #<GEN>: f"sqrtl({gen_for_each_dim('self.{dim} * self.{dim}', _Dims_, join=' + ')})"
        cdef _VecClassName_ vec = _VecClassName_.__new__(_VecClassName_)
        #<GEN>: gen_for_each_dim("vec.{dim} = self.{dim} / l", _Dims_)
        return vec
    #<ENDIF>


    #<GEN>: gen_swizzle_properties(_Dims_, _vType_)


@cython.no_gc
@cython.final
@cython.freelist(8)
cdef class __VecClassName_iterator:
    #<GEN>: gen_var_decls(_Dims_, "_vTypeC_")
    cdef short index


    def __next__(self) -> _vType_:
        #<GEN>: gen_iterator_next(_Dims_)
        pass  #<IGNORE>

    def __iter__(self) -> __VecClassName_iterator:
        #<RETURN_SELF>
        return self

    def __length_hint__(self) -> int:
        _Dims_ = 0  #<IGNORE>
        return _Dims_
# <TEMPLATE_END>