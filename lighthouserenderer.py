from geometry import Point3d, Vector3d, Sphere3d, SphericalCoordinates
from lighthousescreen import LighthouseScreen


class LighthouseRenderer:
    """
    This class combines the screen and the "world model" (i.e. a sphere in this case) and provides a method for the
    above controller class to get a ray casting result.
    """
    __screen: LighthouseScreen
    __sphere: Sphere3d

    def __init__(self):
        origin: Point3d = Point3d(0, 0, 0)
        radius: float = 6.0

        self.__screen = LighthouseScreen()
        self.__sphere = Sphere3d(origin, radius)

    def get_dimensions(self) -> (int, int):
        return self.__screen.get_dimensions()

    def get_screen(self) -> LighthouseScreen:
        return self.__screen

    def cast_parallel_ray_onto_sphere(self, screen_y: int, screen_x: int) -> SphericalCoordinates:
        # print("[DEBUG] screen (x, y) = ({:+.1f}, {:+.1f})".format(screen_x, screen_y))
        ray: Vector3d = self.__screen.get_pixel_based_ray(screen_y, screen_x)
        # print("[DEBUG] ray = base" + str(ray.get_base()) + " -> direction" + str(ray.get_direction()))
        intersection: Point3d = self.__sphere.get_closest_intersect(ray)
        # print("[DEBUG] intersection: " + str(intersection) + " -> " + str(intersection.is_valid()))

        if intersection.is_valid():
            return self.__sphere.get_spherical_coordinates(intersection)
        else:
            return SphericalCoordinates.invalid()

