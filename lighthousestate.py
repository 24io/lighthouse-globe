from geometry import EulerAngles


class LighthouseState:
    """
    This class holds the current state of the animated sphere and the animation in general.

    Stores the rotation rate,
    the target frame rate for the Pyghthouse class, the maximum rotation rate that limits changes made to the rotation
    rate.

    Also stores a boolean that can be used to terminate the main function that can be set from any program part
    that holds a reference to the state object used in the main class.

    Finally, the rotation orientation of the camera view port is stored as a EulerAngle object.
    """
    __rotation_rate: float
    __rotation_rate_max: float
    __target_frame_rate: int
    __inverse_target_frame_rate: float
    __paused: bool
    __should_terminate: bool
    __euler_angles_delta: EulerAngles

    def __init__(self, target_frame_rate: int, rotation_rate: float, rotation_rate_max: float):
        self.__rotation_rate = rotation_rate
        self.__rotation_rate_max = rotation_rate_max
        self.__target_frame_rate = target_frame_rate
        self.__inverse_target_frame_rate = 1.0 / target_frame_rate
        self.__paused = False
        self.__should_terminate = False
        self.__euler_angles_delta = EulerAngles()
        self.reset_rotation_angles_to_default()

    def get_rotation_rate(self) -> float:
        return self.__rotation_rate

    def get_rotation_rate_per_frame(self) -> float:
        return self.__rotation_rate * self.__inverse_target_frame_rate  # division is just slow...

    def get_target_frame_rate(self) -> int:
        return self.__target_frame_rate

    def set_rotation_angles(self, angles: EulerAngles) -> None:
        self.__euler_angles_delta = angles

    def get_rotation_angles(self) -> EulerAngles:
        return self.__euler_angles_delta

    def reset_rotation_angles_to_default(self) -> None:
        self.__euler_angles_delta.alpha = 270.0
        self.__euler_angles_delta.beta = 180.0
        self.__euler_angles_delta.gamma = 0

    def change_rotation_rate(self, delta: float) -> None:
        new_rotation_rate: float = self.__rotation_rate + delta
        if abs(new_rotation_rate) <= self.__rotation_rate_max:
            self.__rotation_rate += delta
            print("[INFO] rotation rate is now ", self.__rotation_rate)
        else:
            rotation_sign: float = self.__rotation_rate / abs(self.__rotation_rate)
            print("[WARN] changing rotation rate would exceed limit ", self.__rotation_rate_max * rotation_sign)

    def toggle_pause(self) -> None:
        self.__paused = not self.__paused
        if self.__paused:
            print("[INFO] animation is now paused")
        else:
            print("[INFO] animation is now running")

    def is_paused(self) -> bool:
        return self.__paused

    def schedule_termination(self) -> None:
        self.__should_terminate = True

    def should_terminate(self) -> bool:
        return self.__should_terminate

    def rotate_around_x_axis(self, deg: float) -> None:
        self.__euler_angles_delta.alpha = (self.__euler_angles_delta.alpha + deg) % 360

    def rotate_around_y_axis(self, deg: float) -> None:
        self.__euler_angles_delta.beta = (self.__euler_angles_delta.beta + deg) % 360

    def rotate_around_z_axis(self, deg: float) -> None:
        self.__euler_angles_delta.gamma = (self.__euler_angles_delta.gamma + deg) % 360
