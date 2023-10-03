#<TEMPLATE_BEGIN>
#cython: language_level=3
#cython: binding=False
#cython: boundscheck=False
#cython: wraparound=False
#cython: nonecheck=False
#cython: cdivision=True
#cython: always_allow_keywords=True
#cython: optimize.use_switch=True

cimport cython


########## common_utils.pyx ##########
#<GEN>: step_generate("common_utils.pyx")


########## vector.pyx ##########
#<GEN>: step_generate("vector.pyx", _globals=vector_codegen.get_globals())


########## transform_2d.pyx ##########
#<GEN>: step_generate("transform_2d.pyx", overload=True)


########## transform_3d.pyx ##########
#<GEN>: step_generate("transform_3d.pyx", overload=True)
#<TEMPLATE_END>