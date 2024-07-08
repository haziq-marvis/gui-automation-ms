import time

from agents import MarvisAgents
from utils.last_app import last_programs_list
from utils.window_focus import get_installed_apps_registry
from tasks import MarvisTasks
from dotenv import load_dotenv
import os
from crewai import Crew
from utils.additional import cleanup_json

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
    step_execution_agent = agents.steps_executer()
    # execution_validator_agent = agents.execution_validator()
    # step_enhancer_agent = agents.step_enhancer_agent()

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

    time.sleep(3)

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
    time.sleep(3)
    json_steps, instructions = cleanup_json(steps)  # TODO: maybe do in post crew
    print("after analysis", json_steps)

    # execution_validator_task = tasks.steps_execution_task(
    #     execution_validator_agent,
    #     action=action,
    #     step_description=step_description,
    #     original_goal=user_requirements,
    #     assistant_goal=enhanced_goal,
    #     app_name=target_app,
    #     instructions=instructions,
    #     previous_step=previous_step,
    #     next_step=next_step
    # )

    crew_tasks = []
    executor = "act"
    # if type(json_steps[0]) is list:
    #     json_steps = json_steps[0]
    #     instructions = {"actions": json_steps}
    print("json_steps", json_steps)
    print("instructions", instructions)
    # if type(instructions[0]) is list:
    #     instructions = instructions[0]
    for i, step in enumerate(json_steps):
        previous_step = None
        if i > 0:
            previous_step = json_steps[i-1]
        next_step = None
        if i+1 < len(json_steps):
            next_step = json_steps[i + 1]
        action = step.get(f"{executor}")
        step_description = step.get("step") or step.get("details", "No step description provided.")

        execution_task = tasks.steps_execution_task(
            step_execution_agent,
            action=action,
            step_description=step_description,
            original_goal=user_requirements,
            assistant_goal=enhanced_goal,
            app_name=target_app,
            instructions=instructions,
            previous_step=previous_step,
            next_step=next_step
        )
        crew_tasks.append(execution_task)

    crew4 = Crew(
        agents=[
            step_execution_agent
        ],
        tasks=crew_tasks
    )
    crew4.kickoff()


if __name__ == "__main__":
    main()
