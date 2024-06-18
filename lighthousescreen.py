from geometry import Point3d, Vector3d
from lighthouseimage import LighthouseImage
from lighthousecamera import LighthouseCamera


class LighthouseScreen:
    """
    This class holds the LighthouseImage objects that are filled with data by the renderer. The working frame is in the
    back while the reading frame is in the front. In this way, the front frame can be sent to the screen in the same
    time when the back frame is still written to. Not really relevant in this case since frame draw time is low.

    The class also stores some data about the screen dimension and resolution and a switch (bool) for the front frame.
    """
    __frame_a: LighthouseImage
    __frame_b: LighthouseImage
    __cam: LighthouseCamera
    __dim_x: int
    __res_x: float
    __dim_y: int
    __res_y: float
    __frame_a_is_front: bool

    def __init__(self, dim_y: int = 14, res_y: float = 1.0, dim_x: int = 28, res_x: float = 0.5):
        LighthouseScreen.__validate_dimensions(dim_y, dim_x)
        self.__dim_x = dim_x
        self.__res_x = res_x
        self.__dim_y = dim_y
        self.__res_y = res_y

        cam_x: float = -0.5 * (dim_x - 1) * res_x
        cam_y: float = -0.5 * (dim_y - 1) * res_y
        cam_z: float = -10.0
        self.__cam = LighthouseCamera(Point3d(cam_x, cam_y, cam_z))

        self.__frame_a = LighthouseImage(dim_y, dim_x)
        self.__frame_b = LighthouseImage(dim_y, dim_x)
        self.__frame_a_is_front = True

    def get_camera(self) -> LighthouseCamera:
        return self.__cam

    def get_dimensions(self) -> (int, int):
        return self.__dim_y, self.__dim_x

    def get_current_front_frame(self) -> LighthouseImage:
        return self.__frame_a if self.__frame_a_is_front else self.__frame_b

    def get_current_back_frame(self) -> LighthouseImage:
        return self.__frame_a if not self.__frame_a_is_front else self.__frame_b

    def get_pixel_based_ray(self, screen_y: int, screen_x: int) -> Vector3d:
        x: float = screen_x * self.__res_x
        y: float = screen_y * self.__res_y
        pixel_offset: Point3d = Point3d(x, y, 0) + self.__cam.get_center()
        pixel: Point3d = self.__cam.get_base_point_in_current_rotation(pixel_offset)
        view_direction: Point3d = self.__cam.get_view_direction_in_current_rotation()
        # print("[DEBUG] screen({:+.2f}, {:+.2f}) -> ray[".format(x, y) + str(pixel) + ", " + str(view_direction) + "]")

        return Vector3d.create_with_direction(pixel, view_direction)

    @staticmethod
    def get_supported_dimensions() -> list[(int, int)]:
        supported_dimensions: list[(int, int)] = [(14, 28)]
        return supported_dimensions

    def swap_frame_buffer(self) -> None:
        self.__frame_a_is_front = not self.__frame_a_is_front

    def set_color(self, y: int, x: int, rgb: (int, int, int)) -> None:
        frame: LighthouseImage = self.get_current_back_frame()
        frame.set_color(y, x, rgb)

    @staticmethod
    def __validate_dimensions(dim_y: int, dim_x: int) -> None:
        dimensions: (int, int) = (dim_y, dim_x)
        supported_dimensions: list[(int, int)] = LighthouseScreen.get_supported_dimensions()
        if dimensions not in supported_dimensions:
            error_str_part1: str = "Dimensions ({:d}, {:d}) currently not supported. ".format(dim_y, dim_x)
            error_str_part2: str = "Currently supported resolutions are: " + str(supported_dimensions)
            raise ValueError(error_str_part1 + error_str_part2)
