simple timer program

has key listeners for the purpose of binding keys to reset the timers

if a key is bound to a timer, the timer will continue playing the sound until the key is pressed 

Requires admin mode

Original purpose - help keep uptime when farming in maplestory


Uses: nicegui, pynput, pygame - packaged using pyinstaller

Build command: 
```bash
pyinstaller --name Timer --onefile --uac-admin --add-data "retro.wav;." --add-data "C:\Users\xryda\AppData\Local\Programs\Python\Python312\Lib\site-packages\nicegui;nicegui" main.py
```

