from textwrap import dedent
from crewai import Task


class MarvisTasks():
    def _get_app_title_task(self, agent, goal, focus_window, programs_list, installed_app_registry):
        return Task(
            description=dedent(f"""You will receive a list of programs and responds only respond with the
                 best match program of the goal. Only respond with the window name or the program name. 
                 For search engines and social networks use Firefox or Chrome.\n
                 Open programs:\n{programs_list}\n
                 Goal: {goal}\n
                All installed programs:\n{installed_app_registry}\n
			    Your Final answer must be the full python code, only the python code and nothing else."""),
            agent=agent
        )

    def execute_enhanced_goal_task(self, task, goal, focused_app):
        enhanced_goal_statement = task.agent.tools['get_enhanced_goal_statement'](goal, focused_app)
        return enhanced_goal_statement['choices'][0]['message']['content']
