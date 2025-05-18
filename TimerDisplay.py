import asyncio
import os
import sys
from typing import Optional, Callable

from docutils.nodes import status
from nicegui import ui
from pathlib import Path
from Timer import Timer
from local_file_picker import local_file_picker  # adjust import as needed


def is_wav_or_mpe_quick(path: str) -> bool:
    path = path.lower()
    return path.endswith('.wav') or path.endswith('.mp3')


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


class TimerCard:
    def __init__(self, card_id: int, parent_grid, get_last_keypress,
                 set_last_keypress, on_remove=None, on_enable=None, on_disable=None,
                 manual_reset=None):
        self.card_id = card_id
        self.name_input = None
        self.file_label = None
        self.file_path = None
        self.slider = None
        self.volume_label = None
        self.enabled = False
        self.key = None
        self.number_input = None
        self.number = 0
        self.volume = 100
        self.on_remove = on_remove
        self.on_enable = on_enable
        self.on_disable = on_disable
        self.get_last_keypress = get_last_keypress
        self.set_last_keypress = set_last_keypress
        self.manual_reset = manual_reset

        with parent_grid:
            self.card = ui.card()
            with self.card:
                with ui.row().classes("w-full justify-between items-center"):
                    self.status_label = ui.label("Status: ")
                    self.switch = ui.switch("Turn On",
                                            on_change=lambda e: self.toggle(e.value),
                                            value=self.enabled)
                with ui.row().classes("w-full"):
                    self.name_input = ui.input(label="Name")
                    self.number_input = ui.number(label="Seconds", min=0, step=1, format='%.0f',
                                                  on_change=lambda e: self.setValue(e.value))
                with ui.row().classes(""):
                    self.sound_label = ui.label('Sound: ')
                    self.file_label = ui.label('Default Sound')
                with ui.row().classes("w-full justify-between items-center"):
                    self.volume_label = ui.label('100%')
                    self.slider = ui.slider(min=0, max=100, step=1, value=self.volume,
                                            on_change=lambda e: self.update_volume(e.value))
                with ui.row().classes("w-full"):
                    self.pick_file_button = ui.button('Pick Sound', on_click=self.pick_file)
                    self.bind_button = ui.button("Bind Key", on_click=self.wait_for_key)
                    self.manual_reset_button = ui.button("Reset", on_click=self.reset)
                self.remove_button = ui.button(on_click=self.remove, icon="clear")

    async def pick_file(self):
        result = await local_file_picker('~', multiple=False)
        if not result or not is_wav_or_mpe_quick(result[0]):
            ui.notify('Not a .wav or .mp3')
            return

        self.file_path = result[0]
        file_name = Path(self.file_path).name
        self.file_label.text = file_name

    async def wait_for_key(self):
        self.set_last_keypress(None)

        while self.get_last_keypress() is None:
            await asyncio.sleep(0.05)  # non-blocking wait

        self.key = self.get_last_keypress()
        self.bind_button.set_text("Bound: " + str(self.key))

    def remove(self):
        self.card.delete()
        if self.on_remove:
            self.on_remove(self)

    def reset(self):
        if self.manual_reset is not None and self.enabled:
            self.manual_reset(self.card_id)

    def toggle(self, value):
        if value is True:
            self.name_input.disable()
            self.pick_file_button.disable()
            self.remove_button.disable()
            self.slider.disable()
            self.number_input.disable()
            self.bind_button.disable()
            self.switch.set_value(True)
            self.manual_reset_button.enable()
            self.enabled = True
            if self.on_enable is not None:
                if not self.on_enable(self, self.card_id):
                    self.toggle(False)
        else:
            self.name_input.enable()
            self.number_input.enable()
            self.bind_button.enable()
            self.pick_file_button.enable()
            self.remove_button.enable()
            self.enabled = False
            self.slider.enable()
            self.manual_reset_button.disable()
            self.switch.set_value(False)
            if self.on_disable is not None:
                self.on_disable(self, self.card_id)

    def update_volume(self, value):
        self.volume = value / 100
        self.volume_label.text = f' {value}%'

    def update_status(self, value):
        self.status_label.text = "Status: " + value

    def setValue(self, value):
        self.number = value

    def validate(self):
        if self.number == 0:
            ui.notify("Number cannot be 0.")
            return False
        return True

    def get_timer(self):
        if not self.validate():
            return None
        if self.file_path is None:
            self.file_path = resource_path("retro.wav")

        return Timer(self.number, self, key=self.key, sound_path=self.file_path, volume=self.volume)
