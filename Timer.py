import os
import sys
import time
import pygame
from pynput.keyboard import Key, Listener
import time
import threading

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path: Path to the resource relative to the project or bundle.

    Returns:
        An absolute path that works whether the app is frozen (e.g., with PyInstaller) or not.
    """
    try:
        # If the app is run from a PyInstaller bundle
        base_path = sys._MEIPASS
    except AttributeError:
        # Otherwise, use the current directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Timer:
    def __init__(self, interval, timer_display, key=None, timer_name="Generic Timer",
                 sound_path=None, sound_time=5, volume=1, use_notification=False, toaster=None):
        self.interval = interval
        self.key = key
        self.timer_name = timer_name
        self.sound_path = sound_path
        self.last_trigger = time.time()
        self.sound_time = sound_time
        self.use_notification = use_notification
        self.last_sound = time.time()
        self.sound = pygame.mixer.Sound(self.sound_path)
        self.sound.set_volume(volume)
        self.last_status_update = time.time()
        self.sound.set_volume(volume)
        self.last_key = None
        self.running = True
        self.timer_display = timer_display
        self.toaster = toaster

        def on_press(keypress):
            try:
                self.last_key = keypress
            except AttributeError:
                time.sleep(.05)

        def start_listener():
            # Set up the listener
            with Listener(on_press=on_press) as listener:
                listener.join()

        self.listener_thread = threading.Thread(target=start_listener, daemon=True)
        self.listener_thread.start()

    def checkAndRun(self):
        if not self.running:
            return

        if self.key is not None and self.last_key is not None:
            if self.last_key == self.key:
                self.reset()
                self.last_key = None

        if time.time() - self.last_status_update > 1:
            if not self.isTriggered():
                self.timer_display.update_status(
                    str(abs(round(self.interval + (self.last_trigger - time.time())))) + " seconds left")
            else:
                self.timer_display.update_status("TRIGGERED")

            self.last_status_update = time.time()

        if self.isTriggered():
            if self.sound_path is not None:
                if time.time() - self.last_sound > self.sound_time:
                    self.last_sound = time.time()
                    if self.use_notification:
                        self.send_notification()
                    else:
                        self.sound.play()
                    if self.key is None:
                        self.reset()

    def isTriggered(self):
        if not self.running:
            return False
        return time.time() - self.last_trigger > self.interval

    def reset(self):
        self.last_trigger = time.time()

    def stop(self):
        self.running = False

    def send_notification(self):

        # Send a notification
        self.toaster.show_toast(
            self.timer_name,  # Title of the notification
            "Key: " + str(self.key),  # Message of the notification
            duration=self.sound_time,  # How long the notification should remain (seconds)
            icon_path=resource_path("clock.ico"),  # Optional: Path to a custom icon
            threaded=True  # Run in a separate thread (won't block your program)
        )
