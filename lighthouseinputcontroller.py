from keyboard import on_press
from geometry import EulerAngles
from lighthousestate import LighthouseState


class LighthouseInputController:
    """
    This class handles the input from the user and modifies the shared state class accordingly.

    NOTE: keyboard input requires sudo privileges on linux.
    """
    __state: LighthouseState
    __next_polar_view_is_north: bool

    def __init__(self, state: LighthouseState):
        self.__state = state
        self.__next_polar_view_is_north = True
        on_press(self.__on_key_press)

    def __on_key_press(self, event) -> None:
        # print("[DEBUG] Key event received: ", event.name)
        match event.name:
            case "esc":
                self.__state.schedule_termination()
            case "+":
                self.__state.change_rotation_rate(+5.0)
            case "-":
                self.__state.change_rotation_rate(-5.0)
            case "space":
                self.__state.toggle_pause()
            case "r":
                self.__state.reset_rotation_angles_to_default()
            case "w":
                self.__state.rotate_around_x_axis(-2.5)
            case "s":
                self.__state.rotate_around_x_axis(+2.5)
            case "a":
                self.__state.rotate_around_y_axis(-2.5)
            case "d":
                self.__state.rotate_around_y_axis(+2.5)
            case "q":
                self.__state.rotate_around_z_axis(+2.5)
            case "e":
                self.__state.rotate_around_z_axis(-2.5)
            case "p":
                # flips Polar view each time p is pressed
                if self.__next_polar_view_is_north:
                    self.__state.set_rotation_angles(EulerAngles(180.0, 0.0, 0.0))
                else:
                    self.__state.set_rotation_angles(EulerAngles(0.0, 0.0, 0.0))
                self.__next_polar_view_is_north = not self.__next_polar_view_is_north
            case _:
                # print("[DEBUG] unhandled key event received: ", event.name)
                pass
