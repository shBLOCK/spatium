# Dummy types for the IDE
cdef class _VecClassName_:
    pass
ctypedef _vTypeC_

#<TEMPLATE_BEGIN>
#<OVERLOAD>
cdef _VecClassName_ ___OpName___(self, _VecClassName_ other):
    cdef _VecClassName_ vec = _VecClassName_.__new__(_VecClassName_)
    #<GEN>: gen_for_each_dim("vec.{dim} = self.{dim} _Op_ other.{dim}", _Dims_)
    return vec

#<OVERLOAD>
cdef _VecClassName_ ___OpName___(self, _vTypeC_ other):
    cdef _VecClassName_ vec = _VecClassName_.__new__(_VecClassName_)
    #<GEN>: gen_for_each_dim("vec.{dim} = self.{dim} _Op_ other", _Dims_)
    return vec

#<OVERLOAD_DISPATCHER>:___OpName___

#<OVERLOAD>
cdef _VecClassName_ __i_OpName___(self, _VecClassName_ other):
    #<RETURN_SELF>
    #<GEN>: gen_for_each_dim("self.{dim} _Op_= other.{dim}", _Dims_)
    return self

#<OVERLOAD>
cdef _VecClassName_ __i_OpName___(self, _vTypeC_ other):
    #<RETURN_SELF>
    #<GEN>: gen_for_each_dim("self.{dim} _Op_= other", _Dims_)
    return self

#<OVERLOAD_DISPATCHER>:__i_OpName___
#<TEMPLATE_END>