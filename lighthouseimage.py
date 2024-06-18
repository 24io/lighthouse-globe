from numpy import zeros


class LighthouseImage:
    """
    This class is essentially a wrapper for the image format used by the Pyghthouse api.
    """
    __image: list[list[list[int]]]
    __dim_x: int
    __dim_y: int

    def __init__(self, dim_y: int, dim_x: int):
        self.__dim_y = dim_y
        self.__dim_x = dim_x
        self.clear()

    def set_color(self, y: int, x: int, rgb: (int, int, int)) -> None:
        self.__image[y][x] = rgb

    def get_color(self, y: int, x: int) -> (int, int, int):
        return self.__image[y][x]

    def clear(self):
        self.__image = (list(list(zeros((self.__dim_y, self.__dim_x, 3)))))

    def get(self) -> list[list[list[int]]]:
        return self.__image
