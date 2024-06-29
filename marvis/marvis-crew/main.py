from agents import MarvisAgents
from utils.last_app import last_programs_list
from utils.window_focus import get_installed_apps_registry
from tasks import MarvisTasks
from dotenv import load_dotenv
import os
from crewai import Crew
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


def main():
    user_requirements = input("# Describe what you want Marvis to do:\n\n")
    agents = MarvisAgents()
    tasks = MarvisTasks()

    # define agent
    get_relevant_app_title_agent = agents.app_selector()  # TODO: assume its working fine
    get_enhanced_goal_agent = agents._goal_enhancer()
    step_creator_agent = agents.step_creator()

    # define tasks
    focus_window = None

    get_app_title_task = tasks.get_app_title_task(
        get_relevant_app_title_agent,
        user_requirements,
        last_programs_list(focus_last_window=focus_window),
        get_installed_apps_registry()
    )


    crew1 = Crew(
        agents=[
            get_relevant_app_title_agent
        ],
        tasks=[
            get_app_title_task
        ]
    )
    crew1.kickoff()
    target_app = get_app_title_task.output.raw_output
    print("output  crew 1", target_app)

    enhanced_goal_task = tasks.enhanced_goal_task(
        get_enhanced_goal_agent,
        user_requirements,
        target_app
    )

    crew2 = Crew(
        agents=[
            get_enhanced_goal_agent
        ],
        tasks=[
            enhanced_goal_task
        ]
    )

    crew2.kickoff()
    enhanced_goal = enhanced_goal_task.output.raw_output
    print("crew2 enhanced_goal:", enhanced_goal)

    step_creator_task = tasks.detailed_steps_creator(
        step_creator_agent,
        user_requirements,
        target_app,
        enhanced_goal
    )

    crew3 = Crew(
        agents=[
            step_creator_agent
        ],
        tasks=[
            step_creator_task
        ]
    )
    crew3.kickoff()
    steps = step_creator_task.output.raw_output
    print("crew3 End:", steps)


if __name__ == "__main__":
    main()
