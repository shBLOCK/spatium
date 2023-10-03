from math import sin, cos, isclose
from random import random

from gdmath import Transform3D, Vec3


def test_normal_constructor_and_get_components():
    t = Transform3D(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
    assert t.x == Vec3(1, 2, 3)
    assert t.y == Vec3(4, 5, 6)
    assert t.z == Vec3(7, 8, 9)
    assert t.origin == Vec3(10, 11, 12)

def test_comparison():
    def gen_diff_at(index, n):
        return Transform3D(*[n if i == index else 0.5 for i in range(12)])

    for a in range(12):
        for b in range(12):
            num = random() + 0.6
            result = gen_diff_at(a, num) == gen_diff_at(b, num)
            assert result if a == b else not result

def test_set_components():
    t = Transform3D()
    t.x = Vec3(1, 2, 3)
    t.y = Vec3(4, 5, 6)
    t.z = Vec3(7, 8, 9)
    t.origin = Vec3(10, 11, 12)
    assert t == Transform3D(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)

def test_empty_constructor():
    assert Transform3D() == Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)

def test_component_constructor():
    assert Transform3D(Vec3(1, 2, 3), Vec3(4, 5, 6), Vec3(7, 8, 9), Vec3(10, 11, 12)) == Transform3D(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)

def test_copy_constructor():
    t = Transform3D(*range(12))
    tc = Transform3D(t)
    assert id(t) != id(tc)
    assert t == tc

def test_translation_constructor():
    t = Transform3D.translating(Vec3(1, 2, 3))
    assert t == Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 2, 3)

def test_rotating_constructor():
    t = Transform3D.rotating(Vec3(1.85, 9.23, 3.42).normalized, 1.98)
    assert t.is_close(Transform3D(-0.350185, 0.551229, -0.757309, -0.075323, 0.789313, 0.609353, 0.933647, 0.270429, -0.234886, 0, 0, 0))

def test_scaling_constructor():
    t = Transform3D.scaling(Vec3(1, 2, 3))
    assert t == Transform3D(1, 0, 0, 0, 2, 0, 0, 0, 3, 0, 0, 0)

def test_vector_xform():
    t = Transform3D(*range(1, 13))
    v = Vec3(1, 2, 3)
    ans = Vec3(40, 47, 54)
    assert (t * v).is_close(ans)
    assert t(v).is_close(ans)

def test_vector_inverse_xform():
    assert (Vec3(1, 2, 3) * Transform3D(*range(1, 13))).is_close(Vec3(-54, -135, -216))

def test_matmul():
    t1 = Transform3D(*range(1, 13))
    t2 = Transform3D(10, 8, 4, 6, 12, 7, 5, 3, 2, 1, 11, 9)
    ans = Transform3D(70, 92, 114, 103, 128, 153, 31, 41, 51, 118, 140, 162)
    assert (t1 @ t2).is_close(ans)
    assert t1(t2).is_close(ans)

def test_determinant():
    assert isclose(Transform3D(1.12, 2.11, 0, 0, 5.8, 6.7, 7.6, 8.5, 0, 1, 2, 3).determinant, 43.6572)

def test_inverse():
    t = Transform3D(1, 2, 3, 6, 5, 4, 7, 9, 8, 1, 2, 3)
    ti = ~t
    assert (ti @ t).is_close(Transform3D())
