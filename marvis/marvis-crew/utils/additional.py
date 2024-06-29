import psutil
import win32process
import win32gui
from .core_imaging import focus_window, capture_screenshot, encode_image
import requests
from PIL import Image
import pyautogui
import io
import os

api_key = os.getenv("OPENAI_API_KEY")


def get_focused_window_details():
    try:
        window_handle = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(window_handle)
        _, window_pid = win32process.GetWindowThreadProcessId(window_handle)
        process = psutil.Process(window_pid)
        process_name = process.name()
        rect = win32gui.GetWindowRect(window_handle)
        window_position = (rect[0], rect[1])
        window_size = (rect[2] - rect[0], rect[3] - rect[1])
        return window_title, window_handle, window_pid, process_name, window_position, window_size
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def get_screen_image(window_title=None, additional_context=None, x=None, y=None, screenshot_size=None):
    window = None
    region = None

    if screenshot_size == 'Full screen':
        # We don't need window focus or a specific region for a full-screen screenshot.
        pass
    elif window_title:  # If a window title is provided, focus on the window.
        window = focus_window(window_title)
        if not window:
            return None  # If no window is found, exit the function.
        if screenshot_size and type(screenshot_size) == tuple and x is not None and y is not None:
            offset_x, offset_y = screenshot_size[0] // 2, screenshot_size[1] // 2
            # Adjust region to be relative to the window's top-left corner.
            window_box = window.box
            region = (
            window_box.left + x - offset_x, window_box.top + y - offset_y, screenshot_size[0], screenshot_size[1])
        else:
            # If screenshot_size is not provided or is not 'Full screen', capture the whole window.
            region = (window.box.left, window.box.top, window.box.width, window.box.height)

    screenshot = capture_screenshot(window, region)

    # Optionally, paste the cursor onto the screenshot, adjusting for the offset if a region is specified
    cursor_img_path = r'C:\Users\Grayphite\codebase\gui-automation-ms\core\media\Mouse_pointer_small.png'
    with Image.open(cursor_img_path) as cursor:
        cursor = cursor.convert("RGBA")  # Ensure cursor image has an alpha channel for transparency

        x_cursor, y_cursor = pyautogui.position()  # Current mouse position

        # If a region is specified, calculate the cursor position within that region
        if region:
            cursor_pos = (x_cursor - region[0], y_cursor - region[1])
        else:
            cursor_pos = (x_cursor, y_cursor)

        screenshot.paste(cursor, cursor_pos, cursor)

    # Convert the screenshot to bytes
    with io.BytesIO() as output_bytes:
        screenshot.save(output_bytes, 'PNG')
        bytes_data = output_bytes.getvalue()

    # Show a preview of the screenshot
    # screenshot.show()

    # Convert the bytes to a base64-encoded image and analyze
    base64_image = encode_image(bytes_data)
    return base64_image


def analyze_screenshot(screenshot, prompt):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{prompt}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screenshot}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']
