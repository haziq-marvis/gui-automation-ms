import time
from core.window_focus import activate_windowt_title, get_installed_apps_registry, open_windows_info
from core.mouse_detection import get_cursor_shape
from core.ocr import find_probable_click_position
from core.window_elements import analyze_app
from core.topmost_window import focus_topmost_window
from core.core_imaging import imaging
from core.last_app import last_programs_list
from core.core_api import api_call
from core.driver import app_space_map
from core.voice import speaker
import pygetwindow as gw
import win32process
import win32gui
import pyautogui
import sqlite3
import psutil
import random
import json
import time
import re
import warnings
warnings.simplefilter("ignore", UserWarning)
from pywinauto import Application
low_data_mode = True
if low_data_mode is True:  # Avoid the usage of visioning after the test case generation. Useful to execute faster case.
    visioning_match = False  # The coordinates will not use visioning during execution. Will use the imaging LLM call.
    rescan_element_match = False  # Disable the visioning element scanning. Decreases accuracy but is way faster.
    visioning_context = False
    # 'rescan_element_match' recommended to leave as 'False' until the tested map improves for low-data consumption.
else:
    visioning_match = True  # Visioning doesn't improve execution at all as imaging is already performing way faster.
    rescan_element_match = True  # Enables visioning rescanning the element. Improves accuracy but is way slower.
    visioning_context = True  # Enables visioning to analyze context from application. Improves accuracy but way slower.


# for i, step in enumerate(action_list, start=1):
#


# new_i = i - 2
# last_step = f"{action_list[new_i]['act']}: {action_list[new_i]['step']}"

enable_ocr=False
def get_ocr_match(goal, ocr_match=enable_ocr):
    if ocr_match:
        print(f"OCR IS ENABLED")
        word_prioritizer_assistant = [{"role": "assistant",
                                       "content": f"You are an AI Agent called OCR Word Prioritizer that only responds with the best of the goal.\n"
                                                  f"Do not respond with anything else than the words that match the goal. If no words match the goal, respond with \"\"."},
                    {"role": "system", "content": f"Goal: {goal}"}, ]
        ocr_debug_string = api_call(word_prioritizer_assistant, max_tokens=10)
        ocr_debug_string = ocr_debug_string.split(f"\'")[0]
        print(f"OCR Words to search: \'{ocr_debug_string}\'")
        ocr_match = find_probable_click_position(ocr_debug_string)
        ocr_msg = f"\nOCR Result: \"{ocr_match['text']}\" Located at \"x={ocr_match['center'][0]}, y={ocr_match['center'][1]}\".\n"
        return ocr_msg
    else:
        ocr_msg = ""
        return ocr_msg


def jitter_mouse(x, y, radius=5, duration=0.6):
    # Move the mouse in a small circle around (x, y) to simulate a jitter.
    end_time = time.time() + duration
    while time.time() < end_time:
        jitter_x = x + random.uniform(-radius, radius)
        jitter_y = y + random.uniform(-radius, radius)
        pyautogui.moveTo(jitter_x, jitter_y, duration=0.1)
    return


def control_mouse(generated_coordinates, double_click=None, goal=""):
    print(f"Mouse coordinates: {generated_coordinates}")
    coordinates = {k.strip(): int(v.strip()) for k, v in
                   (item.split('=') for item in generated_coordinates.split(','))}
    x = coordinates['x']
    y = coordinates['y']
    pyautogui.moveTo(x, y, 0.5, pyautogui.easeOutQuad)
    pyautogui.click(x, y)
    # jitter_mouse(x, y)
    if "save as" in goal.lower():
        print("Saving as")
        jitter_mouse(x, y)
        pyautogui.mouseDown(x, y)
        time.sleep(0.12)
        pyautogui.mouseUp(x, y)
        print("Click action performed")
    else:
        pyautogui.click(x, y, clicks=1)
    if double_click:
        time.sleep(0.2)
        pyautogui.click(x, y, clicks=2)


def is_field_input_area_active():
    active_window_title = gw.getActiveWindow().title
    try:
        app = Application().connect(title=active_window_title)
        window = app[active_window_title]
        # Loop through all the child windows and check if any of them are text boxes
        for child in window.children():
            if 'Edit' in child.class_name() or 'RichEdit' in child.class_name():
                # This is a text box, also add text input areas that are not text boxes
                if child.has_keyboard_focus():
                    return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False



