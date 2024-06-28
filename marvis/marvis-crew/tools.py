from textwrap import dedent
from crewai import Task
from utils.last_app import last_programs_list
from utils.window_focus import get_installed_apps_registry
from langchain.tools import tool
from agents import MarvisAgents
import re
from utils.additional import get_focused_window_details
from utils.additional import get_screen_image
import requests

Agents = MarvisAgents()

api_key = "TO BE DEFINED LATER"

class WindowsExpertTools:
    @tool("Return the best matching app title")
    def get_relevant_app_title(self, goal, focus_window=True):
        all_program_list = last_programs_list(focus_last_window=focus_window)
        installed_app_registry = get_installed_apps_registry()
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
    def get_enhanced_goal_statement(self, goal, focused_app):
        screenshot = get_screen_image(focused_app, additional_context=None, x=None, y=None, screenshot_size="Full Screen")

        additional_context = (
            f"You are an AI Agent called Windows AI that is capable to operate freely all applications on Windows by only using natural language.\n"
            f"You will receive a goal and will try to accomplish it using Windows. Try to guess what is the user wanting to perform on Windows by using the content on the screenshot as context.\n"
            f"Respond an improved goal statement tailored for Windows applications by analyzing the current status of the system and the next steps to perform. Be direct and concise, do not use pronouns.\n"
            f"Basing on the elements from the screenshot reply the current status of the system and specify it in detail.\n"
            f"Focused application: \"{focused_app}\".\nGoal: \"{goal}\"."
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{additional_context}"
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
        json_response = response.json()

        return json_response