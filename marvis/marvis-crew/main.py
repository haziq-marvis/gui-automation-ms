from utils.window_focus import activate_windowt_title, get_installed_apps_registry, get_open_windows
from agents import MarvisAgents
from tasks import MarvisTasks
from dotenv import load_dotenv
import os
load_dotenv()

openai_api_key=os.getenv("OPENAI_API_KEY")

def main():
    idea = input("# Describe what you want Marvis to do:\n\n")

    agents = MarvisAgents()
    tasks = MarvisTasks()

    # focus_window = activate_windowt_title(idea)
    # programs_list = get_open_windows()
    # installed_app_registry = get_installed_apps_registry()

    # app_selector_agent = agents._app_selector()
    # app_title_task = tasks._get_app_title_task(app_selector_agent, idea, focus_window, programs_list, installed_app_registry)
    # app_title = app_title_task.execute()
    # focus_window="chrome"
    # goal_enhancer_agent = agents._goal_enhancer()
    # enhanced_goal_task = tasks._get_enhanced_goal_statement(goal_enhancer_agent, idea, focus_window)
    # enhanced_goal = enhanced_goal_task.execute()

    focus_window = "chrome"
    goal_enhancer_agent = agents._goal_enhancer()
    enhanced_goal_task = tasks._get_enhanced_goal_statement(goal_enhancer_agent, idea, focus_window)
    enhanced_goal = tasks.execute_enhanced_goal_task(enhanced_goal_task, idea, focus_window)
    print("Improved Goal Statement:", enhanced_goal)


    # print(f"AI Analyzing: {app_title}")
    # print(f"Enhanced Goal: {enhanced_goal}")

if __name__ == "__main__":
    main()