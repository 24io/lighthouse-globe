from re import match, compile
from math import floor
from numpy import ndarray, zeros
from typing.io import TextIO


class LighthouseMap:
    """
    This class stores the map data that is projected onto the sphere in the renderer. It also handles the loading of a
    pnm file to provide the map data. Currently only supports PNM version P3.
    """
    __map: ndarray
    __dim_x: int
    __dim_y: int
    __res: float
    __max_interp_range: int
    __npm_version: str
    __max_value: int

    def __int__(self):
        self.__dim_x = 0
        self.__dim_y = 0
        self.__res = 0.0
        self.__map = ndarray([])
        self.__max_interp_range = 0

    def load_image(self, file_name: str) -> None:
        file: TextIO = open(file_name, "rt")
        data: list[str] = file.read().splitlines()

        self.__process_and_remove_header(data)
        self.__load_data_to_map(data)

        file.close()

    def set_maximum_interpolation_range(self, max_interp_range: int) -> None:
        self.__max_interp_range = max_interp_range

    def __load_data_to_map(self, raw_pnm_content: list[str]) -> None:
        lat_index: int = 0
        lon_index: int = 0
        rgb_index: int = 0
        counter: int = 0
        for line in raw_pnm_content:
            for entry in line.split():  # support multiple values per line
                self.__map[lat_index][lon_index][rgb_index] = int(entry)

                rgb_index = (rgb_index + 1) % 3
                if rgb_index == 0:
                    lon_index = (lon_index + 1) % self.__dim_x
                    if lon_index == 0:
                        lat_index = lat_index + 1
                counter += 1

            # Debug section (only for 3 color values per line!)
            # rgb: (int, int, int) = self.__map[lat_index][lon_index]
            # xy_str: str = "({:3d} x{:3d})".format(lat_index, lon_index)
            # rgb_str: str = "[{:3d}, {:3d}, {:3d}]".format(rgb[0], rgb[1], rgb[2])
            # print("[DEBUG] ", xy_str, " --> ", rgb_str)

        print("[DEBUG] processed {:d} colors".format(counter))

    def __process_and_remove_header(self, raw_pnm_content: list[str]):
        read_version: bool = False
        read_dimension: bool = False
        read_header: bool = False  # implies read_max_value

        while not read_header:
            line: str = raw_pnm_content.pop(0)

            if line.lstrip()[0] == "#":
                print("[DEBUG] skipped a comment during file import.")
                pass  # skip comment lines
            elif not read_version:
                self.__validate_and_set_file_version(line)
                read_version = True
            elif not read_dimension:
                self.__validate_and_set_dimensions(line)
                read_dimension = True
            else:
                self.__validate_and_set_max_color_value(line)
                read_header = True

        return

    def __validate_and_set_max_color_value(self, line: str):
        valid_color_limits = [15, 255]
        if int(line) not in valid_color_limits:
            raise ValueError("Maximum color value must be in " + str(valid_color_limits))
        else:
            self.__max_value = int(line)

    def __validate_and_set_file_version(self, line: str):
        if line.strip() == "P3":
            self.__npm_version = "P3"
            # print("DEBUG: PNM version: ", raw_pnm_content[0])
        else:
            raise ValueError("Input format must be PNM in version P3!")

    def __validate_and_set_dimensions(self, line: str):
        line_trimmed: str = line.strip()
        if not match(compile(r"[0-9]+?\s[0-9]+?"), line_trimmed):
            raise ValueError("Input format error while determining dimension!")
        else:
            line_split: (str, str) = line_trimmed.split()
            x: int = int(line_split[0])
            y: int = int(line_split[1])
            # if y != (2 * x):
            #     raise ValueError("Size y must be two times size x!")
            # elif not (x in range(28, 361)) and (y in range(14,181)):
            if not (x in range(28, 361)) and (y in range(14, 181)):
                raise ValueError("Maps size exceed limits (14 <= y <= 18, 28 <= x <= 360)!")
            else:
                self.__dim_x = x
                self.__dim_y = y
                self.__res = 180.0 / y  # == 360 / x
                self.__map = zeros((self.__dim_y, self.__dim_x, 3), dtype=int)
                self.__max_interp_range = x  # higher interpolation is useless (wraps around for same values)
                print("[DEBUG] map dimensions: (x = {:3d}, y = {:3d})".format(x, y))

    def get_color_from_coordinate(self, lat: float, lon: float) -> (int, int, int):
        if not ((lat >= -90) and (lat <= 90)):
            raise ValueError("Latitude must be in range [-90, 90]!")
        if not ((lon >= -180) and (lon <= 180)):
            raise ValueError("Latitude must be in range [-180, 180]!")

        # interpolation radius is determined from resolution, value is rounded since pixel coordinates are also indices.
        # resolution of Pyghthouse image is 180/14 == 360/28 which is the target value after interpolation (ca. 12,86).
        delta: int = floor((180/14) / self.__res)  # range for interpolation
        if delta > self.__max_interp_range:
            delta = self.__max_interp_range  # maximum range for interpolation

        r: int = 0
        g: int = 0
        b: int = 0

        # resolution stores the degrees per pixel in the map -> use to calculate transformation:
        #   coordinates:
        #        map pixels      map-oriented pseudo-spherical    global spherical
        #                                   0       360           -180   0   180
        #           0   x_dim             0 x x x x x                x x x x x   90
        #         0 x x x                   x x x x x                x x x x x
        #           x x x       <----       x x x x x      <----     x x x x x   0
        #     y_dim x x x                   x x x x x                x x x x x
        #                               180 x x x x x                x x x x x  -90

        # lat/lon start in global spherical coordinates

        # normalize lat/lon to be positive and also flip lat so the North Pole is at 0
        lat = 90.0 - lat
        lon = 180.0 + lon

        # lat/lon are now in map-oriented pseudo-spherical coordinates, transform to map pixels via resolution.
        x: int = int(round(lon / self.__res))
        y: int = int(round(lat / self.__res))

        # scale values to map pixels, interpolate with range depending on resolution.
        interp_range_x: range = range(x - delta, x + delta + 1)
        interp_range_y: range = range(y - delta, y + delta + 1)
        interp_num: int = (len(interp_range_x) * len(interp_range_y))
        for i_y in interp_range_y:
            for i_x in interp_range_x:
                # if i_y is less than 0 or greater dim_y, simply roll value over the pole
                if i_y < 0:
                    i_x = round((i_x + (self.__dim_x / 2)) % self.__dim_x)
                    i_y = i_y * (-1)
                elif i_y >= self.__dim_y:
                    i_x = round((i_x + (self.__dim_x / 2)) % self.__dim_x)
                    i_y = self.__dim_y - (i_y % self.__dim_y) - 1
                # if i_x is less than 0 or greater dim_x, simply roll value over the day change meridian
                if i_x < 0:
                    i_x = i_x + 360
                elif i_x >= self.__dim_x:
                    i_x = i_x - 360

                rgb = self.__map[i_y][i_x]
                r += rgb[0]
                g += rgb[1]
                b += rgb[2]

        r = round(r / interp_num)
        g = round(g / interp_num)
        b = round(b / interp_num)

        return r, g, b
