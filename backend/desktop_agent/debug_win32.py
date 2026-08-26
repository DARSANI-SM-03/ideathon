import win32gui
import win32process
import psutil

print(f"Foreground Window HWND: {win32gui.GetForegroundWindow()}")
print(f"Foreground Title      : {win32gui.GetWindowText(win32gui.GetForegroundWindow())}")

print("\n--- Listing All Visible Windows ---")
def enum_cb(hwnd, extra):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                pname = psutil.Process(pid).name()
                print(f"HWND {hwnd} | PID {pid} | Process: '{pname}' | Title: '{title}'")
            except Exception as e:
                print(f"HWND {hwnd} | PID {pid} | Title: '{title}' (error: {e})")
    return True

win32gui.EnumWindows(enum_cb, None)
