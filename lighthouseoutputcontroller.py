from login import username, token
from pyghthouse import Pyghthouse

from geometry import SphericalCoordinates
from lighthousemap import LighthouseMap
from lighthousestate import LighthouseState
from lighthousecamera import LighthouseCamera
from lighthouserenderer import LighthouseRenderer


class LighthouseOutputController:
    """
    This class handles all the output generating classes as well as sending the output to the Pyghthouse api.

    Image creating is done in the rendering class using data held in the map class. This can in future easily be
    modified to hold a list of maps and swapping between them via a map index held by the state class.
    """
    __pyg: Pyghthouse
    __rdr: LighthouseRenderer
    __map: LighthouseMap
    __state: LighthouseState
    __rotation: float

    def __init__(self, state: LighthouseState, file_name: str, max_interpolation_range: int):
        # Values for username and token must be provided in login.py
        self.__rotation = 0
        self.__state = state

        target_frame_rate: int = self.__state.get_target_frame_rate()
        self.__pyg = Pyghthouse(username, token, image_callback=self.draw_next_frame, frame_rate=target_frame_rate)
        self.__rdr = LighthouseRenderer()

        self.__map = LighthouseMap()
        self.__map.load_image(file_name)
        self.__map.set_maximum_interpolation_range(max_interpolation_range)

    def __del__(self):
        self.disconnect()

    def __get_camera_of_renderer(self) -> LighthouseCamera:
        return self.__rdr.get_screen().get_camera()

    def __cast_rays(self) -> None:
        dim_yx: (int, int) = self.__rdr.get_dimensions()
        for y in range(dim_yx[0]):
            for x in range(dim_yx[1]):
                sph_coords: SphericalCoordinates = self.__rdr.cast_parallel_ray_onto_sphere(y, x)
                # print("[DEBUG] sph_coords = " + str(sph_coords))
                if sph_coords.is_valid():
                    lat_rot: float = sph_coords.lat
                    lon_rot: float = ((sph_coords.lon + 180 + round(self.__rotation)) % 360) - 180
                    # print("[DEBUG] (x_sph, y_sph) = ({:+f}, {:+f})".format(lat_rot, lon_rot))
                    rgb: (int, int, int) = self.__map.get_color_from_coordinate(lat_rot, lon_rot)
                    self.__rdr.get_screen().get_current_back_frame().set_color(y, x, rgb)
                else:
                    self.__rdr.get_screen().get_current_back_frame().set_color(y, x, (0, 0, 0))

    def reconnect(self) -> None:
        self.__pyg.connect()

    def disconnect(self) -> None:
        self.__pyg.stop()
        self.__pyg.close()

    def start_frame_rendering(self) -> None:
        self.__pyg.start()

    def stop_frame_rendering(self) -> None:
        self.__pyg.stop()

    def draw_next_frame(self) -> list[list[list[int]]]:
        self.__update_next_frame()  # could in future be run in a separate thread that works on the back frame
        # print("[DEBUG] rot={:6.2f} img=".format(self.__rotation), self.__scr.get_current_front_frame().get())
        return self.__rdr.get_screen().get_current_front_frame().get()

    def __update_next_frame(self) -> None:
        if not self.__state.is_paused():
            self.__rotation += self.__state.get_rotation_rate_per_frame()
        self.__get_camera_of_renderer().set_rotation_tait_bryan_xyz(self.__state.get_rotation_angles())
        self.__cast_rays()
        self.__rdr.get_screen().swap_frame_buffer()


