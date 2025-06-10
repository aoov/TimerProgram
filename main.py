import json
import time
import pygame
from pynput.keyboard import Listener, Key, KeyCode
from win10toast import ToastNotifier

from TimerDisplay import TimerCard
from nicegui import ui, app
import threading
from TimerManager import TimerManager
from pathlib import Path
import os

pygame.mixer.init()

# Remove margin/padding from body for cleaner layout
# Counter for unique card IDs
card_counter = 0
dark = ui.dark_mode()
dark.enable()

# Remove margin/padding from body for cleaner layout
ui.query('body').classes('m-0 p-0')

toaster = ToastNotifier()
useWindows = False

def get_documents_timers_folder():
    # Find user documents folder
    if os.name == 'nt':
        documents_folder = Path(os.environ['USERPROFILE']) / 'Documents'
    else:
        documents_folder = Path.home() / 'Documents'
    timers_folder = documents_folder / 'timers'
    timers_folder.mkdir(parents=True, exist_ok=True)
    return timers_folder


def read_all_timers_from_folder():
    timers_folder = get_documents_timers_folder()
    timer_data_list = []
    for file in timers_folder.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                timer_data_list.append(data)
        except Exception as e:
            print(f"Failed to read {file}: {e}")
    return timer_data_list

def toggle_toasts():
    global useWindows
    useWindows = not useWindows

# Add a button row at the top
with ui.row().classes('p-4'):
    ui.button('Add Timer', on_click=lambda: add_timer())
    ui.button('Save Timers', on_click=lambda: save_timers())
    ui.button('Toggle All On', on_click=lambda: toggle_all())
    ui.switch(text="windows notifications", value=useWindows, on_change=toggle_toasts)
# A grid that grows vertically with content
grid = ui.grid(columns=2).classes('w-full gap-4 p-4')  # no height restriction

manager = TimerManager()
manager_thread = threading.Thread(target=manager.run, daemon=True)
manager_thread.start()
last_keypress = None
timers = []

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
    timers.append(TimerCard(card_counter, grid, get_last_keypress, set_last_keypress,
                            on_remove=lambda e: on_remove(e), on_enable=on_enable,
                            on_disable=on_disable, manual_reset=manual_reset))

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

def manual_reset(timer_id):
    manager.manual_reset(timer_id)

def on_enable(card, card_id):
    timer = card.get_timer(toaster, useWindows)
    if timer is None:
        return False

    manager.add_timer(timer, card_id)
    return True


def string_to_key(key_str):
    """
    Converts a string like 'Key.enter', 'a', or "'g'" to the appropriate Key or KeyCode.
    Returns:
        - Key for special keys
        - KeyCode for regular keys
        - None if invalid
    """
    if key_str is None:
        return None

    # Remove surrounding quotes if present
    if (isinstance(key_str, str) and
            ((key_str.startswith("'") and key_str.endswith("'")) or
             (key_str.startswith('"') and key_str.endswith('"')))):
        key_str = key_str[1:-1]

    if key_str.startswith('Key.'):
        member_name = key_str.split('.', 1)[1]
        try:
            return getattr(Key, member_name)
        except AttributeError:
            return None  # Invalid key string
    elif len(key_str) == 1:
        # Match pynput's KeyCode(char=...)
        return KeyCode(char=key_str)
    else:
        return None  # Unrecognized


# Loads existing timers from the folder
for timer_data in read_all_timers_from_folder():
    card_counter += 1
    timers.append(TimerCard(card_counter, grid, get_last_keypress, set_last_keypress,
                            on_remove=lambda e: on_remove(e), on_enable=on_enable,
                            on_disable=on_disable, manual_reset=manual_reset,
                            number=timer_data.get("interval"), volume=timer_data.get("volume")*100,
                            key=string_to_key(timer_data.get("key")), file_path=timer_data.get("file_path"),
                            name=timer_data.get("name")))

def save_timers():
    delete_all_in_timers_folder()
    counter = 0
    for timer in timers:
        save_to_timers_folder(f"timer_{counter}.json", timer.to_dict())
        counter += 1

def toggle_all():
    for timer in timers:
        timer.toggle(True)

def save_to_timers_folder(filename, data):
    timers_folder = get_documents_timers_folder()
    print("Saved to: " + str(timers_folder.resolve()))
    file_path = timers_folder / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def delete_all_in_timers_folder():
    timers_folder = get_documents_timers_folder()
    for item in timers_folder.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            import shutil
            shutil.rmtree(item)



ui.run(reload=False, title="Aaron's Timer", favicon="⏰")
