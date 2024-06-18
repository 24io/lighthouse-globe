from math import sqrt, nan, acos, isnan, sin, cos, pi


class EulerAngles:
    alpha: float
    beta: float
    gamma: float

    def __init__(self, alpha: float = 0.0, beta: float = 0.0, gamma: float = 0.0):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def set(self, alpha: float, beta: float, gamma: float) -> None:
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma


class SphericalCoordinates:
    lat: float
    lon: float

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def __str__(self) -> str:
        return "({:+f}, {:+f})".format(self.lat, self.lon)

    @staticmethod
    def invalid():
        return SphericalCoordinates(nan, nan)

    def is_valid(self) -> bool:
        return not (isnan(self.lat) or isnan(self.lon))


class Point3d:
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return "({:.3f}, {:.3f}, {:.3f})".format(self.x, self.y, self.z)

    def __sub__(self, other) -> "Point3d":
        if type(other) != Point3d:
            raise TypeError("Cannot subtract Point3d from " + str(type(other)))
        delta_x = self.x - other.x
        delta_y = self.y - other.y
        delta_z = self.z - other.z

        return Point3d(delta_x, delta_y, delta_z)

    def __add__(self, other) -> "Point3d":
        if type(other) != Point3d:
            raise TypeError("Cannot add Point3d to " + str(type(other)))
        delta_x = self.x + other.x
        delta_y = self.y + other.y
        delta_z = self.z + other.z

        return Point3d(delta_x, delta_y, delta_z)

    def get_scaled(self, scalar: float) -> "Point3d":
        x: float = self.x * scalar
        y: float = self.y * scalar
        z: float = self.z * scalar

        return Point3d(x, y, z)

    def get_normalized(self) -> "Point3d":
        length = self.get_distance_from_origin()

        return self.get_scaled(1 / length)

    def get_distance_from_origin(self):
        return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    def is_valid(self) -> bool:
        return not (isnan(self.x) or isnan(self.y) or isnan(self.z))

    def get_tait_bryan_rotated_xyz(self, rotation: EulerAngles) -> "Point3d":
        """
        Gets the rotated equivalent of this point using euler angles in Tait-Bryan notation.

        :param rotation: Rotation angles in Tait-Bryan notation (roll, pitch, yaw)
        :return: A new Point representing this point rotated with the provided angles around the unit vectors
        """
        alpha: float = ((rotation.alpha / 180) * pi) % (2 * pi)
        beta: float = ((rotation.beta / 180) * pi) % (2 * pi)
        gamma: float = ((rotation.gamma / 180) * pi) % (2 * pi)
        # alpha (1) rotates around z, beta (2) around x', gamma (3) around z'' giving rotation matrix (s=sin, c=cos):
        # (obtained from wiki page for euler angles or by simply multiplying the three unit-vector rotation matrices)
        #                     c_2 c_3           |      - c_2 s_3            |       s_2
        # X_1 Y_2 Z_3 =  c_1 s_3 + c_3 s_1 s_2  |   c_1 c_3 - s_1 s_2 s_3   |   - c_2 s_1
        #                s_1 s_3 - c_1 c_3 s_2  |   c_3 s_1 + c_1 s_2 s_3   |     c_1 c_2
        m_11: float = + cos(beta) * cos(gamma)
        m_12: float = - cos(beta) * sin(gamma)
        m_13: float = + sin(beta)
        m_21: float = + cos(alpha) * sin(gamma) + cos(gamma) * sin(alpha) * sin(beta)
        m_22: float = + cos(alpha) * cos(gamma) - sin(alpha) * sin(beta) * sin(gamma)
        m_23: float = - cos(beta) * sin(alpha)
        m_31: float = + sin(alpha) * sin(gamma) - cos(alpha) * cos(gamma) * sin(beta)
        m_32: float = + cos(gamma) * sin(alpha) + cos(alpha) * sin(beta) * sin(gamma)
        m_33: float = + cos(alpha) * cos(beta)
        # store x, y, z for less self-reference:
        x: float = self.x
        y: float = self.y
        z: float = self.z
        # calculate resulting new x, y, z values
        new_x: float = m_11 * x + m_12 * y + m_13 * z
        new_y: float = m_21 * x + m_22 * y + m_23 * z
        new_z: float = m_31 * x + m_32 * y + m_33 * z

        return Point3d(new_x, new_y, new_z)


