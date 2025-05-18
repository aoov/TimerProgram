import time
import pygame
from pynput.keyboard import Listener

from TimerDisplay import TimerCard
from nicegui import ui, app
import threading
from TimerManager import TimerManager

import os

pygame.mixer.init()

# Remove margin/padding from body for cleaner layout
# Counter for unique card IDs
card_counter = 0

# Remove margin/padding from body for cleaner layout
ui.query('body').classes('m-0 p-0')

# Add a button row at the top
with ui.row().classes('p-4'):
    ui.button('Add Timer', on_click=lambda: add_timer())

# A grid that grows vertically with content
grid = ui.grid(columns=2).classes('w-full gap-4 p-4')  # no height restriction

manager = TimerManager()
manager_thread = threading.Thread(target=manager.run, daemon=True)
manager_thread.start()
last_keypress = None


def on_press(key):
    global last_keypress
    try:
        last_keypress = key
    except AttributeError:
        time.sleep(.05)


def start_listener():
    # Set up the listener
    with Listener(on_press=on_press) as listener:
        listener.join()


# Create and start the thread for the listener
listener_thread = threading.Thread(target=start_listener)
listener_thread.start()


def add_timer():
    global card_counter
    # Generate a unique Python ID
    card_counter += 1
    TimerCard(card_counter, grid, get_last_keypress, set_last_keypress,
              on_remove=lambda e: on_remove(e), on_enable=on_enable,
              on_disable=on_disable, manual_reset=manual_reset)


def get_last_keypress():
    return last_keypress


def set_last_keypress(key):
    global last_keypress
    last_keypress = key


def on_remove(card):
    manager.remove_timer(card.get_timer)


def on_disable(card, card_id):
    card.update_status("")
    manager.remove_timer(card_id)


def on_enable(card, card_id):
    timer = card.get_timer()
    if timer is None:
        return False

    manager.add_timer(timer, card_id)
    return True


def manual_reset(timer_id):
    manager.manual_reset(timer_id)


ui.run(reload=False, title="Aaron's Timer", favicon="⏰")
