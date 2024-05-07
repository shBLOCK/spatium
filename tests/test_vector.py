import pytest
import math

from spatium import *


def test_empty_constructor():
    vec = Vec3(0)
    assert vec.x == vec.y == vec.z == 0

def test_normal_constructor():
    vec = Vec3(1, 2, 3)
    assert vec.x == 1
    assert vec.y == 2
    assert vec.z == 3

    vec = Vec3(1, 2.0, 3)
    assert vec.x == 1
    assert vec.y == 2
    assert vec.z == 3

def test_combined_constructors():
    vec = Vec4(Vec2(1, 2), Vec2(3, 4))
    assert vec.x == 1
    assert vec.y == 2
    assert vec.z == 3
    assert vec.w == 4

    vec = Vec3(1, Vec2(2, 3))
    assert vec.x == 1
    assert vec.y == 2
    assert vec.z == 3

def test_type_conversion_constructor():
    vec = Vec3(Vec3i(1, 2, 3))
    assert vec.x == 1
    assert vec.y == 2
    assert vec.z == 3

def test_repr():
    assert repr(Vec3(1, 2, 3)) == "Vec3(1.0, 2.0, 3.0)"
    assert repr(Vec3i(1, 2, 3)) == "Vec3i(1, 2, 3)"

def test_comparison():
    a = Vec3(1, 2, 3)
    b = Vec3(3, 2, 1)
    c = Vec3(1, 2, 3)
    assert (a != b) == True
    assert (a == c) == True
    assert (a == b) == False
    assert (a != c) == False

def test_swizzle():
    v2 = Vec2(1, 2)
    v3 = Vec3(1, 2, 3)
    v4 = Vec4(1, 2, 3, 4)
    assert v2.yx == Vec2(2, 1)
    assert v2.yxxy == Vec4(2, 1, 1, 2)
    assert v3.yxzy == Vec4(2, 1, 3, 2)
    assert v3.ylo == Vec3(2, 1, 0)
    assert v4.wzyx == Vec4(4, 3, 2, 1)

def test_copy():
    a = Vec3(1, 2, 3)
    b = +a
    b.x = 5
    assert a == Vec3(1, 2, 3)
    assert b == Vec3(5, 2, 3)

def test_neg():
    a = Vec3(1, 2, 3)
    b = -a
    assert b == Vec3(-1, -2, -3)

def test_add():
    a = Vec3(1, 2, 3)
    b = Vec3(4, 5, 6)
    assert a + b == Vec3(5, 7, 9)
    assert a == Vec3(1, 2, 3)

def test_iadd():
    a = Vec3(1, 2, 3)
    b = Vec3(4, 5, 6)
    a += b
    assert a == Vec3(5, 7, 9)

def test_add_float():
    a = Vec3(1, 2, 3)
    assert a + 1.5 == Vec3(2.5, 3.5, 4.5)

def test_add_int():
    a = Vec3(1, 2, 3)
    assert a + 1 == Vec3(2, 3, 4)

def test_iadd_float():
    a = Vec3(1, 2, 3)
    a += 1.5
    assert a == Vec3(2.5, 3.5, 4.5)

def test_sub():
    a = Vec3(1, 2, 3)
    b = Vec3(6, 5, 4)
    assert a - b == Vec3(-5, -3, -1)

def test_mul():
    a = Vec3(1, 2, 3)
    b = Vec3(0, 2, 4)
    assert a * b == Vec3(0, 4, 12)

def test_div():
    a = Vec3(1, 2, 3)
    b = Vec3(0.5, 2, 1.5)
    assert a / b == Vec3(2, 1, 2)

def test_div_zero():
    a = Vec3(1, 2, 3)
    b = Vec3(0, 1, 2)
    import math
    assert a / b == Vec3(math.inf, 2, 1.5)

def test_dot():
    a = Vec3(1, 2, 3)
    b = Vec3(2, 1, 3)
    assert a @ b == 13.0

def test_cross():
    a = Vec3(1, 2, 3)
    b = Vec3(3, 7, 5)
    assert a ^ b == Vec3(-11, 4, 1)

    a = Vec2(1, 2)
    b = Vec2(3, 4)
    with pytest.raises(TypeError):
        # noinspection PyStatementEffect
        a ^ b

def test_len():
    assert len(Vec2()) == 2
    assert len(Vec3()) == 3
    assert len(Vec4()) == 4
    assert len(Vec2i()) == 2
    assert len(Vec3i()) == 3
    assert len(Vec4i()) == 4

def test_iter():
    for i, value in enumerate(Vec3(1, 2, 3)):
        assert value == i+1

def test_unpack():
    x, y, z = Vec3(1, 2, 3)
    assert x == 1
    assert y == 2
    assert z == 3

def test_getitem():
    assert Vec3(0, 1.5, 0)[1] == 1.5

def test_setitem():
    v = Vec3(1, 3, 3)
    v[1] = 2
    assert v == Vec3(1, 2, 3)

def test_length():
    assert math.isclose(Vec3(1, 2, 3).length, 3.7416573867739413)

def test_length_squared():
    assert Vec3(1, 2, 3).length_sqr == 14

def test_distance_to():
    a = Vec3(1, 2, 3)
    b = Vec3(4, 5, 6)
    assert math.isclose(a.distance_to(b), (a - b).length)

def test_distance_to_with_or_operator():
    a = Vec3(1, 2, 3)
    b = Vec3(4, 5, 6)
    assert math.isclose(a | b, (a - b).length)

def test_distance_squared_to():
    a = Vec3(1, 2, 3)
    b = Vec3(4, 5, 6)
    assert a.distance_sqr_to(b) == 27

def test_normalized():
    a = Vec3(1, 2, 3)
    a = a.normalized
    assert math.isclose(a.x, 0.2672612419124244)
    assert math.isclose(a.y, 0.5345224838248488)
    assert math.isclose(a.z, 0.8017837257372732)

def test_big_int():
    Vec2i(2**63-1)

def test_float_precision():
    assert Vec2(math.ulp(0)).x == math.ulp(0)
    assert Vec2(1e308).x == 1e308
