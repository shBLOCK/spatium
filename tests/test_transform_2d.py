from math import sin, cos, isclose
from random import random

from spatium import Transform2D, Vec2


def test_normal_constructor_and_get_components():
    t = Transform2D(1, 2, 3, 4, 5, 6)
    assert t.x == Vec2(1, 2)
    assert t.y == Vec2(3, 4)
    assert t.origin == Vec2(5, 6)

def test_comparison():
    def gen_diff_at(index, n):
        return Transform2D(*[n if i == index else 0.5 for i in range(6)])

    for a in range(6):
        for b in range(6):
            num = random() + 0.6
            result = gen_diff_at(a, num) == gen_diff_at(b, num)
            assert result if a == b else not result

def test_set_components():
    t = Transform2D()
    t.x = Vec2(1, 2)
    t.y = Vec2(3, 4)
    t.origin = Vec2(5, 6)
    assert t == Transform2D(1, 2, 3, 4, 5, 6)

def test_empty_constructor():
    assert Transform2D() == Transform2D(1, 0, 0, 1, 0, 0)

def test_component_constructor():
    assert Transform2D(Vec2(1, 2), Vec2(3, 4), Vec2(5, 6)) == Transform2D(1, 2, 3, 4, 5, 6)

def test_copy_constructor():
    t = Transform2D(*range(6))
    tc = Transform2D(t)
    assert id(t) != id(tc)
    assert t == tc

def test_translation_constructor():
    t = Transform2D.translating(Vec2(1, 2))
    assert t == Transform2D(1, 0, 0, 1, 1, 2)

def test_rotating_constructor():
    r = 1.23
    t = Transform2D.rotating(r)
    assert t.is_close(Transform2D(cos(r), sin(r), -sin(r), cos(r), 0, 0), 1e-7)

def test_scaling_constructor():
    t = Transform2D.scaling(Vec2(1, 2))
    assert t == Transform2D(1, 0, 0, 2, 0, 0)

def test_vector_xform():
    t = Transform2D(1, 2, 3, 4, 5, 6)
    v = Vec2(1, 2)
    ans = Vec2(12, 16)
    assert (t * v).is_close(ans)
    assert t(v).is_close(ans)

def test_vector_inverse_xform():
    print(Vec2(1, 2) * Transform2D(1, 2, 3, 4, 5, 6))
    print((~Transform2D(*range(1, 7))) * Vec2(1, 2))
    assert (Vec2(1, 2) * Transform2D(1, 2, 3, 4, 5, 6)).is_close(Vec2(-12, -28))

def test_matmul():
    t1 = Transform2D(1, 2, 3, 4, 5, 6)
    t2 = Transform2D(3, 1, 2, 6, 5, 4)
    ans = Transform2D(6, 10, 20, 28, 22, 32)
    assert (t1 @ t2).is_close(ans)
    assert t1(t2).is_close(ans)

def test_imatmul():
    t1 = Transform2D(1, 2, 3, 4, 5, 6)
    t2 = Transform2D(3, 1, 2, 6, 5, 4)
    t3 = Transform2D(t1)
    t3 @= t2
    assert t2 @ t1 == t3

def test_determinant():
    assert isclose(Transform2D(1.6, 2.5, 3.4, 4.3, 5.2, 6.1).determinant, -1.62)

def test_inverse():
    assert (~Transform2D(1, 2, 3, 4, 5, 6)).is_close(Transform2D(-2, 1, 1.5, -0.5, 1, -2))
