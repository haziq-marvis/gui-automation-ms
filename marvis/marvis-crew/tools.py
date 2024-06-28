from textwrap import dedent
from crewai import Task
from utils.last_app import last_programs_list
from utils.window_focus import get_installed_apps_registry
from langchain.tools import tool
from agents import MarvisAgents
import re
from utils.additional import get_focused_window_details


class WindowsExpertTools:
    @tool("Return the best matching app title")
    def get_relevant_app_title(self, goal, focus_window=True):
        all_program_list = last_programs_list(focus_last_window=focus_window)
        installed_app_registry = get_installed_apps_registry()
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

    @tool("Return the enhanced goal based on current state of the system")
    def get_enhanced_goal_statement(self, goal, focus_window=True):