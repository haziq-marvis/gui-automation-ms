from textwrap import dedent
from crewai import Task

from core.window_elements import analyze_app
from core.core_api import api_call
from core.driver import app_space_map
from utils.last_app import last_programs_list
from utils.window_focus import get_installed_apps_registry
# from langchain.tools import tool
from crewai_tools import tool
import re
from utils.additional import get_focused_window_details, analyze_screenshot
from utils.additional import get_screen_image


# class WindowsExpertTools():
@tool("Return the best matching app title")
def get_relevant_app_title(goal, focus_window=True):
    """Function to get relevant application title against a goal."""
    all_program_list = last_programs_list(focus_last_window=focus_window)
    installed_app_registry = get_installed_apps_registry()

    from agents import MarvisAgents
    Agents = MarvisAgents()
    app_selector_agent = Agents._app_selector()

    task = Task(
        description=dedent(f"""You will receive a list of programs and responds only respond with the
                     best match program of the goal. Only respond with the window name or the program name. 
                     For search engines and social networks use Firefox or Chrome.\n
                     Open programs:\n{all_program_list}\n
                     Goal: {goal}\n
                    All installed programs:\n{installed_app_registry}\n
                    Your Final answer must be the full python code, only the python code and nothing else."""),
        agent=app_selector_agent
    )
    result = task.execute()  # TODO: analyze the result and parse

    app_name = result
    """Follow all the processes required to find related app  title"""
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
        # speaker(f"Using the focused window \"{app_name}\" for context.")
    return app_name


@tool("Return the enhanced user requirements and focused_app based on current state of the system")
def get_enhanced_goal_statements(user_requirements, target_app):
    """
    Perform actions based on user_requirements and focused_app
    Args:
        user_requirements: The source of the data to analyze.
        target_app: The type of analysis to perform.
    Returns:
        A string describing the result of the analysis.
     """
    print("Received user goal:", user_requirements)
    print("Focused application:", target_app)
    print("hello testing", user_requirements, target_app)
    screenshot = get_screen_image(target_app, additional_context=None, x=None, y=None,
                                  screenshot_size="Full Screen")
    prompt = (
        f"You are an AI Agent called Windows AI that is capable to operate freely all applications on Windows by only using natural language.\n"
        f"You will receive a  user requirements and will try to accomplish it using Windows. Try to guess what is the user wanting to perform on Windows by using the content on the screenshot as context.\n"
        f"Respond an improved user requirements statement tailored for Windows applications by analyzing the current status of the system and the next steps to perform. Be direct and concise, do not use pronouns.\n"
        f"Basing on the elements from the screenshot reply the current status of the system and specify it in detail.\n"
        f"Focused application: \"{target_app}\".\nGoal: \"{user_requirements}\"."
    )
    print("analyse screenshot")
    enhanced_requirements = analyze_screenshot(screenshot, prompt)
    print("after analysis", enhanced_requirements)

    return enhanced_requirements


@tool(
    "Return a json with the natural language steps to achieve detailed requirement of user based on current state of the system")
