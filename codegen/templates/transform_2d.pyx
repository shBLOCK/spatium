cimport cython

cdef class Vec2:
    cdef double x, y


#<TEMPLATE_BEGIN>
from libc.math cimport atan2, sin, cos, sqrt, NAN


@cython.auto_pickle(True)
@cython.freelist(1024)
@cython.no_gc
@cython.final
cdef class Transform2D:
    cdef double xx, xy
    cdef double yx, yy
    cdef double ox, oy


    cdef inline void identity(self) noexcept:
        self.xx, self.xy = 1.0, 0.0
        self.yx, self.yy = 0.0, 1.0
        self.ox = self.oy = 0.0

    #<OVERLOAD>
    cdef void __init__(self) noexcept:
        self.identity()

    #<OVERLOAD>
    cdef void __init__(self, double xx, double xy, double yx, double yy, double ox, double oy) noexcept:
        self.xx = xx
        self.xy = xy
        self.yx = yx
        self.yy = yy
        self.ox = ox
        self.oy = oy

    #<OVERLOAD>
    cdef void __init__(self, Vec2 x, Vec2 y, Vec2 origin) noexcept:
        self.xx, self.xy = x.x, x.y
        self.yx, self.yy = y.x, y.y
        self.ox, self.oy = origin.x, origin.y

    #<OVERLOAD>
    cdef void __init__(self, Transform2D transform) noexcept:
        self.xx = transform.xx
        self.xy = transform.xy
        self.yx = transform.yx
        self.yy = transform.yy
        self.ox = transform.ox
        self.oy = transform.oy

    #<OVERLOAD_DISPATCHER>:__init__

    @staticmethod
    def translating(Vec2 translation) -> Transform2D:
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.identity()
        t.ox, t.oy = translation.x, translation.y
        return t

    @staticmethod
    def rotating(float rotation, Vec2 origin = None) -> Transform2D:
        cdef double c = cos(rotation)
        cdef double s = sin(rotation)
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.xx = c
        t.xy = s
        t.yx = -s
        t.yy = c
        if origin is not None:
            t.ox, t.oy = origin.x, origin.y
        return t

    @staticmethod
    def scaling(Vec2 scale, Vec2 origin = None) -> Transform2D:
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.xx = scale.x
        t.yy = scale.y
        if origin is not None:
            t.ox, t.oy = origin.x, origin.y
        return t

    cdef inline Transform2D copy(self) noexcept:
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
        if not isinstance(other, Transform2D):
            return False
        return self.xx == (<Transform2D> other).xx and self.xy == (<Transform2D> other).xy and\
               self.yx == (<Transform2D> other).yx and self.yy == (<Transform2D> other).yy and\
               self.ox == (<Transform2D> other).ox and self.oy == (<Transform2D> other).oy

    def __ne__(self, object other) -> bool:
        if not isinstance(other, Transform2D):
            return True
        return self.xx != (<Transform2D> other).xx or self.xy != (<Transform2D> other).xy or \
               self.yx != (<Transform2D> other).yx or self.yy != (<Transform2D> other).yy or \
               self.ox != (<Transform2D> other).ox or self.oy != (<Transform2D> other).oy

    def is_close(self, Transform2D other, double rel_tol = DEFAULT_RELATIVE_TOLERANCE, double abs_tol = DEFAULT_ABSOLUTE_TOLERANCE) -> bool:
        return is_close(self.xx, other.xx, rel_tol, abs_tol) and \
               is_close(self.xy, other.xy, rel_tol, abs_tol) and \
               is_close(self.yx, other.yx, rel_tol, abs_tol) and \
               is_close(self.yy, other.yy, rel_tol, abs_tol) and \
               is_close(self.ox, other.ox, rel_tol, abs_tol) and \
               is_close(self.oy, other.oy, rel_tol, abs_tol)

    @property
    def x(self) -> Vec2:
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.xx
        vec.y = self.xy
        return vec

    @property
    def y(self) -> Vec2:
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.yx
        vec.y = self.yy
        return vec

    @property
    def origin(self) -> Vec2:
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.ox
        vec.y = self.oy
        return vec

    @x.setter
    def x(self, Vec2 value) -> None:
        self.xx = value.x
        self.xy = value.y

    @y.setter
    def y(self, Vec2 value) -> None:
        self.yx = value.x
        self.yy = value.y

    @origin.setter
    def origin(self, Vec2 value) -> None:
        self.ox = value.x
        self.oy = value.y

    def __getitem__(self, int item) -> Vec2:
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

    def __setitem__(self, int key, Vec2 value) -> None:
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

    def __len__(self) -> int:
        return 3

    cdef inline double tdotx(self, double x, double y) noexcept:
        return x * self.xx + y * self.yx

    cdef inline double mulx(self, double x, double y) noexcept:
        return self.tdotx(x, y) + self.ox

    cdef inline double tdoty(self, double x, double y) noexcept:
        return x * self.xy + y * self.yy

    cdef inline double muly(self, double x, double y) noexcept:
        return self.tdoty(x, y) + self.oy

    def __mul__(self, Vec2 other) -> Vec2:
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.mulx(other.x, other.y)
        vec.y = self.muly(other.x, other.y)
        return vec

    #<OVERLOAD>
    cdef Vec2 __call__(self, Vec2 other) noexcept:
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.mulx(other.x, other.y)
        vec.y = self.muly(other.x, other.y)
        return vec

    #<OVERLOAD>
    cdef Transform2D __call__(self, Transform2D other) noexcept:
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
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.xx = self.tdotx(other.xx, other.xy)
        t.xy = self.tdoty(other.xx, other.xy)
        t.yx = self.tdotx(other.yx, other.yy)
        t.yy = self.tdoty(other.yx, other.yy)
        t.ox = self.mulx(other.ox, other.oy)
        t.oy = self.muly(other.ox, other.oy)
        return t

    def __imatmul__(self, Transform2D other) -> None:
        self.xx = other.tdotx(self.xx, self.xy)
        self.xy = other.tdoty(self.xx, self.xy)
        self.yx = other.tdotx(self.yx, self.yy)
        self.yy = other.tdoty(self.yx, self.yy)
        self.ox = other.mulx(self.ox, self.oy)
        self.oy = other.muly(self.ox, self.oy)

    cdef inline double _determinant(self) noexcept:
        return self.xx * self.yy - self.xy * self.yx

    @property
    def determinant(self) -> float:
        return self._determinant()

    def __invert__(self) -> Transform2D:
        cdef double i_det = 1.0 / self._determinant()
        cdef Transform2D t = Transform2D.__new__(Transform2D)
        t.xx = self.yy * +i_det
        t.xy = self.xy * -i_det
        t.yx = self.yx * -i_det
        t.yy = self.xx * +i_det
        t.ox = -t.tdotx(self.ox, self.oy)
        t.oy = -t.tdoty(self.ox, self.oy)
        return t


    cdef inline double get_rotation(self) noexcept:
        return atan2(self.xy, self.xx)

    cdef inline void set_rotation(self, double rotation) noexcept:
        cdef double scale_x = self.get_scale_x()
        cdef double scale_y = self.get_scale_y()
        cdef double c = cos(rotation)
        cdef double s = sin(rotation)
        self.xx = c
        self.xy = s
        self.yx = -s
        self.yy = c
        self.set_scale_x(scale_x)
        self.set_scale_y(scale_y)

    cdef inline double get_scale_x(self) noexcept:
        return sqrt(self.xx * self.xx + self.xy * self.xy)

    cdef inline double get_scale_y(self) noexcept:
        cdef double det = self._determinant()
        cdef double det_sign = 1.0 if det > 0.0 else -1.0 if det < 0.0 else 0.0 if det == 0.0 else NAN
        return sqrt(self.yx * self.yx + self.yy * self.yy) * det_sign

    cdef inline void set_scale_x(self, double value) noexcept:
        cdef double m = value / sqrt(self.xx * self.xx + self.xy * self.xy)
        self.xx *= m
        self.xy *= m

    cdef inline void set_scale_y(self, double value) noexcept:
        cdef double m = value / sqrt(self.yx * self.yx + self.yy * self.yy)
        self.yx *= m
        self.yy *= m

    @property
    def rotation(self) -> float:
        return self.get_rotation()

    @rotation.setter
    def rotation(self, float value) -> None:
        self.set_rotation(value)

    # @property
    # def scale(self) -> _T2ScaleProxy:
    #     cdef _T2ScaleProxy proxy = _T2ScaleProxy.__new__(_T2ScaleProxy)
    #     proxy.transform = self
    #     return proxy
    @property
    def scale(self) -> Vec2:
        cdef Vec2 vec = Vec2.__new__(Vec2)
        vec.x = self.get_scale_x()
        vec.y = self.get_scale_y()
        return vec

    @scale.setter
    def scale(self, Vec2 value) -> None:
        self.set_scale_x(value.x)
        self.set_scale_y(value.y)


    def translate_ip(self, Vec2 translation) -> Transform2D:
        self.ox = translation.x
        self.oy = translation.y
        return self

    def translated(self, Vec2 translation) -> Transform2D:
        cdef Transform2D t = self.copy()
        t.translate_ip(translation)
        return t

    def rotate_ip(self, float rotation) -> Transform2D:
        self.__imul__(Transform2D.rotation(rotation))
        return self

    def rotated(self, float rotation) -> Transform2D:
        cdef Transform2D t = self.copy()
        t.rotate_ip(rotation)
        return t

    def scale_ip(self, Vec2 scale) -> Transform2D:
        self.xx *= scale.x
        self.xy *= scale.y
        self.yx *= scale.x
        self.yy *= scale.y
        self.ox *= scale.x
        self.oy *= scale.y
        return self

    def scaled(self, Vec2 scale) -> Transform2D:
        cdef Transform2D t = self.copy()
        t.scale_ip(scale)
        return t


# @cython.freelist(16)
# @cython.no_gc
# @cython.final
# cdef class _T2ScaleProxy:
#     cdef Transform2D transform
#
#     @property
#     def x(self) -> float:
#         return self.transform.get_scale_x()
#
#     @property
#     def y(self) -> float:
#         return self.transform.get_scale_y()
#
#     @x.setter
#     def x(self, float value) -> None:
#         self.transform.set_scale_x(value)
#
#     @y.setter
#     def y(self, float value) -> None:
#         self.transform.set_scale_y(value)
#
#     @property
#     def vec(self) -> Vec2:
#         cdef Vec2 vec = Vec2.__new__(Vec2)
#         vec.x = self.transform.get_scale_x()
#         vec.y = self.transform.get_scale_y()
#         return vec
#
#     @vec.setter
#     def vec(self, Vec2 value) -> None:
#         self.transform.set_scale_x(value.x)
#         self.transform.set_scale_y(value.y)
#<TEMPLATE_END>