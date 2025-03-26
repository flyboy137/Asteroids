
from constants import *

class Timer:
    def __init__(self, trigger_time, func):
        self.trigger_time = trigger_time
        self.func = func
        self.start_time = 0
        self.end_time = self.start_time
        self.pause_time = 0
        self.is_start, self.is_pause = False, False

    def start(self):
        self.start_time = get_time()
        self.end_time = self.start_time
        self.is_start = True

    def stop(self):
        self.start_time, self.end_time = 0, 0
        self.is_start = False

    def pause(self):
        self.is_start = False
        self.is_pause = True
        self.pause_time = get_time()

    def resume(self):
        self.start_time += get_time() - self.pause_time
        self.is_pause = False
        self.is_start = True

    def update(self):
        if self.is_start:
            self.end_time = get_time()
            if self.end_time - self.start_time >= self.trigger_time:
                self.func()
                self.start_time = self.end_time