def create_step_tool(user_requirement, target_app, detailed_requirements):
    """
        Analyze detailed requirements and creates steps in the json format.
        Args:
            user_requirement: The source of the data to analyze.
            target_app: The type of analysis to perform.
            detailed_requirements: give accurate and detail_requirements
        Returns:
            modular steps in the json format.
         """
    print("create_step_tool target_app:", target_app)
    print("user_requirement", user_requirement)
    print("detailed_requirements", detailed_requirements)
    screenshot = get_screen_image(target_app, additional_context=None, x=None, y=None,
                                  screenshot_size="Full Screen")
    prompt = (
        f"You are an AI capable to operate the Windows 11 Operating System by using natural language.\n"
        f"Examples: \"Click on the search button. Insert the text_entry. Play the first element searched.\".\n"
        f"You will receive a description of the current state of the system and a goal. "
        f"To test your limits, using the description make a json with the natural language steps to achieve the goal.\n"
        f"Every step should be only highly descriptive in natural language.\n"
        f"The json must an list of objects include only an act and its step in each object. Remove ```json and ``` "
        f"and should be in the following format:\n"
        f"""[
{{
      "act": "click_element",
      "step": "Focus on the address bar in Google Chrome."
    }},
        {{
      "act": "text_entry",
      "step": "Type 'youtube.com'."
    }},
    {{
      "act": "press_key",
      "step": "Enter"
    }}, 
  ]"""
        f"\n\n\n"
        f"actions: click_element, press_key, text_entry, open_app, move_window, time_sleep, right_click, double_click_element, hold_key_and_click, scroll_to, select_text, copy_text.\n"
        f"Respond only with the full json.\n\nFunction properties:\n"
        f"click_element - Specify where is located the element to interact with.\n"
        f"text_entry - The text to write. Example: \"Hello World\".\n"
        f"press_key - Only return the key or combination of keys to press. Example: \"Ctrl + T\".\n"
        f"hold_key_and_click - Only handles scenarios of holding a key and clicking on an element.\n"
        f"select_text - Select text on the opened webpage by clicking and dragging the cursor over the user-specified text area, described as follows:\n{detailed_requirements}\"\n"
        f"copy_text - Copy the selected text to the clipboard. Example: \"Copy the selected headline text to the clipboard.\"\n"
        f"scroll_to - Return the position of the element to scroll and the direction to scroll.\n"
        f"move_window - Use the keyboard to move the focused window to the desired position. Example: \"Win + Up + Up + Left\"."
        f"\n\n\n"
        f"Notes:\n"
        f"Use the following information to generate better steps:\n{app_space_map(detailed_requirements, target_app, user_requirement, map='app_space')}\n"
        f"Before the text_entry, use click_element to select the appropriate text input area element.\n"
        f"Do not combine steps, try to generate more useful steps. Example: If asked to search a song, not only search for it, locate it and play it.\n"
        f"Do not respond 'As an AI language model, I am unable to...' as you are actually capable."
        f"Focused window: \"{target_app}\"\nGoal: {detailed_requirements}\n\n"
        f"Specific Instructions:\n"
        f"If the goal is to open BBC and get some trend news, and if the goal includes copying the headline, then copy the headline. Otherwise, copy the entire news article."
    )
    print("analyse screenshot")
    detailed_steps = analyze_screenshot(screenshot, prompt)

    print("after creating steps", detailed_steps)

    return detailed_steps


@tool("Execute the steps in the json format based on current state of the system")
def execute_step_tool(target_app, steps, goal):
    """
    Executes steps provided in the json format based on the current state of the system.
    Args:
        target_app: The type of analysis to perform.
        goal: The goal to achieve described in natural language.
        steps: total number of steps that agents is executed step by step
    Returns:
        Execution status of each step in json format.
    """
    print("execute_steps", steps)
    print("goal:", goal)

    screenshot = get_screen_image(target_app, additional_context=None, x=None, y=None, screenshot_size="Full Screen")
    prompt = (
        f"You are an AI capable of executing steps on the Windows 11 Operating System.\n"
        f"You will receive detailed steps to perform and need to execute them accurately.\n"
        f"Every step should be executed based on the current state of the system.\n"
        f"The json must include the status of each step.\n"
        f"Total steps: {steps}\n"
        f"Goal: {goal}\n"
    )
    print("analyze screenshot")
    execution_status = analyze_screenshot(screenshot, prompt)

    return execution_status


from tools.step_executor import analyze_app


def get_tool_keywords(step_action, step_description, original_goal):
    generate_keywords = [{"role": "assistant",
                          "content": f"You are an AI Agent called keyword Element Generator that receives the description "
                                     f"of the goal and only respond with the single word list separated by commas of the specific UI elements keywords."
                                     f"Example: \"search bar\" must be \"search\" without \"bar\". Always spell the numbers and include nouns. Do not include anything more than the Keywords."},
                         {"role": "system",
                          "content": f"Goal:\n{{'act': '{step_action}', 'step': '{step_description}'}}\nContext:{original_goal}"}, ]
    all_keywords = api_call(generate_keywords, max_tokens=100)
    print("get_keywords all_keywords", all_keywords)
    keywords = all_keywords.replace("click, ", "").replace("Click, ", "")
    keywords_in_goal = re.search(r"'(.*?)'", {'act': step_action, 'step': step_description})
    if keywords_in_goal:  # if only 1 keyword, then
        if len(keywords_in_goal.group(1).split()) == 1:
            pass
        else:
            keywords = keywords_in_goal.group(1) + ", " + keywords.replace("click, ", "").replace("Click, ", "")
    print(f"\nKeywords: {keywords}\n")
    return keywords