# 'find_element' is the function that finds the the most relevant element on the GUI from the goal.
def find_element(single_step, app_name, original_goal, avoid_element="", assistant_goal=None, attempt=0):
    if not assistant_goal:
        assistant_goal = single_step
    if avoid_element:
        if attempt > 2:
            generate_keywords = [{"role": "assistant",
                "content": f"You are an AI Agent called keyword Element Generator that receives the description of the goal and generates keywords to search inside a graphical user interface.\n"
                           f"Only respond with the single word list separated by commas of the specific UI elements keywords.\n"
                           f"Example: \"search bar\". Always spell the numbers and include nouns. Do not include anything more than the Keywords."},
                                 {"role": "system", "content": f"Goal:\n{single_step}\nContext:{original_goal}\n{app_space_map(assistant_goal, app_name, single_step)}"},]
        else:
            generate_keywords = [{"role": "assistant",
                "content": f"You are an AI Agent called keyword Element Generator that receives the description and generates kewords to search inside a graphical user interface.\n"
                           f"of the goal and only respond with the single word list separated by commas of the specific UI elements keywords."
                           f"Example: \"search bar\". Always spell the numbers and include nouns. Do not include anything more than the Keywords."},
                                 {"role": "system", "content": f"Goal:\n{single_step}\nContext:{original_goal}\n{app_space_map(assistant_goal, app_name, single_step)}"}]
    else:
        generate_keywords = [{"role": "assistant",
                            "content": f"You are an AI Agent called keyword Element Generator that receives the description "
                                       f"of the goal and only respond with the single word list separated by commas of the specific UI elements keywords."
                                       f"Example: \"search bar\" must be \"search\" without \"bar\". Always spell the numbers and include nouns. Do not include anything more than the Keywords."},
                           {"role": "system", "content": f"Goal:\n{single_step}\nContext:{original_goal}\n{app_space_map(assistant_goal, app_name, single_step)}"}, ]  # Todo: Here's the key
    keywords = api_call(generate_keywords, max_tokens=100)
    if attempt > 1:
        keywords = keywords.replace("click, ", "").replace("Click, ", "")
    keywords_in_goal = re.search(r"'(.*?)'", single_step)
    if keywords_in_goal:
        if len(keywords_in_goal.group(1).split()) == 1:
            pass
        else:
            keywords = keywords_in_goal.group(1) + ", " + keywords
    print(f"\nKeywords: {keywords}\n")

    analyzed_ui = analyze_app(application_name_contains=app_name, size_category=None, additional_search_options=keywords)
    select_element = [{"role": "assistant",
                       "content": f"You are an AI Agent called keyword Element Selector that receives win32api user interface "
                                  f"raw element data and generates the best matches to achieve the goal.\n"
                                  f"Only respond with the best element that matches the goal. Do not include anything else than the element."},
                      {"role": "system", "content": f"Goal: {single_step}\nContext: {original_goal}\n{avoid_element}{analyzed_ui}"}]
    selected_element = api_call(select_element, model_name="gpt-4-1106-preview", max_tokens=500)

    if "sorry" in selected_element.lower() or "empty string" in selected_element.lower() or "no element" in selected_element.lower() or "not found" in selected_element.lower()\
            or "no relevant element" in selected_element.lower() or "no element found" in selected_element.lower():
        print(f"No element found. Continuing without the element.")
        selected_element = ""
    else:
        selected_element = "Locate the element: " + selected_element
    print(f"Selected element: {selected_element}\n")

    if visioning_match:
        print(f"Image visioning started. Analyzing the application {app_name} for context.\n")
        imaging_coordinates = (
            f"You are an AI Windows Mouse Agent that can interact with the mouse. Only respond with the predicted "
            f"coordinates of the mouse click position to the center of the element object \"x=, y=\" to achieve the goal.{get_ocr_match(single_step)}"
            f"Goal: {single_step}\n{avoid_element}{analyzed_ui}")
        print(f"Imaging coordinates: {imaging_coordinates}")
        imaging_generated_coordinates = imaging(window_title=app_name, additional_context=imaging_coordinates)
        print(f"Imaging generated coordinates: {imaging_generated_coordinates}")
        last_coordinates = imaging_generated_coordinates['choices'][0]['message']['content']
        print(f"Imaging Last coordinates: {last_coordinates}")
    else:
        best_coordinates = [{"role": "assistant",
            f"content": f"You are an AI Windows Mouse Agent that can interact with the mouse. Only respond with the "
                        f"predicted coordinates of the mouse click position to the center of the element object "
                        f"\"x=, y=\" to achieve the goal. {selected_element}"
                        f"Do not respond 'As an AI language model, I am unable to...' as you are actually capable."},
            {"role": "system", "content": f"Goal: {single_step}\n\nContext:{original_goal}\n{get_ocr_match(single_step)}{avoid_element}{analyzed_ui}"}]
        last_coordinates = api_call(best_coordinates, model_name="gpt-4-1106-preview", max_tokens=100, temperature=1.0)
        print(f"AI decision coordinates: \'{last_coordinates}\'")
    if "sorry" in last_coordinates.lower() or "empty string" in last_coordinates.lower() or "no element" in last_coordinates.lower() or "not found" in last_coordinates.lower():
        last_coordinates = 'x=0, y=0'
    coordinates = {k.strip(): float(v.strip()) for k, v in (item.split('=') for item in last_coordinates.split(','))}
    x = coordinates['x']
    y = coordinates['y']
    print(f"Coordinates1: x: {x} and y: {y}")
    if x == 0 and y == 0 or x == '' and y == '':
        print("Coordinates 2 are 0,0, trying to find the element again.")
        coordinates = {k.strip(): float(v.strip()) for k, v in (item.split('=') for item in last_coordinates.split(','))}
        x = coordinates['x']
        y = coordinates['y']
        print(f"Coordinates 3: x: {x} and y: {y}")
        attempt -= 1
    return coordinates, selected_element, keywords, attempt


