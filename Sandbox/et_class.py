# elaspsed time implemenetd as python class
#
# Elapsed timer / stopwatch, implemented as a python class
# https://realpython.com/python-timer/#python-timer-functions
#

import time

class TimerError(Exception):
    # A custom exception used to report errors in use of Timer class
    # use built-in class for error handling
    pass

class Timer:
    def __init__(self, text="Elapsed time: {:0.2f} seconds", logger=print):
        self._start_time = None
        self.text = text
        self.logger = logger

    def start(self):
        # Start a new timer
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")
        self._start_time = time.perf_counter()

    def stop(self):
        # Stop the timer, and report the elapsed time in seconds
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        if self.logger:
            self.logger(self.text.format(elapsed_time))
        return elapsed_time

###############################
# MAIN

def main():
    stopwatch = Timer(text="SUT reboot required {:.2f} seconds", logger=print)
    stopwatch.start()
    time.sleep(3)
    stopwatch.stop()

if __name__ == "__main__":
    main()