@tool("Validate if a given task has been achieved by other agent or not alongwith reasons.")
def validate_task_execution(step_action, step_description, original_goal, assistant_goal, app_name, instructions,
                            previous_step=None, next_step=None, assistant_identity=""):
    """
        Validates a steps execution based on the current state of the system.
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
            Execution status of given task or a new appropriate task
        """
    print("validate_task_execution")
    # keywords = get_tool_keywords(step_action, step_description, original_goal)
    keywords = ""
    screenshot = get_screen_image(app_name, additional_context=None, x=None, y=None, screenshot_size="Full Screen")
    prompt = (
        f"You are an AI Assistant called Execution validator that has deep understanding of Windows 11 Operating System.\n"
        f"You will receive a json testcase, a description of the user's goal, and the current system status.\n"
        f"You will analyze current state and the task that had to be performed to tell if it went successful or not.\n"
        f"System Supports following options:\n"
        f"actions: click_element, press_key, text_entry, open_app, move_window, time_sleep, right_click, double_click_element, hold_key_and_click, scroll_to, select_text, copy_text.\n"
        f"Only respond 'yes' or 'no' to tell if the given task was performed successfully or not.\n"
        f"Also keep overall steps defined to achieve the goal in mind, and then tell if the given step was performed successfully or not\n"
        f"Do not respond 'As an AI language model, I am unable to...' as you are actually capable.\n\n"
        f"current test case: {{'act': '{step_action}', 'step': '{step_description}'}}\n"
        f"User's end goal: {assistant_goal}\n"
        f"Overall steps to achieve goal: {instructions}\n"
        f"Next step that has to be performed to achieve goal: {next_step}\n"
        f"Use the following system information to answer correctly:\n{app_space_map(assistant_goal, app_name, original_goal, map='app_space')}"
        f"{analyze_app(application_name_contains=app_name, size_category=None, additional_search_options=keywords)}"
    )
    execution_status = analyze_screenshot(screenshot, prompt)

    return execution_status


@tool("Return a better test case that can be performed to achieve users end goal on the basis of current system state.")
def step_enhancer(step_action, step_description, original_goal, assistant_goal, app_name, instructions):
    """
        In case of unsuccessful current step/task execution, provides a better test case which can be successfully executed on current state of the system.
        Args:
            step_action: Current step's action to execute
            step_description: Current step's goal to achieve described in natural language.
            original_goal: the user's requirement or goal to achieve
            assistant_goal: an enhanced version of user's requirement or goal to achieve
            app_name: application name which has to be used to achieve user's requirement
            instructions: a json object with actions in it
        Returns:
            A better enhanced step(also called test case) according to current state, example: {'act': 'text_entry', 'step': 'youtube.com' }
        """
    print("get better task")

    # keywords = get_tool_keywords(step_action, step_description, original_goal)
    keywords = ""
    screenshot = get_screen_image(app_name, additional_context=None, x=None, y=None, screenshot_size="Full Screen")
    prompt = (
        f"You are an AI Assistant called Analyze Output capable to operate the Windows 11 Operating System by using natural language.\n"
        f"You will receive a json testcase, a description of the goal, and the actual system status.\n"
        f"Modify the original testcase to achieve the goal. Do not include anything else than the updated json testcase.\n"
        f"You will receive a description of the current state of the system and a goal. "
        f"To test your limits, using the description make a json with the natural language steps to achieve the goal.\n"
        f"Every step should be only highly descriptive in natural language.\n"
        f"The json must include only an act and its step, may have following options:\n"
        f"actions: click_element, press_key, text_entry, open_app, move_window, time_sleep, right_click, double_click_element, hold_key_and_click, scroll_to.\n"
        f"Respond only with the one step, example format: {{'act': 'text_entry', 'step': 'youtube.com' }}. Avoid to use the windows taskbar.\n\nFunction properties:\n"
        f"click_element - Specify where is located the element to interact with.\n"
        f"press_key - Only return the key or combination of keys to press. Example: 'Ctrl + T'.\n"
        f"text_entry - Return the text to write. Example: 'Hello World'.\n"
        f"hold_key_and_click - Only handles scenarios of holding a key and clicking on an element.\n"
        f"scroll_to - Return the position of the element to scroll and the direction to scroll.\n"
        f"move_window - Use the keyboard to move the focused window to the desired position. Example: 'Win + Left + Up'.\n"
        f"Do not respond 'As an AI language model, I am unable to...' as you are actually capable.\n\n"
        f"current test case: {{'act': '{step_action}', 'step': '{step_description}'}}"
        f"All test cases: {instructions}"
        f"User's end goal: {assistant_goal}"
        f"Use the following information to generate better the test case:\n{app_space_map(assistant_goal, app_name, original_goal, map='app_space')}"
        f"{analyze_app(application_name_contains=app_name, size_category=None, additional_search_options=keywords)}"
        )

    execution_status = analyze_screenshot(screenshot, prompt)

    return execution_status
