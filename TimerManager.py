import threading
import time


class TimerManager:
    def __init__(self):
        self.timers = {}
        self.running = True
        self.timers_lock = threading.Lock()

    def add_timer(self, timer, timer_id):
        with self.timers_lock:
            self.timers[timer_id] = timer

    def remove_timer(self, timer_id):
        with self.timers_lock:
            if timer_id in self.timers:
                del self.timers[timer_id]

    def manual_reset(self, timer_id):
        with self.timers_lock:
            if timer_id in self.timers:
                self.timers[timer_id].reset()

    def run(self):
        while self.running:
            with self.timers_lock:
                for timer in list(self.timers.values()):
                    timer.checkAndRun()
            time.sleep(0.1)