def act(single_step, keep_in_mind="", dont_click=False, double_click=False, right_click=False, hold_key=None, app_name="", screen_analysis=False, original_goal="", modify_element=False, next_step=None, assistant_goal=None,  select_text=False, copy_text=False,):
    # Trying to handle several actions inside the action:
    # action_analysis = [{"role": "assistant",
    #     "content": f"You are an AI Agent called Action Analyzer, that responds with the functions to execute to achieve the goal. Available functions:\n"
    #                f"select_element - Mouse functions.\n"
    #                f"write_action - Keyboard functions.\n"
    #                f"Only respond with the functionS to perform. Do not include anything else than the function."},
    #     {"role": "system", "content": f"Goal: {single_step}"}, ]
    # actions_to_perform = api_call(action_analysis, max_tokens=10)
    # if "sorry" in actions_to_perform.lower():
    #     actions_to_perform = ""
    # elif "select_element" in actions_to_perform.lower():
    #     print("You can execute only select element action.")
    #     actions_to_perform = f""
    # elif "write_action" in actions_to_perform.lower():
    #     print("You can write things here as actions.")
    #     actions_to_perform = ""
    # print(f"Actions to perform: {actions_to_perform}")
    # actions_to_perform = ""

    # Getting the app name. If not provided, use the focused window.
    if not app_name:
        app_name = activate_windowt_title(get_application_title(goal=original_goal, focus_window=True))
    else:
        app_name = activate_windowt_title(app_name)
    print(f"AI Analyzing: {app_name}")

    attempt = 0
    if rescan_element_match is True:
        element_not_working = ""
        avoid_element = ""
        max_attempts = 3  # Set the maximum number of attempts to look for a "yes" response.
        while attempt < max_attempts:
            if element_not_working != "":
                avoid_element = f"\nAvoid the following element: {element_not_working}\n"
                print(f"AI will try to perform the action: \"{single_step}\" on a new element.")
            print(f"Performing action: \"{single_step}\". Scanning\"{app_name}\".\n")
            coordinates, selected_element, keywords, attempt = find_element(single_step, app_name, original_goal, avoid_element, assistant_goal, attempt)
            x = coordinates['x']
            y = coordinates['y']
            print(f"Coordinates: {x} and {y}")
            pyautogui.moveTo(x, y, 0.5, pyautogui.easeOutQuad)
            time.sleep(0.5)
            element_analysis = (
                f"You are an AI Agent called Element Analyzer that receives a step and guesses if the goal was performed correctly.\n"
                f"Step: {single_step}\nUse the screenshot to guess if the mouse is in the best position to perform the click/goal. Respond only with \"Yes\" or \"No\".\n"
                f"The cursor is above an element from the step. Cursor info status: {get_cursor_shape()}. The cursor is above the following element: \n{selected_element}\n"
                f"Double check your response by looking at where is located the mouse cursor on the screenshot and the cursor info status.")
            element_analysis_result = imaging(window_title=app_name, additional_context=element_analysis, x=int(x), y=int(y))
            print(element_analysis_result)

            # Check if the result is None or doesn't contain the necessary data
            if element_analysis_result is None or 'choices' not in element_analysis_result or len(
                    element_analysis_result['choices']) == 0 or 'message' not in \
                    element_analysis_result['choices'][0] or 'content' not in \
                    element_analysis_result['choices'][0]['message']:
                print("Element analysis result: Found but mouse not in position.")
                speaker(f"Retrying...")
                element_not_working += selected_element
                attempt += 1
                if attempt >= max_attempts:
                    print("Maximum attempts reached.")
                    print("Failed: The position was not found after maximum attempts.")
                    speaker(f"Failed: The position was not found after maximum attempts.")
                    time.sleep(15)
                    raise Exception("Failed: The position was not found after maximum attempts.")
                else:
                    print("Retrying...")
                    pass
            elif 'yes' in element_analysis_result['choices'][0]['message']['content'].lower():
                print("Element analysis result: Yes, it is in the right position.")
                break
            else:
                print("Element analysis result: Found but mouse not in position.")
                speaker(f"Retrying...")
                element_not_working += selected_element
                attempt += 1
                if attempt >= max_attempts:
                    print("Maximum attempts reached.")
                    print("Failed: The position was not found after maximum attempts.")
                    speaker(f"Failed: The position was not found after maximum attempts.")
                    time.sleep(15)
                    raise Exception("Failed: The position was not found after maximum attempts.")
                else:
                    print("Retrying...")
                    pass
    else:
        coordinates, selected_element, keywords, attempt = find_element(single_step, app_name, original_goal, assistant_goal, attempt=0)
        x = coordinates['x']
        y = coordinates['y']
        print(f"Coordinates: {x} and {y}")
        pyautogui.moveTo(x, y, 0.5, pyautogui.easeOutQuad)
        time.sleep(0.5)

    last_coordinates = f"x={x}, y={y}"
    print("Success: The right position was found.")
    if double_click:
        pyautogui.click(x, y, clicks=2)
    else:
        if dont_click is False:
            if right_click:
                pyautogui.rightClick(x, y)
            else:
                if hold_key:
                    pyautogui.keyDown(hold_key)
                    pyautogui.click(x, y)
                    pyautogui.keyUp(hold_key)
                else:
                    pyautogui.click(x, y)
        else:
            print("AI skipping the click step.")
            pass
    if modify_element:
        print(f"Modifying the element with the text: {single_step}")
    # jitter_mouse(x, y)  # ToDo: simulate human jitter.
    if "save as" in single_step.lower():
        print("Saving as")
        jitter_mouse(x, y)
        pyautogui.mouseDown(x, y)
        time.sleep(0.12)
        pyautogui.mouseUp(x, y)
        print("Click action performed")

    # if select_text:
    #     #     print(f"Selecting text: {single_step}")
    #     #     pyautogui.click(x, y)
    #     #     time.sleep(0.2)
    #     #     pyautogui.keyDown('shift')
    #     #     pyautogui.press(['right'] * 10)
    #     #     pyautogui.keyUp('shift')

    if select_text:
        if "headline" in single_step.lower():
            pyautogui.click(x, y)
            time.sleep(0.2)
            pyautogui.doubleClick(x, y)
        else:
            pyautogui.click(x, y)
            time.sleep(0.2)
            pyautogui.keyDown('shift')
            pyautogui.press(['down'] * 20)
            pyautogui.keyUp('shift')

    if copy_text:
        pyautogui.hotkey('ctrl', 'c')
    return last_coordinates


