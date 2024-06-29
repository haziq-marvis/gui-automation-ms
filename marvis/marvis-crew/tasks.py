from textwrap import dedent
from typing import ClassVar
from agents import MarvisAgents
from crewai import Task
from crewai.task import TaskOutput
from utils.window_focus import activate_windowt_title
from tools.get_app_title import process_app_title_result

def post_app_title(output: TaskOutput):
    target_app = output.raw_output
    print("Opening given window", target_app)
    print("applying additional logic")
    target_app = process_app_title_result(target_app)
    print("Opening app")
    activate_windowt_title(target_app)
    output.raw_output = target_app

class MarvisTasks():
    def get_app_title_task(self, agent, user_requirements, programs_list, installed_app_registry, focused_app=None):
        return Task(
            description=dedent(f"""
            **Task**: Return relevant application to perform user_requirements
            **Description**: You will receive a list of programs and responds only respond with the
                 best match program of the goal. Only respond with the exact window name or the program name. 
                 For search engines and social networks use Firefox or Chrome.\n
                 Open programs:\n{programs_list}\n
                 User's End Goal: {user_requirements}\n
                All installed programs:\n{installed_app_registry}\n
                
            **Parameters**: 
            - user_requirements: {user_requirements}

            **Note**:
            Only choose an open window name or installed apps if not open already from the given option, do not suggest anything else. You ll get 100$ for correct answer."""),
            agent=agent,
            expected_output="target_app: Title of installed application or open window that can be used to perform user requirements",
            callback=post_app_title
        )

    def enhanced_goal_task(self, agent, user_requirement, target_app):
        return Task(
            description=dedent(f"""An efficient assistant who has access to a tool that can analyze screen and give enhanced goal 'get_enhanced_goal_statement_tool', you use the tool to share enhanced goal on the user_requirements: {user_requirement} and target_app: {target_app}
    
            **Parameters**: 
            - user_requirements: {user_requirement}
            - target_app: {target_app}
            **Note**:
            Only choose an open window name or installed apps if not open already from the given option, do not suggest anything else. You ll get 100$ for correct answer.
            """),
            expected_output=f"Enhanced goal statement according to user_requirements: {user_requirement} and target_app: {target_app} using tools.",
            agent=agent
        )

    def detailed_steps_creator(self, agent, user_requirement, target_app, detailed_requirements):
        return Task(
            description=dedent(
                f"""An efficient assistant who has access to a tool that can take detailed requirements 'create_step_tool', you use the tool to create detailed json with the natural language steps to achieve the goal.

            **Parameters**: 
            - user_requirements: {user_requirement}
            - target_app: {target_app}
            - detailed_requirements: {detailed_requirements}
            **Note**:
            Share all the detailed steps back with me, do not remove anything. You ll get 100$ for complete answer.
            """),
            expected_output=f"Response from the utility form of a json to achieve the goal.The json must include only an act and its step, should be in the format created by the tool.",
            agent=agent
        )


