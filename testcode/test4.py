import keyboard

def greeting(e):
    print("Hello, Python初心者！")

keyboard.add_hotkey('ctrl+c', greeting)

keyboard.wait()