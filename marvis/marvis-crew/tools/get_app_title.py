from typing import Type, Any
from langchain.tools import Tool
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from textwrap import dedent
from crewai import Task
from utils.last_app import last_programs_list
from utils.window_focus import get_installed_apps_registry
import re
from utils.additional import get_focused_window_details, analyze_screenshot


class GetAppTitleBaseTool:
    def from_function(
            self,
            func,
            name,
            description,
            args_schema: Type[BaseModel] = None,
            return_direct: bool = False,
    ):
        """Create a structured tool from a function."""
        parser = PydanticOutputParser(pydantic_object=args_schema)
        description_with_schema = f"""{description}
        Input should be a string representation of a dictionary containing the following keys:
        {parser.get_format_instructions()}
        """

        def parse_input_and_delegate(user_requirements: str, focused_app: str) -> Any:
            """Parse the input and delegate to the function."""
            try:
                parsed = parser.invoke(
                    '{' + f'"user_requirements": "{user_requirements}", "focused_app": "{focused_app}"' + '}')
            except Exception as e:
                return f"Could not parse input: {str(e)}"
            return func(parsed)

        tool = Tool.from_function(
            parse_input_and_delegate,
            name,
            description_with_schema,
            args_schema=None,
            return_direct=return_direct,
        )
        return tool


class ValidateAppTitleParams(BaseModel):
    """Input for reading a post"""

    user_requirements: str = Field(description="requirement of the end user")
    focused_app: str = Field(description="Current focused app")


def util_get_relevant_app_title(user_requirement, focused_app):
    """Function to get relevant application title against a goal."""
    print("Inside util_get_relevant_app_title")
    print("user_requirement", user_requirement)
    print("focused_app", focused_app)
    all_program_list = last_programs_list(focus_last_window=focused_app)
    installed_app_registry = get_installed_apps_registry()

    from agents import MarvisAgents
    Agents = MarvisAgents()
    app_selector_agent = Agents._app_selector()

    task = Task(
        description=dedent(f"""You will receive a list of programs and responds only respond with the
                     best match program of the goal. Only respond with the window name or the program name. 
                     For search engines and social networks use Firefox or Chrome.\n
                     Open programs:\n{all_program_list}\n
                     Goal: {user_requirement}\n
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


get_app_title_tool = GetAppTitleBaseTool().from_function(
    util_get_relevant_app_title,
    "util_get_relevant_app_title",
    "Tool that return releavnt app title based on user requirements and focused app",
    args_schema=ValidateAppTitleParams,
)