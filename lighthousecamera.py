from geometry import Point3d, EulerAngles


class LighthouseCamera:
    """
    This class holds information about the camera view port that provides data for the screen rendering.

    Contains a base center point and view direction as well as rotation information.

    Rotation is done using Tait-Bryan notation Euler angles (roll, pitch, yaw)
    """
    __center: Point3d
    __view_direction: Point3d
    __rotation: EulerAngles

    def __init__(self, center: Point3d, view_direction: Point3d = Point3d(0, 0, 1)):
        self.__center = center
        self.__view_direction = view_direction
        self.__rotation = EulerAngles()

    @staticmethod
    def from_xyz(x: float, y: float, z: float) -> "LighthouseCamera":
        return LighthouseCamera(Point3d(x, y, z))

    def get_center(self) -> Point3d:
        return self.__center

    def get_center_in_current_rotation(self) -> Point3d:
        return self.__center.get_tait_bryan_rotated_xyz(self.__rotation)

    def get_view_direction(self) -> Point3d:
        return self.__view_direction

    def get_view_direction_in_current_rotation(self) -> Point3d:
        return self.__view_direction.get_tait_bryan_rotated_xyz(self.__rotation)

    def get_base_point_in_current_rotation(self, point: Point3d) -> Point3d:
        return point.get_tait_bryan_rotated_xyz(self.__rotation)

    def set_rotation_tait_bryan_xyz(self, angles: EulerAngles) -> None:
        self.__rotation = angles
