cimport cython

cdef class Vec3:
    cdef py_float x, y, z


#<TEMPLATE_BEGIN>
from libc.math cimport sinl, cosl


@cython.auto_pickle(True)
@cython.freelist(1024)
@cython.no_gc
@cython.final
cdef class Transform3D:
    cdef py_float xx, xy, xz
    cdef py_float yx, yy, yz
    cdef py_float zx, zy, zz
    cdef py_float ox, oy, oz

    cdef inline void identity(self) noexcept:
        self.xx, self.xy, self.xz = 1.0, 0.0, 0.0
        self.yx, self.yy, self.yz = 0.0, 1.0, 0.0
        self.zx, self.zy, self.zz = 0.0, 0.0, 1.0
        self.ox = self.oy = self.oz = 0.0

    #<OVERLOAD>
    cdef void __init__(self) noexcept:
        self.identity()

    #<OVERLOAD>
    cdef void __init__(self, py_float xx, py_float xy, py_float xz, py_float yx, py_float yy, py_float yz, py_float zx, py_float zy, py_float zz, py_float ox, py_float oy, py_float oz) noexcept:
        self.xx = xx
        self.xy = xy
        self.xz = xz
        self.yx = yx
        self.yy = yy
        self.yz = yz
        self.zx = zx
        self.zy = zy
        self.zz = zz
        self.ox = ox
        self.oy = oy
        self.oz = oz

    #<OVERLOAD>
    cdef void __init__(self, Vec3 x, Vec3 y, Vec3 z, Vec3 origin) noexcept:
        self.xx, self.xy, self.xz = x.x, x.y, x.z
        self.yx, self.yy, self.yz = y.x, y.y, y.z
        self.zx, self.zy, self.zz = z.x, z.y, z.z
        self.ox, self.oy, self.oz = origin.x, origin.y, origin.z

    #<OVERLOAD>
    cdef void __init__(self, Transform3D transform) noexcept:
        self.xx = transform.xx
        self.xy = transform.xy
        self.xz = transform.xz
        self.yx = transform.yx
        self.yy = transform.yy
        self.yz = transform.yz
        self.zx = transform.zx
        self.zy = transform.zy
        self.zz = transform.zz
        self.ox = transform.ox
        self.oy = transform.oy
        self.oz = transform.oz

    #<OVERLOAD_DISPATCHER>:__init__

    @staticmethod
    def translating(Vec3 translation, /) -> Transform3D:
        cdef Transform3D t = Transform3D.__new__(Transform3D)
        t.identity()
        t.ox += translation.x
        t.oy += translation.y
        t.oz += translation.z
        return t

    @staticmethod
    def rotating(Vec3 axis, py_float angle, /, Vec3 origin = None) -> Transform3D:
        cdef Transform3D trans = Transform3D.__new__(Transform3D)

        cdef py_float axis_x_sq = axis.x * axis.x
        cdef py_float axis_y_sq = axis.y * axis.y
        cdef py_float axis_z_sq = axis.z * axis.z
        cdef py_float c = cosl(angle)

        trans.xx = axis_x_sq + c * (1.0 - axis_x_sq)
        trans.yy = axis_y_sq + c * (1.0 - axis_y_sq)
        trans.zz = axis_z_sq + c * (1.0 - axis_z_sq)

        cdef py_float s = sinl(angle)
        cdef t = 1.0 - c

        cdef xyzt = axis.x * axis.y * t
        cdef zyxs = axis.z * s
        trans.yx = xyzt - zyxs
        trans.xy = xyzt + zyxs

        xyzt = axis.x * axis.z * t
        zyxs = axis.y * s
        trans.zx = xyzt + zyxs
        trans.xz = xyzt - zyxs

        xyzt = axis.y * axis.z * t
        zyxs = axis.x * s
        trans.zy = xyzt - zyxs
        trans.yz = xyzt + zyxs

        if origin is not None:
            trans.ox = origin.x
            trans.oy = origin.y
            trans.oz = origin.z

        return trans

    @staticmethod
    def scaling(Vec3 scale, /, Vec3 origin = None) -> Transform3D:
        cdef Transform3D t = Transform3D.__new__(Transform3D)
        t.identity()
        t.xx = scale.x
        t.yy = scale.y
        t.zz = scale.z

        if origin is not None:
            t.ox = origin.x
            t.oy = origin.y
            t.oz = origin.z

        return t

    cdef inline Transform3D copy(self):
        cdef Transform3D t = Transform3D.__new__(Transform3D)
        t.xx = self.xx
        t.xy = self.xy
        t.xz = self.xz
        t.yx = self.yx
        t.yy = self.yy
        t.yz = self.yz
        t.zx = self.zx
        t.zy = self.zy
        t.zz = self.zz
        t.ox = self.ox
        t.oy = self.oy
        t.oz = self.oz
        return t
    
    def __repr__(self) -> str:
        return f"⎡X: ({self.xx}, {self.xy}, {self.xz})\n⎢Y: ({self.yx}, {self.yy}, {self.yz})\n⎢Z: ({self.zx}, {self.zy}, {self.zz})\n⎣O: ({self.ox}, {self.oy}, {self.oz})"

    def __eq__(self, object other) -> bool:
        if not isinstance(other, Transform3D):
            return False
        return self.xx == (<Transform3D> other).xx and self.xy == (<Transform3D> other).xy and self.xz == (<Transform3D> other).xz and\
               self.yx == (<Transform3D> other).yx and self.yy == (<Transform3D> other).yy and self.yz == (<Transform3D> other).yz and\
               self.zx == (<Transform3D> other).zx and self.zy == (<Transform3D> other).zy and self.zz == (<Transform3D> other).zz and\
               self.ox == (<Transform3D> other).ox and self.oy == (<Transform3D> other).oy and self.oz == (<Transform3D> other).oz

    def __ne__(self, object other) -> bool:
        if not isinstance(other, Transform3D):
            return True
        return self.xx != (<Transform3D> other).xx or self.xy != (<Transform3D> other).xy or self.xz != (<Transform3D> other).xz or\
               self.yx != (<Transform3D> other).yx or self.yy != (<Transform3D> other).yy or self.yz != (<Transform3D> other).yz or\
               self.zx != (<Transform3D> other).zx or self.zy != (<Transform3D> other).zy or self.zz != (<Transform3D> other).zz or\
               self.ox != (<Transform3D> other).ox or self.oy != (<Transform3D> other).oy or self.oz != (<Transform3D> other).oz

    def is_close(self, Transform3D other, /, py_float rel_tol = DEFAULT_RELATIVE_TOLERANCE, py_float abs_tol = DEFAULT_ABSOLUTE_TOLERANCE) -> bool:
        return is_close(self.xx, other.xx, rel_tol, abs_tol) and \
               is_close(self.xy, other.xy, rel_tol, abs_tol) and \
               is_close(self.xz, other.xz, rel_tol, abs_tol) and \
               is_close(self.yx, other.yx, rel_tol, abs_tol) and \
               is_close(self.yy, other.yy, rel_tol, abs_tol) and \
               is_close(self.yz, other.yz, rel_tol, abs_tol) and \
               is_close(self.zx, other.zx, rel_tol, abs_tol) and \
               is_close(self.zy, other.zy, rel_tol, abs_tol) and \
               is_close(self.zz, other.zz, rel_tol, abs_tol) and \
               is_close(self.ox, other.ox, rel_tol, abs_tol) and \
               is_close(self.oy, other.oy, rel_tol, abs_tol) and \
               is_close(self.oz, other.oz, rel_tol, abs_tol)

    #TODO: Better hashing
    def __hash__(self) -> py_int:
        cdef py_int h = 0
        h ^= bitcast_float(self.xx)
        h ^= rotl_ratio(bitcast_float(self.xy), 1, 12)
        h ^= rotl_ratio(bitcast_float(self.xz), 2, 12)
        h ^= rotl_ratio(bitcast_float(self.yx), 3, 12)
        h ^= rotl_ratio(bitcast_float(self.yy), 4, 12)
        h ^= rotl_ratio(bitcast_float(self.yz), 5, 12)
        h ^= rotl_ratio(bitcast_float(self.zx), 6, 12)
        h ^= rotl_ratio(bitcast_float(self.zy), 7, 12)
        h ^= rotl_ratio(bitcast_float(self.zz), 8, 12)
        h ^= rotl_ratio(bitcast_float(self.ox), 9, 12)
        h ^= rotl_ratio(bitcast_float(self.oy), 10, 12)
        h ^= rotl_ratio(bitcast_float(self.oz), 11, 12)
        return h

    @property
    def x(self) -> Vec3:
        cdef Vec3 vec = Vec3.__new__(Vec3)
        vec.x = self.xx
        vec.y = self.xy
        vec.z = self.xz
        return vec

    @property
    def y(self) -> Vec3:
        cdef Vec3 vec = Vec3.__new__(Vec3)
        vec.x = self.yx
        vec.y = self.yy
        vec.z = self.yz
        return vec

    @property
    def z(self) -> Vec3:
        cdef Vec3 vec = Vec3.__new__(Vec3)
        vec.x = self.zx
        vec.y = self.zy
        vec.z = self.zz
        return vec

    @property
    def origin(self) -> Vec3:
        cdef Vec3 vec = Vec3.__new__(Vec3)
        vec.x = self.ox
        vec.y = self.oy
        vec.z = self.oz
        return vec

    @x.setter
    def x(self, Vec3 value) -> None:
        self.xx = value.x
        self.xy = value.y
        self.xz = value.z

    @y.setter
    def y(self, Vec3 value) -> None:
        self.yx = value.x
        self.yy = value.y
        self.yz = value.z

    @z.setter
    def z(self, Vec3 value) -> None:
        self.zx = value.x
        self.zy = value.y
        self.zz = value.z

    @origin.setter
    def origin(self, Vec3 value) -> None:
        self.ox = value.x
        self.oy = value.y
        self.oz = value.z

    def __getitem__(self, py_int item) -> Vec3:
        cdef vec = Vec3.__new__(Vec3)

        if item == 0:
            vec.x = self.xx
            vec.y = self.xy
            vec.z = self.xz
        elif item == 1:
            vec.x = self.yx
            vec.y = self.yy
            vec.z = self.yz
        elif item == 2:
            vec.x = self.zx
            vec.y = self.zy
            vec.z = self.zz
        elif item == 3:
            vec.x = self.ox
            vec.y = self.oy
            vec.z = self.oz
        else:
            raise IndexError(item)

        return vec

    def __setitem__(self, py_int key, Vec3 value) -> None:
        if key == 0:
            self.xx = value.x
            self.xy = value.y
            self.xz = value.z
        elif key == 1:
            self.yx = value.x
            self.yy = value.y
            self.yz = value.z
        elif key == 2:
            self.zx = value.x
            self.zy = value.y
            self.zz = value.z
        elif key == 3:
            self.ox = value.x
            self.oy = value.y
            self.oz = value.z
        else:
            raise IndexError(key)

    def __len__(self) -> py_int:
        return 4

    cdef inline py_float tdotx(self, py_float x, py_float y, py_float z) noexcept:
        return x * self.xx + y * self.yx + z * self.zx

    cdef inline py_float mulx(self, py_float x, py_float y, py_float z) noexcept:
        return self.tdotx(x, y, z) + self.ox

    cdef inline py_float tdoty(self, py_float x, py_float y, py_float z) noexcept:
        return x * self.xy + y * self.yy + z * self.zy

    cdef inline py_float muly(self, py_float x, py_float y, py_float z) noexcept:
        return self.tdoty(x, y, z) + self.oy

    cdef inline py_float tdotz(self, py_float x, py_float y, py_float z) noexcept:
        return x * self.xz + y * self.yz + z * self.zz

    cdef inline py_float mulz(self, py_float x, py_float y, py_float z) noexcept:
        return self.tdotz(x, y, z) + self.oz

    def __mul__(self, Vec3 other) -> Vec3:
        cdef Vec3 vec = Vec3.__new__(Vec3)
        vec.x = self.mulx(other.x, other.y, other.z)
        vec.y = self.muly(other.x, other.y, other.z)
        vec.z = self.mulz(other.x, other.y, other.z)
        return vec

    #<OVERLOAD>
    cdef Vec3 __call__(self, Vec3 other):
        cdef Vec3 vec = Vec3.__new__(Vec3)
        vec.x = self.mulx(other.x, other.y, other.z)
        vec.y = self.muly(other.x, other.y, other.z)
        vec.z = self.mulz(other.x, other.y, other.z)
        return vec

    #<OVERLOAD>
    cdef Transform3D __call__(self, Transform3D other):
        cdef Transform3D t = Transform3D.__new__(Transform3D)
        t.xx = self.tdotx(other.xx, other.xy, other.xz)
        t.xy = self.tdoty(other.xx, other.xy, other.xz)
        t.xz = self.tdotz(other.xx, other.xy, other.xz)
        t.yx = self.tdotx(other.yx, other.yy, other.yz)
        t.yy = self.tdoty(other.yx, other.yy, other.yz)
        t.yz = self.tdotz(other.yx, other.yy, other.yz)
        t.zx = self.tdotx(other.zx, other.zy, other.zz)
        t.zy = self.tdoty(other.zx, other.zy, other.zz)
        t.zz = self.tdotz(other.zx, other.zy, other.zz)
        t.ox = self.mulx(other.ox, other.oy, other.oz)
        t.oy = self.muly(other.ox, other.oy, other.oz)
        t.oz = self.mulz(other.ox, other.oy, other.oz)
        return t

    #<OVERLOAD_DISPATCHER>:__call__

    def __matmul__(self, Transform3D other) -> Transform3D:
        cdef Transform3D t = Transform3D.__new__(Transform3D)
        t.xx = self.tdotx(other.xx, other.xy, other.xz)
        t.xy = self.tdoty(other.xx, other.xy, other.xz)
        t.xz = self.tdotz(other.xx, other.xy, other.xz)
        t.yx = self.tdotx(other.yx, other.yy, other.yz)
        t.yy = self.tdoty(other.yx, other.yy, other.yz)
        t.yz = self.tdotz(other.yx, other.yy, other.yz)
        t.zx = self.tdotx(other.zx, other.zy, other.zz)
        t.zy = self.tdoty(other.zx, other.zy, other.zz)
        t.zz = self.tdotz(other.zx, other.zy, other.zz)
        t.ox = self.mulx(other.ox, other.oy, other.oz)
        t.oy = self.muly(other.ox, other.oy, other.oz)
        t.oz = self.mulz(other.ox, other.oy, other.oz)
        return t

    def __imatmul__(self, Transform3D other) -> Transform3D:
        cdef py_float xx = other.tdotx(self.xx, self.xy, self.xz)
        cdef py_float xy = other.tdoty(self.xx, self.xy, self.xz)
        cdef py_float xz = other.tdotz(self.xx, self.xy, self.xz)
        cdef py_float yx = other.tdotx(self.yx, self.yy, self.yz)
        cdef py_float yy = other.tdoty(self.yx, self.yy, self.yz)
        cdef py_float yz = other.tdotz(self.yx, self.yy, self.yz)
        cdef py_float zx = other.tdotx(self.zx, self.zy, self.zz)
        cdef py_float zy = other.tdoty(self.zx, self.zy, self.zz)
        cdef py_float zz = other.tdotz(self.zx, self.zy, self.zz)
        cdef py_float ox = other.mulx(self.ox, self.oy, self.oz)
        cdef py_float oy = other.muly(self.ox, self.oy, self.oz)
        cdef py_float oz = other.mulz(self.ox, self.oy, self.oz)
        self.xx, self.xy, self.xz = xx, xy, xz
        self.yx, self.yy, self.yz = yx, yy, yz
        self.zx, self.zy, self.zz = zx, zy, zz
        self.ox, self.oy, self.oz = ox, oy, oz
        return self

    cdef inline py_float _determinant(self) noexcept:
        return (self.xx * (self.yy * self.zz - self.yz * self.zy) -
                self.yx * (self.xy * self.zz - self.xz * self.zy) +
                self.zx * (self.xy * self.yz - self.yy * self.xz))

    @property
    def determinant(self) -> py_float:
        return self._determinant()

    def __invert__(self) -> Transform3D:
        cdef py_float cox = self.yy * self.zz - self.yz * self.zy
        cdef py_float coy = self.xz * self.zy - self.xy * self.zz
        cdef py_float coz = self.xy * self.yz - self.yy * self.xz
        cdef py_float det = self.xx * cox + self.yx * coy + self.zx * coz
        cdef py_float i_det = 1.0 / det

        cdef Transform3D t = Transform3D.__new__(Transform3D)
        t.xx = cox * i_det
        t.xy = coy * i_det
        t.xz = coz * i_det
        t.yx = (self.zx * self.yz - self.yx * self.zz) * i_det
        t.yy = (self.xx * self.zz - self.zx * self.xz) * i_det
        t.yz = (self.yx * self.xz - self.xx * self.yz) * i_det
        t.zx = (self.yx * self.zy - self.zx * self.yy) * i_det
        t.zy = (self.zx * self.xy - self.xx * self.zy) * i_det
        t.zz = (self.xx * self.yy - self.yx * self.xy) * i_det
        t.ox = -t.tdotx(self.ox, self.oy, self.oz)
        t.oy = -t.tdoty(self.ox, self.oy, self.oz)
        t.oz = -t.tdotz(self.ox, self.oy, self.oz)
        return t

    def translate_ip(self, Vec3 translation, /) -> Transform3D:
        self.ox += translation.x
        self.oy += translation.y
        self.oz += translation.z
        return self

    def translated(self, Vec3 translation, /) -> Transform3D:
        cdef Transform3D t = self.copy()
        t.translate_ip(translation)
        return t

    def rotate_ip(self, Vec3 axis, py_float angle, /) -> Transform3D:
        self.__imatmul__(Transform3D.rotating(axis, angle))
        return self

    def rotated(self, Vec3 axis, py_float angle, /) -> Transform3D:
        cdef Transform3D t = self.copy()
        t.rotate_ip(axis, angle)
        return t

    def scale_ip(self, Vec3 scale, /) -> Transform3D:
        self.xx *= scale.x
        self.yx *= scale.x
        self.zx *= scale.x
        self.xy *= scale.y
        self.yy *= scale.y
        self.zy *= scale.y
        self.xz *= scale.z
        self.yz *= scale.z
        self.zz *= scale.z
        return self

    def scaled(self, Vec3 scale, /) -> Transform3D:
        cdef Transform3D t = self.copy()
        t.scale_ip(scale)
        return t
#<TEMPLATE_END>