class Vector3d:
    __top: Point3d
    __base: Point3d
    __length: float

    def __init__(self, base: Point3d, top: Point3d):
        self.__base = base
        self.__top = top
        self.__recalculate_length()

    @staticmethod
    def create_with_direction(base: Point3d, direction: Point3d) -> "Vector3d":
        return Vector3d(base, base + direction)

    def set_base(self, base: Point3d) -> None:
        self.__base = base
        self.__recalculate_length()

    def get_base(self) -> Point3d:
        return self.__base

    def set_top(self, top: Point3d) -> None:
        self.__top = top
        self.__recalculate_length()

    def get_top(self) -> Point3d:
        return self.__top

    def get_length(self) -> float:
        return self.__length

    def get_direction(self) -> Point3d:
        return (self.__top - self.__base).get_normalized()

    def get_scaled(self, scalar: float) -> "Vector3d":
        new_top: Point3d = self.__base + self.get_direction().get_scaled(scalar)
        return Vector3d(self.__base, new_top)

    def scale(self, scalar: float) -> None:
        self.__top = self.__base + self.get_direction().get_scaled(scalar)
        self.__recalculate_length()

    def normalize(self) -> None:
        self.__top = self.__base + self.get_direction()
        self.__recalculate_length()

    def __recalculate_length(self) -> None:
        # print("[DEBUG] recalculating for:" + str(self.__base) + " -> " + str(self.__top))
        len_x: float = self.__top.x - self.__base.x
        len_y: float = self.__top.y - self.__base.y
        len_z: float = self.__top.z - self.__base.z
        self.__length = sqrt(len_x*len_x + len_y*len_y + len_z*len_z)


class Sphere3d:
    center: Point3d
    radius: float

    def __init__(self, center: Point3d, radius: float):
        self.center = center
        self.radius = radius

    def does_intersect_line(self, line: Vector3d) -> bool:
        return self.get_closest_intersect(line).is_valid()

    def get_closest_intersect(self, line: Vector3d) -> Point3d:
        abc: (float, float, float) = self.__get_abc_intersection_parameters(line)
        a: float = abc[0]
        b: float = abc[1]
        c: float = abc[2]
        d: float = b * b - 4 * a * c
        # print("[DEBUG] discriminant = {:+.2}".format(d))
        if d < 0:
            return Point3d(nan, nan, nan)
        else:
            s1: float = (-b + sqrt(d)) / (2 * a)
            s2: float = (-b - sqrt(d)) / (2 * a)
            t: float = s1 if abs(s1) < abs(s2) else s2  # assumes line origin is always outside sphere
            return line.get_scaled(t).get_top()

    def get_spherical_coordinates(self, point: Point3d) -> SphericalCoordinates:
        rad_to_deg: float = 180 / pi
        p: Point3d = point - self.center
        r: float = p.get_distance_from_origin()
        # print("[DEBUG] radius = {:+f}".format(r))
        if r == 0.0:
            raise ValueError("Radius for point " + str(point) + " is zero! Spherical coordinates are not defined.")

        lat: float
        lon: float

        lat = - (acos(p.z / r) - pi/2) * rad_to_deg
        if lat == +90.0 or lat == -90.0:
            lon = 0.0
        else:
            apparent_radius: float = sqrt(p.x * p.x + p.y * p.y)
            sign_y: float = +1.0 if p.y >= 0 else -1.0
            lon = sign_y * acos(p.x / apparent_radius) * rad_to_deg

        return SphericalCoordinates(lat, lon)

    def __get_abc_intersection_parameters(self, line: Vector3d) -> (float, float, float):
        # the formula for hull of sphere with radius r and origin at (0, 0, 0):
        #   x*x + y*y + z*z - r*r == 0
        # together with the formula for a line:
        #   base + direction * t - point == (0, 0, 0)
        # can be written as quadratic equation for t, since all other values are known.
        # dx, dy, dz are coordinates of direction vector while bx, by ,bz are coordinates of base point:
        #   a*t^2 + 2*b*t + c == 0
        # with:
        #   a = dx*dx + dy*dy + dz*dz
        #   b = bx*dx + by*dy + bz*dz
        #   c = bx*bx + by*by + bz*bz - r*r
        # using the abc-formula we get as discriminant (b^2 - 4ac), which we test for the sign.
        r: float = self.radius
        # base needs to be transformed (only a xyz-shift) so the coordinate system has the sphere at its center:
        bx: float = line.get_base().x - self.center.x
        by: float = line.get_base().y - self.center.y
        bz: float = line.get_base().z - self.center.z
        # print("[DEBUG] bx = {:+.3f} by = {:+.3f} bz = {:+.3f}".format(bx, by, bz))
        # normalized direction is used:
        dx: float = line.get_direction().x
        dy: float = line.get_direction().y
        dz: float = line.get_direction().z
        # print("[DEBUG] dx = {:+.3f} dy = {:+.3f} dz = {:+.3f}".format(dx, dy, dz))
        # calculate intersection parameters:
        a: float = (dx*dx + dy*dy + dz*dz)
        b: float = (bx*dx + by*dy + bz*dz) * 2
        c: float = (bx*bx + by*by + bz*bz - r*r)
        # print("[DEBUG]  a = {:+.3f}  b = {:+.3f}  c = {:+.3f}".format(a, b, c))

        return a, b, c
