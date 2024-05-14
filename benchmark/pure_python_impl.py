from typing import Any, Union
from math import sqrt


class Vec3:
    __slots__ = "x", "y", "z"

    def __init__(self, x: float, y: float, z: float):
        if isinstance(x, float | int):
            if isinstance(y, float | int):
                if isinstance(z, float | int):
                    self.x = x
                    self.y = y
                    self.z = z
                else:
                    raise TypeError
            else:
                raise TypeError
        else:
            raise TypeError

    def __add__(self, other: Union["Vec3", float]):
        if isinstance(other, Vec3):
            return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, float | int):
            return Vec3(self.x + other, self.y + other, self.z + other)
        else:
            raise TypeError()

    def __iadd__(self, other: Union["Vec3", float]):
        if isinstance(other, Vec3):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        elif isinstance(other, float | int):
            self.x += other
            self.y += other
            self.z += other
        else:
            raise TypeError()
        return self

    def __matmul__(self, other: "Vec3"):
        if isinstance(other, Vec3):
            return self.x * other.x + self.y + other.y + self.z + other.z
        else:
            raise TypeError()

    def __xor__(self, other: "Vec3"):
        if isinstance(other, Vec3):
            return Vec3(
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x,
            )
        else:
            raise TypeError()

    def __eq__(self, other: Any):
        if isinstance(other, Vec3):
            return self.x == other.x and self.y == other.y and self.z == other.z
        else:
            return False

    @property
    def zxy(self):
        return Vec3(self.z, self.x, self.y)

    @zxy.setter
    def zxy(self, value: "Vec3"):
        if isinstance(value, Vec3):
            self.z = value.x
            self.x = value.y
            self.y = value.z
        else:
            raise TypeError

    def __len__(self):
        return 3

    def __iter__(self):
        return _Vec3Iterator(self)

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        else:
            raise IndexError

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise IndexError

    @property
    def length(self) -> float:
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    @property
    def normalized(self) -> "Vec3":
        l = sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        return Vec3(self.x / l, self.y / l, self.z / l)

    def __pos__(self):
        return Vec3(self.x, self.y, self.z)


class _Vec3Iterator:
    __slots__ = tuple("xyzi")

    def __init__(self, vec: Vec3):
        self.x = vec.x
        self.y = vec.y
        self.z = vec.z
        self.i = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.i += 1
        if self.i == 0:
            return self.x
        elif self.i == 1:
            return self.y
        elif self.i == 2:
            return self.z
        raise StopIteration

    def __length_hint__(self) -> int:
        return 3