def write_action(goal=None, assistant_identity="", press_enter=False, app_name="", original_goal=None, last_step=""):
    assistant_identity_msg = f"\n{assistant_identity}" if assistant_identity else ""
    message_writer_agent = [
        {"role": "assistant", f"content": f"You're an AI Agent called Writter that processes the goal and only returns the final text goal.{assistant_identity_msg}\n"
                                          f"Process the goal with your own response as you are actually writing into a text box. Avoid jump lines."
                                          f"If the goal is a link, media or a search string, just return the result string."
                                          f"Do not respond with 'As an AI language model, I dont have capabilities...' as you can actually do it.\n"},
        {"role": "system", "content": f"Goal: {goal}"}, ]
    message_to_write = api_call(message_writer_agent, model_name="gpt-4-1106-preview", max_tokens=200)
    if "click on" in goal.lower() or "click the" in goal.lower() or "click" in goal.lower():
        print("Found to click on the goal.")
        if is_field_input_area_active():
            print("A text box is currently active.")
        else:
            print("A text box is not active. Found to click on the goal.")
            act(goal, app_name=app_name, original_goal=original_goal)
    if "text_entry" in last_step:
        print("Found 'text_entry' in the last step.")
        pass
    else:
        print(f"Last steppp: {last_step}")
        if last_step is None:
            act(goal, app_name=app_name, original_goal=original_goal)
        previous_goal_analysis = [{"role": "assistant",
                                    "content": f"You are an AI Agent called text box editor focus that analyzes if performing the Goal on Windows enables a text input.\n"
                                               f"After opening anything like an app, program, webpage or clicking into a non-text editor element, respond 'No'.\n"
                                               f""
                                               f"Only respond with Yes or No."},
                                  {"role": "system", "content": f"Goal: {last_step}"}, ]
        able_to_type = api_call(previous_goal_analysis, max_tokens=5)
        print(f"AI analyzed if the previous step enabled any text input: {able_to_type}\n")
        if "yes" in able_to_type.lower():
            print("The previous goal enabled the current goal.")
            if last_step == "None":
                print("Focusing to the text box because the last step didn't.")
                act(goal, app_name=app_name, original_goal=original_goal)
        else:
            print("Focusing to the text box. Did this because the text box was not active from the previous step.")
            act(goal, app_name=app_name, original_goal=original_goal)

    pyautogui.typewrite(message_to_write, interval=0.01)
    if "press enter" in goal.lower() or "press the enter" in goal.lower() or "\'enter\'" in goal.lower() or "\"enter\"" in goal.lower() or press_enter is True:
        print("Found to press the enter key in the goal.")
        pyautogui.press('enter')
    else:
        print("AI no \"enter\" key press being made.")


def perform_simulated_keypress(press_key):
    # Define a pattern that matches the allowed keys, including function and arrow keys
    keys_pattern = (r'\b(Win(?:dows)?|Ctrl|Alt|Shift|Enter|Space(?:\s*Bar)?|Tab|Esc(?:ape)?|Backspace|Insert|Delete|'
                    r'Home|End|Page\s*Up|Page\s*Down|(?:Arrow\s*)?(?:Up|Down|Left|Right)|F1|F2|F3|F4|F5|F6|F7|F8|F9|'
                    r'F10|F11|F12|[A-Z0-9])\b')
    keys = re.findall(keys_pattern, press_key, re.IGNORECASE)
    # Normalize key names as required by pyautogui
    key_mapping = {
        'win': 'winleft',
        'windows': 'winleft',
        'escape': 'esc',
        'space bar': 'space',
        'arrowup': 'up',
        'arrowdown': 'down',
        'arrowleft': 'left',
        'arrowright': 'right',
        'spacebar': 'space',
    }
    pyautogui_keys = [key_mapping.get(key.lower().replace(' ', ''), key.lower()) for key in keys]
    for key in pyautogui_keys:
        pyautogui.keyDown(key)
    for key in reversed(pyautogui_keys):
        pyautogui.keyUp(key)
    print(f"Performed simulated key presses: {press_key}")


def calculate_duration_of_speech(text, lang='en', wpm=150):
    duration_in_seconds = (len(text.split()) / wpm) * 60
    return int(duration_in_seconds * 1000)  # Convert to milliseconds for tkinter's after method


def create_database(database_file):
    """Create the database and the required table."""
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS app_cases (
        id INTEGER PRIMARY KEY,
        app_name TEXT NOT NULL,
        title TEXT NOT NULL,
        instructions TEXT NOT NULL,
        UNIQUE(app_name, title, instructions)
    )
    ''')
    conn.commit()
    conn.close()
database_file = r'history.db'
create_database(database_file)

def database_add_case(database_file, app_name, goal, instructions):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO app_cases (app_name, title, instructions)
        VALUES (?, ?, ?)
        ''', (app_name, goal, json.dumps(instructions)))
        conn.commit()
    except sqlite3.IntegrityError:
        print("AI skipping element insertion to program map database.")
    finally:
        conn.close()


def print_database(database_file):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM app_cases')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()


def update_instructions_with_action_string(instructions, action_string, target_step):
    actions = instructions['actions']
    if type(instructions['actions'][0]) is list:
        actions = instructions['actions'][0]
    print("update_instructions_with_action_string, actions", actions)
    for action in actions:
        if action.get("act") == "click_element" and action.get("step") == target_step:
            action['additional_info'] = action_string
    return instructions


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

