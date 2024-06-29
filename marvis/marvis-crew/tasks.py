from textwrap import dedent
from typing import ClassVar
from agents import MarvisAgents
from crewai import Task
from tools import get_enhanced_goal_statement
from pydantic import BaseModel, Field


class CustomToolTask(Task):
    user_input: str = Field(default="")
    focused_app: str = Field(default="")
    custom_tool: any = Field(default=None)
    def run(self):
        print("testing run")
        result = self.agent.use_tool(self.custom_tool, user_input=self.user_input, focused_app=self.focused_app)

class MarvisTasks():
    def _get_app_title_task(self, agent, goal, programs_list, installed_app_registry, focused_app=None):
        return Task(
            description=dedent(f"""You will receive a list of programs and responds only respond with the
                 best match program of the goal. Only respond with the window name or the program name. 
                 For search engines and social networks use Firefox or Chrome.\n
                 Open programs:\n{programs_list}\n
                 Goal: {goal}\n
                 focused_app: {focused_app}
                All installed programs:\n{installed_app_registry}\n
			    Your Final answer must be the full python code, only the python code and nothing else."""),
            agent=agent,
            expected_output="title of installed application or window."
        )

    def enhanced_goal_task(self, agent, user_requirement, focused_app):
        return Task(
            # user_input=user_input,
            # focused_app=focused_app,
            # custom_tool=get_enhanced_goal_statement,
            description=dedent(f"""An expert Windows User who can take a look at given screen and a goal using tool and return enhanced goalaccording to user_requirements: {user_requirement} and focused_app: {focused_app}."""),
            expected_output=f"Enhanced goal statements according to user_requirements: {user_requirement} and focused_app: {focused_app}",
            agent=agent
        )


