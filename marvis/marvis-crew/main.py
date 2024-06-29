from agents import MarvisAgents
from tasks import MarvisTasks
from dotenv import load_dotenv
from textwrap import dedent
from tools import get_enhanced_goal_statement
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


def main():
    user_requirements = input("# Describe what you want Marvis to do:\n\n")
    agents = MarvisAgents()
    # tasks = MarvisTasks()
    from crewai import Task, Crew

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