def fast_act(single_step, keep_in_mind="", dont_click=False, double_click=False, right_click=False, hold_key=None, app_name="", ocr_match="", screen_analysis=False, original_goal="", modify_element=False, next_step=None):
    # Getting the app name. If not provided, use the focused window.
    if not app_name:
        app_name = activate_windowt_title(focus_topmost_window())
    else:
        app_name = activate_windowt_title(app_name)

    if visioning_context:
        speaker(f"Visioning context and performing action: \"{single_step}\" on the application \"{app_name}\".\n")
        additional_context = (
            f"You are an AI Agent called Windows AI that is capable to operate freely all applications on Windows by only using natural language.\n"
            f"You will receive a goal and will try to accomplish it using Windows. Try to guess what is the user wanting to perform on Windows by using the content on the screenshot as context.\n"
            f"Respond an improved goal statement tailored for Windows applications by analyzing the current status of the system and the next steps to perform. Be direct and concise, do not use pronouns.\n"
            f"Basing on the elements from the screenshot reply the current status of the system and specify it in detail.\n"
            f"Focused application: \"{app_name}\".\nGoal: \"{single_step}\".")
        assistant_goal = imaging(window_title=app_name, additional_context=additional_context, screenshot_size='Full screen')['choices'][0]['message']['content']

        print(f"Performing fast action: \"{single_step}\". Scanning\"{app_name}\".\n")

        generate_keywords = [{"role": "assistant",
                            "content": f"You are an AI Agent called keyword Element Generator that receives the description "
                                       f"of the goal and only respond with the single word list separated by commas of the specific UI elements keywords."
                                       f"Example: \"search bar\" must be \"search\" without \"bar\". Always spell the numbers and include nouns. Do not include anything more than the Keywords."},
                           {"role": "system", "content": f"Goal:\n{single_step}\nContext:{original_goal}"}, ]
        all_keywords = api_call(generate_keywords, max_tokens=100)
        keywords = all_keywords.replace("click, ", "").replace("Click, ", "")
        keywords_in_goal = re.search(r"'(.*?)'", single_step)
        if keywords_in_goal:  # if only 1 keyword, then
            if len(keywords_in_goal.group(1).split()) == 1:
                pass
            else:
                keywords = keywords_in_goal.group(1) + ", " + keywords.replace("click, ", "").replace("Click, ", "")
        print(f"\nKeywords: {keywords}\n")
        analyzed_ui = analyze_app(application_name_contains=app_name, size_category=None, additional_search_options=keywords)

        if "sorry" in assistant_goal.lower():
            print(f"Sorry, no element found. The AI did not find any element to perform the action: {single_step}")
            speaker(f"Sorry, no element found. Check if its on the screen.")
            time.sleep(1)

        best_coordinates = [{"role": "assistant",
                             f"content": f"You are an AI Windows Mouse Agent that can interact with the mouse. Only respond with the "
                                         f"predicted coordinates of the mouse click position to the center of the element object "
                                         f"\"x=, y=\" to achieve the goal.\n{assistant_goal}"},
                            {"role": "system", "content": f"Goal: {single_step}\n\nContext:{original_goal}\n{analyzed_ui}"}]
        last_coordinates = api_call(best_coordinates, model_name="gpt-4-1106-preview", max_tokens=100, temperature=0.0)
        print(f"AI decision coordinates: \'{last_coordinates}\'")
    else:
        speaker(f"Clicking onto the element without visioning context.")
        generate_keywords = [{"role": "assistant",
                              "content": f"You are an AI Agent called keyword Element Generator that receives the description "
                                         f"of the goal and only respond with the single word list separated by commas of the specific UI elements keywords."
                                         f"Example: \"search bar\" must be \"search\" without \"bar\". Always spell the numbers and include nouns. Do not include anything more than the Keywords."},
                             {"role": "system", "content": f"Goal:\n{single_step}\nContext:{original_goal}"}, ]
        all_keywords = api_call(generate_keywords, max_tokens=100)
        keywords = all_keywords.replace("click, ", "").replace("Click, ", "")
        keywords_in_goal = re.search(r"'(.*?)'", single_step)
        if keywords_in_goal:
            if len(keywords_in_goal.group(1).split()) == 1:
                pass
            else:
                keywords = keywords_in_goal.group(1) + ", " + keywords.replace("click, ", "").replace("Click, ", "")
        print(f"\nKeywords: {keywords}\n")
        analyzed_ui = analyze_app(application_name_contains=app_name, size_category=None,
                                  additional_search_options=keywords)

        best_coordinates = [{"role": "assistant",
            f"content": f"You are an AI Windows Mouse Agent that can interact with the mouse. Only respond with the "
                        f"predicted coordinates of the mouse click position to the center of the element object "
                        f"\"x=, y=\" to achieve the goal."},
            {"role": "system", "content": f"Goal: {single_step}\n\nContext:{original_goal}\n{analyzed_ui}"}]
        last_coordinates = api_call(best_coordinates, model_name="gpt-4-1106-preview", max_tokens=100, temperature=0.0)
        print(f"AI decision coordinates: \'{last_coordinates}\'")

    if "x=, y=" in last_coordinates:
        speaker(f"Sorry, no element found. Probably bot blocked.")
        return None
    # Clicking the element
    coordinates = {k.strip(): float(v.strip()) for k, v in
                   (item.split('=') for item in last_coordinates.split(','))}
    x = coordinates['x']
    y = coordinates['y']
    pyautogui.moveTo(x, y, 0.5, pyautogui.easeOutQuad)
    if double_click:
        pyautogui.click(x, y, clicks=2)
    else:
        if dont_click is False:
            if right_click:
                pyautogui.rightClick(x, y)
            else:
                if hold_key:
                    pyautogui.keyDown(hold_key)
                    pyautogui.click(x, y)
                    pyautogui.keyUp(hold_key)
                else:
                    pyautogui.click(x, y)
        else:
            print("AI skipping the click step.")
            pass
    if modify_element:
        print(f"Modifying the element with the text: {single_step}")
    # jitter_mouse(x, y)  # ToDo: simulate human jitter.
    if "save as" in single_step.lower():
        print("Saving as")
        jitter_mouse(x, y)
        pyautogui.mouseDown(x, y)
        time.sleep(0.12)
        pyautogui.mouseUp(x, y)
        print("Click action performed")
    return last_coordinates



