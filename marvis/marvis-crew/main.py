from agents import MarvisAgents
from tasks import MarvisTasks
from dotenv import load_dotenv
from textwrap import dedent
from tools import get_enhanced_goal_statement
import os
from crewai import Crew

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


def main():
    user_requirements = input("# Describe what you want Marvis to do:\n\n")
    agents = MarvisAgents()
    tasks = MarvisTasks()

    # define agent
    get_relevant_app_title_agent = agents._app_selector()
    get_enhanced_goal_agent = agents._goal_enhancer()

    # define tasks

    get_app_title_task = tasks._get_app_title_task(get_relevant_app_title_agent, user_requirements, [], [], focused_app="Google Chrome")
    enhanced_goal_task = tasks.enhanced_goal_task(get_enhanced_goal_agent, user_requirements, focused_app="Google Chrome")

    crew = Crew(
        agents=[
            # get_relevant_app_title_agent,
            get_enhanced_goal_agent
        ],
        tasks=[
            # get_app_title_task,
            enhanced_goal_task
        ]
    enhanceUserRequirementsTask = Task(
        # config={
        #     'user_requirements': user_requirements,
        #     'focused_app': "Firefox"
        # },
        tools=[get_enhanced_goal_statement],
        description=dedent(
            f"""
            **Task**: {user_requirements}
            **Description**: Based on user requirements and focused app enhance user requirements

            **Parameters**: 
            - user_requirements: {user_requirements}
            - focused_app: select a relevant windows application for {user_requirements}

        """
        ),
        expected_output="User Enhanced Requirements",
        agent=agents._goal_enhancer()
    )

    crew.kickoff()
    # enhanceUserRequirementsTask = Task(
    #     config={
    #         'user_requirements': user_requirements,
    #         'focused_app': "Firefox"
    #     },
    #     tools=[get_enhanced_goal_statement],
    #     description=dedent(
    #         """An expert Windows OS User who can take a look at the given screen and user requirements using the tool and return enhanced user requirements."""),
    #     expected_output="User Enhanced Requirements",
    #     agent=agents._goal_enhancer()
    # )

    print("End:")
    # res = enhanceUserRequirementsTask.execute()
    # print("Improved Goal Statement:", res)

    # Create a crew and assign the task
    crew = Crew(
        agents=[agents._goal_enhancer()],
        tasks=[enhanceUserRequirementsTask],
        verbose=True
    )

    # Execute the crew
    result = crew.kickoff()
    print(result)


if __name__ == "__main__":
    main()
