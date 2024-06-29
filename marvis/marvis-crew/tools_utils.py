from textwrap import dedent
from crewai import Task

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


@tool("Return a json with the natural language steps to achieve detailed requirement of user based on current state of the system")
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
        f"The json must include only an act and its step, should be in the following format:"
        f"\n\n\n"
        f"actions: click_element, press_key, text_entry, open_app, move_window, time_sleep, right_click, double_click_element, hold_key_and_click, scroll_to.\n"
        f"Respond only with the full json.\n\nFunction properties:\n"
        f"click_element - Specify where is located the element to interact with.\n"
        f"text_entry - The text to write. Example: \"Hello World\".\n"
        f"press_key - Only return the key or combination of keys to press. Example: \"Ctrl + T\".\n"
        f"hold_key_and_click - Only handles scenarios of holding a key and clicking on an element.\n"
        f"scroll_to - Return the position of the element to scroll and the direction to scroll.\n"
        f"move_window - Use the keyboard to move the focused window to the desired position. Example: \"Win + Up + Up + Left\"."
        f"\n\n\n"
        f"Notes:\n"
        f"Use the following information to generate better steps:\n{app_space_map(detailed_requirements, target_app, user_requirement, map='app_space')}\n"
        f"Before the text_entry, use click_element to select the appropriate text input area element.\n"
        f"Do not combine steps, try to generate more useful steps. Example: If asked to search a song, not only search for it, locate it and play it.\n"
        f"Do not respond 'As an AI language model, I am unable to...' as you are actually capable."
        f"Focused window: \"{target_app}\"\nGoal: {detailed_requirements}"
    )
    print("analyse screenshot")
    detailed_steps = analyze_screenshot(screenshot, prompt)

    print("after creating steps", detailed_steps)

    return detailed_steps