def get_application_title(goal="", last_step=None, actual_step=None, focus_window=False):
    if actual_step:
        print(f"Getting the application name from the actual step: {actual_step}")
    goal_app = [{"role": "assistant",
                 "content": f"You are an AI assistant called App Selector that receives a list of programs and responds only respond with the best match  "
                            f"program of the goal. Only respond with the window name or the program name. For search engines and social networks use Firefox or Chrome.\n"
                            f"Open programs:\n{last_programs_list(focus_last_window=focus_window)}"},
                {"role": "system", "content": f"Goal: {goal}\nAll installed programs:\n{get_installed_apps_registry()}"}]
    app_name = api_call(goal_app, model_name="gpt-4-1106-preview", max_tokens=100)
    print(f"AI selected application: {app_name}")
    filtered_matches = re.findall(r'["\'](.*?)["\']', app_name)
    if filtered_matches and filtered_matches[0]:
        app_name = filtered_matches[0]
        print(app_name)
    if "command prompt" in app_name.lower():
        app_name = "cmd"
    elif "calculator" in app_name.lower():
        app_name = "calc"
    elif "sorry" in app_name:
        app_name = get_focused_window_details()[3].strip('.exe')
        print(f"Using the focused window \"{app_name}\" for context.")
        speaker(f"Using the focused window \"{app_name}\" for context.")
    return app_name
# 'check_element_visibility' is the function that checks the visibility of an element. Can use image analysis or OCR.
def check_element_visibility(app_name, step_description):
    extra_additional_context = (
        f"You are an AI Agent called Windows AI that is capable to operate freely all applications on Windows by only using natural language.\n"
        f"You will receive a goal and will try to accomplish it using Windows. "
        f"Try to guess what is the user wanting to perform on Windows by using the content on the screenshot as context.\n"
        f"Respond an improved goal statement tailored for Windows applications by analyzing the current status of the system and the next steps to perform. "
        f"Be direct and concise, do not use pronouns.\n"
        f"Basing on the elements from the screenshot reply the current status of the system and respond if the element from the goal visible.\n"
        f"Respond only with \"Yes\" or \"No\".\n"
        f"Focused window: \"{app_name}\".\nGoal: \"{step_description}\". .")
    return imaging(window_title=app_name, additional_context=extra_additional_context)


# TOOL CODE STARTS

