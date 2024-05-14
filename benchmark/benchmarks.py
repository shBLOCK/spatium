# fmt: off
# begin: noinspection PyUnresolvedReferences
# begin: noinspection PyUnusedLocal
# begin: noinspection PyUnboundLocalVariable
# begin: noinspection PyTypeChecker
# begin: noinspection PyCallingNonCallable
# begin: noinspection PyStatementEffect
# begin: noinspection PyShadowingNames

from benchmarking import *

# Get rid of the import message
import pygame; print(); del pygame

# Dummy values to get rid of IDE errors
import numpy as np
from numpy import array
from pygame import Vector3
from spatium import Vec3
a: Vec3
b: Vec3


# section Benchmark
@Subject("Spatium", color="tab:purple", sort=30)
def spatium():
    from spatium import Vec3
    a = Vec3(1, 2, 3)
    b = a.zyx

@Subject("Pure Python", color="tab:blue", sort=10)
def pure_python():
    from pure_python_impl import Vec3
    a = Vec3(1, 2, 3)
    b = Vec3(3, 2, 1)

@Subject("Pygame", color="tab:green", sort=20)
def pygame():
    from pygame import Vector3
    a = Vector3(1, 2, 3)
    b = a.zyx

@Subject("Numpy", color="tab:orange", sort=0)
def numpy():
    import numpy as np
    array = np.array
    a = array((1.0, 2.0, 3.0), dtype=np.float64)
    b = array((3.0, 2.0, 1.0), dtype=np.float64)

@Subject("PyGLM", color="tab:cyan", sort=25)
def pyglm():
    from glm import vec3
    a = vec3(1, 2, 3)
    b = vec3(3, 2, 1)


instantiation = Benchmark("Instantiation")
@instantiation(spatium, pure_python)
def _():
    Vec3(1.0, 2.0, 3.0)
@instantiation
def pygame():
    Vector3(1.0, 2.0, 3.0)
@instantiation
def numpy():
    array((1.0, 2.0, 3.0))
@instantiation
def pyglm():
    vec3(1.0, 2.0, 3.0)

copy = Benchmark("Copy")
@copy(spatium, pure_python, pyglm)
def _():
    +a
@copy(pygame, numpy)
def _():
    a.copy()

add = Benchmark("Addition")
@add
def _all_():
    a + b

add_ip = Benchmark("Inplace Addition")
@add_ip
def _all_():
    a += b

dot = Benchmark("Dot Product")
@dot(spatium, pure_python)
def _():
    a @ b
@dot(pygame, numpy)
def _():
    a.dot(b)
@dot.setup(pyglm)
def _():
    from glm import dot
@dot
def pyglm():
    dot(a, b)

cross = Benchmark("Cross Product")
@cross(spatium, pure_python)
def _():
    a ^ b
@cross
def pygame():
    a.cross(b)
@cross.setup(numpy)
def _():
    cross = np.cross
@cross.setup(pyglm)
def _():
    from glm import cross
@cross(numpy, pyglm)
def _():
    cross(a, b)

equality = Benchmark("Equality")
@equality
def _all_():
    a == b

iteration = Benchmark("Iteration")
@iteration
def _all_():
    tuple(a)

length = Benchmark("Length")
@length(spatium, pure_python)
def _():
    a.length
@length
def pygame():
    a.length()
@length.setup(pyglm)
def _():
    from glm import length
@length
def pyglm():
    length(a)

normalize = Benchmark("Normalize")
@normalize(spatium, pure_python)
def _():
    a.normalized
@normalize
def pygame():
    a.normalize()
@normalize.setup(numpy)
def _():
    norm = np.linalg.norm
@normalize
def numpy():
    norm(a)
@normalize.setup(pyglm)
def _():
    from glm import normalize
@normalize
def pyglm():
    normalize(a)

get_item = Benchmark("Get Item")
@get_item
def _all_():
    a[1]

set_item = Benchmark("Set Item")
@set_item
def _all_():
    a[1] = 4.0

swizzle_get = Benchmark("Swizzle Get")
@swizzle_get(spatium, pure_python, pygame, pyglm)
def _():
    a.zxy

swizzle_set = Benchmark("Swizzle Set")
@swizzle_set(spatium, pure_python, pygame, pyglm)
def _():
    a.zxy = b


result = run_benchmarks(
    order_permutations=True,
    min_runs_per_case=100
)
save_result(result, Path("results" if CI else "results_local", result.datetime.strftime("%Y%m%d_%H-%M-%S") + ".dat"))
