from time import sleep, time
from datetime import datetime
from lighthousestate import LighthouseState
from lighthouseinputcontroller import LighthouseInputController
from lighthouseoutputcontroller import LighthouseOutputController


class LighthouseGlobe:
    """
    This is the main class of the project. Combines all other functionality contained in the two controller classes
    which can communicate via the state class. Also handles the timing of a heartbeat signal and secures disconnecting
    from the api on any exception.
    """
    __ic: LighthouseInputController
    __oc: LighthouseOutputController
    __state: LighthouseState

    __timer_start_time: float
    __last_update_time: float

    def __init__(self, frame_rate: int, rotation_rate: int, file_name: str, max_interpolation_range: int):
        self.__state = LighthouseState(frame_rate, rotation_rate, rotation_rate_max=90.0)
        self.__ic = LighthouseInputController(self.__state)
        self.__oc = LighthouseOutputController(self.__state, file_name, max_interpolation_range)

        self.__loop_counter = 0
        self.__last_update_time = time()

    def __del__(self):
        self.__oc.stop_frame_rendering()
        self.__oc.disconnect()

    def __start_timer(self) -> None:
        self.__timer_start_time = time()

    def __sleep_rest_of_cycle(self) -> None:
        delta_time: float = time() - self.__last_update_time
        sleep_time: float = (1/self.__state.get_target_frame_rate()) - delta_time

        self.__last_update_time = time() + sleep_time

        sleep(sleep_time if sleep_time > 0 else 0)
        # Debug section
        # dt_str: str = " dt=" + "{:+10.5f}s".format(delta_time)
        # st_str: str = " st=" + "{:+10.5f}s".format(sleep_time)
        # tt_str: str = " tt=" + "{:+10.5f}s".format(self.__last_update_time - self.__start_time)
        # print("[DEBUG]", dt_str, st_str, tt_str)

    def get_elapsed_time_string(self) -> str:
        delta_time: float = time() - self.__timer_start_time
        return "{:.3f}s".format(delta_time).rjust(12)

    def run_main_loop(self) -> None:
        heartbeat_interval_seconds: int = 15
        loop_counter: int = 0
        loop_limit: int = self.__state.get_target_frame_rate() * heartbeat_interval_seconds
        self.__start_timer()
        try:
            self.__oc.start_frame_rendering()
            while not self.__state.should_terminate():
                if loop_counter >= loop_limit:
                    timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    print("Heartbeat of main loop at", timestamp, "after ", self.get_elapsed_time_string())
                    loop_counter = 0
                loop_counter += 1
                self.__sleep_rest_of_cycle()
        except BaseException as e:
            raise e
        finally:
            self.__oc.stop_frame_rendering()
            self.__oc.disconnect()


# stole this if-statement from the Pyghthouse examples
if __name__ == '__main__':
    lg: LighthouseGlobe = LighthouseGlobe(frame_rate=30,
                                          rotation_rate=45,
                                          file_name="earth_contrast.pnm",
                                          max_interpolation_range=3)

    lg.run_main_loop()

    exit(0)