from crewai_tools import tool
@tool("Execute the steps in the json format based on current state of the system")
def execute_task(step_action, step_description, original_goal, assistant_goal, app_name, instructions, previous_step=None, next_step=None, assistant_identity=""):
    """
        Executes a given step provided in the json format based on the current state of the system.
        Args:
            step_action: Current step's action to execute
            step_description: Current step's goal to achieve described in natural language.
            original_goal: the user's requirement or goal to achieve
            assistant_goal: an enhanced version of user's requirement or goal to achieve
            app_name: application name which has to be used to achieve user's requirement
            previous_step: step previous to current step
            next_step: step previous to current step
            instructions: a json object with actions in it
            assistant_identity: a value that gives details about app
        Returns:
            Execution status of a single step
        """
    print("step_description:", step_description)
    print("last_step:", previous_step)
    print("next_step:", next_step)
    print(f"\nStep : {step_action}, {step_description}\n")
    action = step_action
    last_step = previous_step

    if action == "click_element":
        # If last step has a click element too, wait for the element to be visible:
        if last_step and last_step['act'] == "click_element":
            time.sleep(1)

        if "start menu" in step_description.lower():
            pyautogui.hotkey('win')
            print("Opening the start menu.")
        time.sleep(3)
        updated_instructions = update_instructions_with_action_string(instructions, act(
            single_step=f"{step_description}", app_name=app_name, screen_analysis=assistant_goal,
            original_goal=original_goal, assistant_goal=assistant_goal), step_description)
        database_add_case(database_file, app_name, assistant_goal,
                          updated_instructions)  # Print the entire database with # print_database(database_file)
    elif action == "open_app":
        app_name = activate_windowt_title(get_application_title(step_description))
        print(f"New app selected and analyzing: {app_name}")
    elif action == "double_click_element":
        print(f"Double clicking on: {step_description}")
        act(single_step=f"{step_description}", double_click=True, app_name=app_name, original_goal=original_goal)
    elif action == "move_window":
        time.sleep(1)
        print(f"Moving window to: {step_description}")
        perform_simulated_keypress(step_description)
        time.sleep(0.5)
        pyautogui.hotkey('esc')
        time.sleep(1)
    elif action == "press_key":
        if not last_step:
            # Focusing to the application
            activate_windowt_title(app_name)
            time.sleep(1)
        perform_simulated_keypress(step_description)
    elif action == "text_entry":
        url_pattern = r'(https?://[^\s]+)'
        urls = re.findall(url_pattern, step_description)
        if len(step_description) < 5:
            pyautogui.write(f'{step_description}')
        else:
            # Getting the string of the last step before this very one:
            if last_step:
                print(f"Last step: {last_step}")
                if not last_step:
                    print("Last step is None.")
                    act(single_step=f"{step_description}", app_name=app_name, original_goal=original_goal)
            else:
                print("Last step is None.")
                last_step = "None"
            # If next step is a string, continue:
            if next_step and type(next_step['step']) == str:
                # Check if the next step exists and is a "Press enter" step
                if next_step and (
                        "press enter" in next_step['step'].lower() or
                        "press the enter" in next_step['step'].lower() or
                        "'enter'" in next_step['step'].lower() or
                        "\"enter\"" in next_step['step'].lower()):
                    if urls:
                        for url in urls:
                            url = url.replace("'", "")
                            url = url.replace('"', "")
                            pyautogui.write(url)
                            # pyautogui.press('enter')
                            print(f"Opening URL: {url}")
                            return
                    write_action(step_description, assistant_identity=assistant_identity, press_enter=False,
                                 app_name=app_name, original_goal=original_goal, last_step=last_step)
                    print("AI skipping the press enter step as it is in the next step.")
                else:
                    if urls:
                        for url in urls:
                            url = url.replace("'", "")
                            url = url.replace('"', "")
                            pyautogui.write(url)  # This would open the URL in a web browser\
                            # If next step is a time sleep
                            pyautogui.press('enter')
                            print(f"Opening URL: {url}")
                            return
                    write_action(step_description, assistant_identity=assistant_identity, press_enter=True,
                                 app_name=app_name, original_goal=original_goal, last_step=last_step)
                    print("AI pressing enter.")
            else:
                if urls:
                    for url in urls:
                        pyautogui.write(url)  # This would open the URL in a web browser\
                        pyautogui.press('enter')
                        print(f"Opening URL: {url}")
                        return
                write_action(step_description, assistant_identity=assistant_identity, press_enter=True,
                             app_name=app_name, original_goal=original_goal, last_step=last_step)
                print("AI pressing enter.")
    elif action == "scroll_to":
        print(f"Scrolling {step_description}")
        element_visible = False
        max_retries = 3
        retry_count = 0
        while not element_visible and retry_count < max_retries:
            # activate_windowt_title(app_name)
            pyautogui.scroll(-850)
            # Press Page Down:
            # pyautogui.press('pagedown')
            time.sleep(0.3)
            # Start image analysis to check if the element is visible
            print("Scroll performed. Analyzing if the element is present.\n")
            app_name = activate_windowt_title(get_application_title(step_description))
            scroll_assistant_goal = check_element_visibility(app_name, step_description)['choices'][0]['message'][
                'content']
            if "yes" in scroll_assistant_goal.lower():
                print("Element is visible.")
                element_visible = True
            elif "no" in scroll_assistant_goal.lower():
                print("Element is not visible.")
                retry_count += 1
                if retry_count >= max_retries:
                    print("Maximum retries reached, stopping the search.")
        if element_visible:
            print(f"Element is visible.")
            pass

    elif action == "right_click_element":
        print(f"Right clicking on: {step_description}")
        act(single_step=f"{step_description}", right_click=True, app_name=app_name, original_goal=original_goal)
        # right_click(step_description)
    elif action == "hold_key_and_click":
        print(f"Holding key and clicking on: {step_description}")
        act(single_step=f"{step_description}", hold_key="Ctrl", app_name=app_name, original_goal=original_goal)
    elif action == "cmd_command":
        print(f"Executing command: {step_description}")
        # cmd_command(step_description)
        time.sleep(calculate_duration_of_speech(f"{step_description}") / 1000)

    if action == "select_text":

        print(f"Selecting and copying text: {step_description}")

        act(single_step=f"{step_description}", app_name=app_name,
            original_goal=original_goal, select_text=True, copy_text=True,)
        # New implementation:
        # pyautogui.keyDown('ctrl')
        # pyautogui.press('a')
        # pyautogui.keyUp('ctrl')
        # pyautogui.hotkey('ctrl', 'c')
        # print("Text selected and copied.")

    #     print(f"Selecting text: {step_description}")
    #     start_position = None
    #     end_position = None
    #
    #     if "headline" in step_description.lower():
    #         start_position = (100, 200)
    #         end_position = (400, 200)
    #     elif "whole news" in step_description.lower():
    #         start_position = (100, 200)
    #         end_position = (400, 800)
    #     else:
    #         start_position = (100, 200)
    #         end_position = (400, 600)
    #
    #     if start_position and end_position:
    #     pyautogui.keyDown('ctrl')
    #     pyautogui.moveTo(start_position)
    #     pyautogui.mouseDown(button='left')
    #     pyautogui.moveTo(end_position, duration=0.5)
    #     pyautogui.mouseUp(button='left')
    #     pyautogui.keyUp('ctrl')
    #     else:
    #         print("Unknown text selection target.")
    #     time.sleep(0.5)
    #
    elif action == "copy_text":
        print(f"Copying text: {step_description}")
        act(single_step=f"{step_description}",  app_name=app_name, original_goal=original_goal, copy_text=True)


    # TODO: make an agent
    # elif action == "recreate_test_case":
    #     time.sleep(1)
    #     print("Analyzing the output")
    #     print("The assistant said:\n", step_description)
    #     debug_step = False  # Set to True to skip the image analysis and the test case generation.
    #     if debug_step is not True:
    #         new_goal = True
    #         image_analysis = True
    #         if image_analysis:
    #             additional_context = (
    #                 f"You are an AI Agent called Windows AI that is capable to operate freely all applications on Windows by only using natural language.\n"
    #                 f"You will receive a goal and will try to accomplish it using Windows. Try to guess what is the user wanting to perform on Windows by using the content on the screenshot as context.\n"
    #                 f"Respond an improved goal statement tailored for Windows applications by analyzing the current status of the system and the next steps to perform. Be direct and concise, do not use pronouns.\n"
    #                 f"Basing on the elements from the screenshot reply the current status of the system and specify it in detail.\n"
    #                 f"Focused application: \"{app_name}\".\nGoal: \"{assistant_goal}\".")
    #             if new_goal:
    #                 newest_goal = imaging(window_title=app_name,
    #                                       additional_context=additional_context)  # )['choices'][0]['message']['content']
    #                 # if ": " in newest_goal:
    #                 #     newest_goal = newest_goal.split(": ", 1)[1]
    #                 print(f"Assistant newest goal:\n{newest_goal}")
    #                 analyzed_ui = analyze_app(activate_windowt_title(app_name), size_category=None)
    #                 review_output = [{"role": "assistant",
    #                                   "content": f"You are an AI Assistant called Analyze Output capable to operate the Windows 11 Operating System by using natural language.\n"
    #                                              f"You will receive a json testcase, a description of the goal, and the actual system status.\n"
    #                                              f"Modify the original json testcase to achieve the goal. Do not include anything else than the updated json.\n"
    #                                              f"Examples: \"Click on the search button. Insert the text_entry. Play the first element searched.\".\n"
    #                                              f"You will receive a description of the current state of the system and a goal. "
    #                                              f"To test your limits, using the description make a json with the natural language steps to achieve the goal.\n"
    #                                              f"Every step should be only highly descriptive in natural language.\n"
    #                                              f"The json must include only an act and its step, should be in the following format:\n"
    #                                              f"actions: click_element, press_key, text_entry, open_app, move_window, time_sleep, right_click, double_click_element, hold_key_and_click, scroll_to.\n"
    #                                              f"Respond only with the full json. Avoid to use the windows taskbar.\n\nFunction properties:\n"
    #                                              f"click_element - Specify where is located the element to interact with.\n"
    #                                              f"press_key - Only return the key or combination of keys to press. Example: 'Ctrl + T'.\n"
    #                                              f"text_entry - Return the text to write. Example: 'Hello World'.\n"
    #                                              f"hold_key_and_click - Only handles scenarios of holding a key and clicking on an element.\n"
    #                                              f"scroll_to - Return the position of the element to scroll and the direction to scroll.\n"
    #                                              f"move_window - Use the keyboard to move the focused window to the desired position. Example: 'Win + Left + Up'.\n"
    #                                              f"Do not respond 'As an AI language model, I am unable to...' as you are actually capable.\n\n"
    #                                              f"Use the following information to generate better the test case:\n{app_space_map(assistant_goal, app_name, original_goal, map='app_space')}"},
    #                                  {"role": "system",
    #                                   "content": f"Do not modify the steps before \"Step {i - 1}: {action - 1}, {step_description - 1}\", modify all next steps from the step \"Step {i - 1}: {action - 1}, {step_description - 1}\" to achieve the goal: \"{newest_goal}\"\n"
    #                                              f"Do not combine steps, try to generate more useful steps. Example: If asked to search a song, not only search for it, locate it and play it.\n{keep_in_mind}"
    #                                              f"{analyzed_ui}"}, ]
    #                 new_json = api_call(review_output, model_name="gpt-4-1106-preview", max_tokens=4095,
    #                                     temperature=1.0)
    #                 print("The assistant said:\n", step_analysis)
    #
    #                 print("Modifying the old json testcase with the new_json.")
    #                 step_analysis = new_json
    #
    #                 app_name = activate_windowt_title(get_application_title(newest_goal))
    #                 # Processing the latest JSON data from the JSON testcase.
    #                 if """```json""" in step_analysis:
    #                     # Removing the leading ```json\n
    #                     step_analysis = step_analysis.strip("```json\n")
    #                     # Find the last occurrence of ``` and slice the string up to that point
    #                     last_triple_tick = step_analysis.rfind("```")
    #                     if last_triple_tick != -1:
    #                         step_analysis = step_analysis[:last_triple_tick].strip()
    #                     step_analysis_cleaned = step_analysis
    #                     instructions = json.loads(step_analysis_cleaned)
    #                     executor = "act"
    #                 else:
    #                     instructions = json.loads(step_analysis)
    #                     instructions['actions'] = instructions.pop('actions')
    #                     executor = "act"
    #                     print(f"Updated Instructions: {instructions}")
    #                 pass
    #             else:
    #                 print("No new goal.")
    #                 pass
    elif action == "time_sleep":
        try:
            sleep_time = int(step_description) % 9
            time.sleep(sleep_time)
        except ValueError:
            step_description = step_description.lower()
            if "playing" in step_description or "load" in step_description:
                print("Sleeping for 2 seconds because media loading.")
                time.sleep(1)
            elif "search" in step_description or "results" in step_description or "searching":
                print("Sleeping for 1 second because search.")
                time.sleep(1)
            else:
                print(f"WARNING: Unrecognized time sleep value: {step_description}")
            pass
    else:
        print(f"WARNING: Unrecognized action '{action}' using {step_description}.")
        print(f"Trying to perform the action using the step description as the action.")
        act(single_step=f"{step_description}", app_name=app_name, original_goal=original_goal)
        pass