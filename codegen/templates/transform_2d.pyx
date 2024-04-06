cimport cython

# Dummy types for the IDE
ctypedef py_float
ctypedef py_int
cdef class Vec2:
    cdef py_float x, y


#<TEMPLATE_BEGIN>
from libc.math cimport atan2l, sinl, cosl, sqrtl, NAN


@cython.auto_pickle(True)
@cython.freelist(1024)
@cython.no_gc
@cython.final
cdef class Transform2D:
    """2D linear transformation (2*3 matrix)."""

    cdef py_float xx, xy
    cdef py_float yx, yy
    cdef py_float ox, oy


    cdef inline void identity(self) noexcept:
        self.xx, self.xy = 1.0, 0.0
        self.yx, self.yy = 0.0, 1.0
        self.ox = self.oy = 0.0

    #<OVERLOAD>
    cdef inline void __init__(self) noexcept:
        """Create an identity transform."""
        self.identity()

    #<OVERLOAD>
    cdef inline void __init__(self, py_float xx, py_float xy, py_float yx, py_float yy, py_float ox, py_float oy) noexcept:
        """Create a transform from all the matrix elements."""
        self.xx = xx
        self.xy = xy
        self.yx = yx
        self.yy = yy
        self.ox = ox
        self.oy = oy

    #<OVERLOAD>
    cdef inline void __init__(self, Vec2 x, Vec2 y, Vec2 origin) noexcept:
        """Create a transform using two base vectors and the origin vector."""
        self.xx, self.xy = x.x, x.y
        self.yx, self.yy = y.x, y.y
        self.ox, self.oy = origin.x, origin.y

    #<OVERLOAD>
    cdef inline void __init__(self, Transform2D transform) noexcept:
        """Create a copy."""
        self.xx = transform.xx
        self.xy = transform.xy
        self.yx = transform.yx
        self.yy = transform.yy
        self.ox = transform.ox
        self.oy = transform.oy

    #<OVERLOAD_DISPATCHER>:__init__

    @staticmethod
    def translating(Vec2 translation, /) -> Transform2D:
        """Create a translation transform."""
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.identity()
        t.ox, t.oy = translation.x, translation.y
        return t

    @staticmethod
    def rotating(py_float rotation, /, Vec2 origin = None) -> Transform2D:
        """Create a rotation transform."""
        cdef py_float c = cosl(rotation)
        cdef py_float s = sinl(rotation)
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.xx = c
        t.xy = s
        t.yx = -s
        t.yy = c
        if origin is not None:
            t.ox, t.oy = origin.x, origin.y
        return t

    @staticmethod
    def scaling(Vec2 scale, /, Vec2 origin = None) -> Transform2D:
        """Create a scale transform."""
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.xx = scale.x
        t.yy = scale.y
        if origin is not None:
            t.ox, t.oy = origin.x, origin.y
        return t

    cdef inline Transform2D copy(self):
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.xx = self.xx
        t.xy = self.xy
        t.yx = self.yx
        t.yy = self.yy
        t.ox = self.ox
        t.oy = self.oy
        return t

    def __repr__(self) -> str:
        return f"⎡X: ({self.xx}, {self.xy})\n⎢Y: ({self.yx}, {self.yy})\n⎣O: ({self.ox}, {self.oy})"

    def __eq__(self, object other) -> bool:
        """Perform exact comparison.

        See Also: `Transform2D.is_close()`
        """
        if not isinstance(other, Transform2D):
            return False
        return self.xx == (<Transform2D> other).xx and self.xy == (<Transform2D> other).xy and\
               self.yx == (<Transform2D> other).yx and self.yy == (<Transform2D> other).yy and\
               self.ox == (<Transform2D> other).ox and self.oy == (<Transform2D> other).oy

    def __ne__(self, object other) -> bool:
        """Perform exact comparison.

        See Also: `Transform2D.is_close()`
        """
        if not isinstance(other, Transform2D):
            return True
        return self.xx != (<Transform2D> other).xx or self.xy != (<Transform2D> other).xy or \
               self.yx != (<Transform2D> other).yx or self.yy != (<Transform2D> other).yy or \
               self.ox != (<Transform2D> other).ox or self.oy != (<Transform2D> other).oy

    def is_close(self, Transform2D other, /, py_float rel_tol = DEFAULT_RELATIVE_TOLERANCE, py_float abs_tol = DEFAULT_ABSOLUTE_TOLERANCE) -> bool:
        """Determine if the two transforms are close enough.

        See Also: `math.is_close()`
        """
        return is_close(self.xx, other.xx, rel_tol, abs_tol) and \
               is_close(self.xy, other.xy, rel_tol, abs_tol) and \
               is_close(self.yx, other.yx, rel_tol, abs_tol) and \
               is_close(self.yy, other.yy, rel_tol, abs_tol) and \
               is_close(self.ox, other.ox, rel_tol, abs_tol) and \
               is_close(self.oy, other.oy, rel_tol, abs_tol)

    #TODO: Better hashing
    def __hash__(self) -> py_int:
        cdef py_int h = 0
        h ^= bitcast_float(self.xx)
        h ^= rotl_ratio(bitcast_float(self.xy), 1, 6)
        h ^= rotl_ratio(bitcast_float(self.yx), 2, 6)
        h ^= rotl_ratio(bitcast_float(self.yy), 3, 6)
        h ^= rotl_ratio(bitcast_float(self.ox), 4, 6)
        h ^= rotl_ratio(bitcast_float(self.oy), 5, 6)
        return h

    @property
    def x(self) -> Vec2:
        """Base vector X."""
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.xx
        vec.y = self.xy
        return vec

    @property
    def y(self) -> Vec2:
        """Base vector Y."""
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.yx
        vec.y = self.yy
        return vec

    @property
    def origin(self) -> Vec2:
        """Origin vector."""
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.ox
        vec.y = self.oy
        return vec

    @x.setter
    def x(self, Vec2 value) -> None:
        """Set the X base of the matrix."""
        self.xx = value.x
        self.xy = value.y

    @y.setter
    def y(self, Vec2 value) -> None:
        """Set the Y base of the matrix."""
        self.yx = value.x
        self.yy = value.y

    @origin.setter
    def origin(self, Vec2 value) -> None:
        """Set the origin."""
        self.ox = value.x
        self.oy = value.y

    def __getitem__(self, py_int item) -> Vec2:
        """Get a column of the transformation matrix.

        0: Base vector X
        1: Base vector Y
        2: Origin vector
        """
        cdef Vec2 vec = Vec2.__new__(Vec2)

        if item == 0:
            vec.x = self.xx
            vec.y = self.xy
        elif item == 1:
            vec.x = self.yx
            vec.y = self.yy
        elif item == 2:
            vec.x = self.ox
            vec.y = self.oy
        else:
            raise IndexError(item)

        return vec

    def __setitem__(self, py_int key, Vec2 value) -> None:
        """Set a column of the transformation matrix.

        0: Base vector X
        1: Base vector Y
        2: Origin vector
        """

        if key == 0:
            self.xx = value.x
            self.xy = value.y
        elif key == 1:
            self.yx = value.x
            self.yy = value.y
        elif key == 2:
            self.ox = value.x
            self.oy = value.y
        else:
            raise IndexError(key)

    def __len__(self) -> py_int:
        """The amount of columns. Is always 3 for `Transform2D`s."""
        return 3

    cdef inline py_float tdotx(self, py_float x, py_float y) noexcept:
        return x * self.xx + y * self.yx

    cdef inline py_float mulx(self, py_float x, py_float y) noexcept:
        return self.tdotx(x, y) + self.ox

    cdef inline py_float tdoty(self, py_float x, py_float y) noexcept:
        return x * self.xy + y * self.yy

    cdef inline py_float muly(self, py_float x, py_float y) noexcept:
        return self.tdoty(x, y) + self.oy

    def __mul__(self, Vec2 other) -> Vec2:
        """Transform a copy of the vector."""
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.mulx(other.x, other.y)
        vec.y = self.muly(other.x, other.y)
        return vec

    #<OVERLOAD>
    cdef inline Vec2 __call__(self, Vec2 other):
        """Transform a copy of the vector."""
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.mulx(other.x, other.y)
        vec.y = self.muly(other.x, other.y)
        return vec

    #<OVERLOAD>
    cdef inline Transform2D __call__(self, Transform2D other):
        """Transform a copy of the passed in `Transform2D`."""
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.xx = self.tdotx(other.xx, other.xy)
        t.xy = self.tdoty(other.xx, other.xy)
        t.yx = self.tdotx(other.yx, other.yy)
        t.yy = self.tdoty(other.yx, other.yy)
        t.ox = self.mulx(other.ox, other.oy)
        t.oy = self.muly(other.ox, other.oy)
        return t

    #<OVERLOAD_DISPATCHER>:__call__

    def __matmul__(self, Transform2D other) -> Transform2D:
        """Transform a copy of the `Transform2D` on the right."""
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.xx = self.tdotx(other.xx, other.xy)
        t.xy = self.tdoty(other.xx, other.xy)
        t.yx = self.tdotx(other.yx, other.yy)
        t.yy = self.tdoty(other.yx, other.yy)
        t.ox = self.mulx(other.ox, other.oy)
        t.oy = self.muly(other.ox, other.oy)
        return t

    def __imatmul__(self, Transform2D other) -> Transform2D:
        #<RETURN_SELF>
        """Transform this `Transform2D` inplace with the other `Transform2D`."""
        cdef py_float xx = other.tdotx(self.xx, self.xy)
        cdef py_float xy = other.tdoty(self.xx, self.xy)
        cdef py_float yx = other.tdotx(self.yx, self.yy)
        cdef py_float yy = other.tdoty(self.yx, self.yy)
        cdef py_float ox = other.mulx(self.ox, self.oy)
        cdef py_float oy = other.muly(self.ox, self.oy)
        self.xx, self.xy = xx, xy
        self.yx, self.yy = yx, yy
        self.ox, self.oy = ox, oy
        return self

    cdef inline py_float _determinant(self) noexcept:
        return self.xx * self.yy - self.xy * self.yx

    @property
    def determinant(self) -> py_float:
        """Compute the determinant of the matrix."""
        return self._determinant()

    def __invert__(self) -> Transform2D:
        """Get the invert transform."""
        cdef py_float i_det = 1.0 / self._determinant()
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.xx = self.yy * +i_det
        t.xy = self.xy * -i_det
        t.yx = self.yx * -i_det
        t.yy = self.xx * +i_det
        t.ox = -t.tdotx(self.ox, self.oy)
        t.oy = -t.tdoty(self.ox, self.oy)
        return t


    cdef inline py_float get_rotation(self) noexcept:
        return atan2l(self.xy, self.xx)

    cdef inline void set_rotation(self, py_float rotation) noexcept:
        cdef py_float scale_x = self.get_scale_x()
        cdef py_float scale_y = self.get_scale_y()
        cdef py_float c = cosl(rotation)
        cdef py_float s = sinl(rotation)
        self.xx = c
        self.xy = s
        self.yx = -s
        self.yy = c
        self.set_scale_x(scale_x)
        self.set_scale_y(scale_y)

    cdef inline py_float get_scale_x(self) noexcept:
        return sqrtl(self.xx * self.xx + self.xy * self.xy)

    cdef inline py_float get_scale_y(self) noexcept:
        cdef py_float det = self._determinant()
        cdef py_float det_sign = 1.0 if det > 0.0 else -1.0 if det < 0.0 else 0.0 if det == 0.0 else NAN
        return sqrtl(self.yx * self.yx + self.yy * self.yy) * det_sign

    cdef inline void set_scale_x(self, py_float value) noexcept:
        cdef py_float m = value / sqrtl(self.xx * self.xx + self.xy * self.xy)
        self.xx *= m
        self.xy *= m

    cdef inline void set_scale_y(self, py_float value) noexcept:
        cdef py_float m = value / sqrtl(self.yx * self.yx + self.yy * self.yy)
        self.yx *= m
        self.yy *= m

    @property
    def rotation(self) -> py_float:
        """Get the rotation angle this transform represents."""
        return self.get_rotation()

    @rotation.setter
    def rotation(self, py_float value) -> None:
        """Set the rotation angle this transform represents.

        See Also: `Transform2D.rotating()`
        """
        self.set_rotation(value)

    # @property
    # def scale(self) -> _T2ScaleProxy:
    #     cdef _T2ScaleProxy proxy = _T2ScaleProxy.__new__(_T2ScaleProxy)
    #     proxy.transform = self
    #     return proxy
    @property
    def scale(self) -> Vec2:
        """Get the scaling transformation this transform represents."""
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.get_scale_x()
        vec.y = self.get_scale_y()
        return vec

    @scale.setter
    def scale(self, Vec2 value) -> None:
        """Set the scaling transformation this transform represents.

        See Also: `Transform2D.scaling()`
        """
        self.set_scale_x(value.x)
        self.set_scale_y(value.y)


    def translate_ip(self, Vec2 translation, /) -> Transform2D:
        #<RETURN_SELF>
        """Apply translation to this transform inplace."""
        self.ox = translation.x
        self.oy = translation.y
        return self

    def translated(self, Vec2 translation, /) -> Transform2D:
        """Apply translation to a copy of this transform."""
        cdef Transform2D t = self.copy()
        t.translate_ip(translation)
        return t

    def rotate_ip(self, py_float rotation, /) -> Transform2D:
        #<RETURN_SELF>
        """Apply rotation to this transform inplace."""
        self.__imatmul__(Transform2D.rotating(rotation))
        return self

    def rotated(self, py_float rotation, /) -> Transform2D:
        """Apply rotation to a copy of this transform."""
        cdef Transform2D t = self.copy()
        t.rotate_ip(rotation)
        return t

    def scale_ip(self, Vec2 scale, /) -> Transform2D:
        #<RETURN_SELF>
        """Apply scaling to this transform inplace."""
        self.xx *= scale.x
        self.xy *= scale.y
        self.yx *= scale.x
        self.yy *= scale.y
        self.ox *= scale.x
        self.oy *= scale.y
        return self

    def scaled(self, Vec2 scale, /) -> Transform2D:
        """Apply scaling to a copy of this transform."""
        cdef Transform2D t = self.copy()
        t.scale_ip(scale)
        return t
#<TEMPLATE_END>