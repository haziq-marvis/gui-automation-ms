from typing import Type, Any
from langchain.tools import Tool
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from utils.additional import get_focused_window_details, analyze_screenshot, get_screen_image


class GetEnhancedGoalBaseTool:
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


class ValidateEnhancedGoalParams(BaseModel):
    """Input for reading a post"""

    user_requirements: str = Field(description="requirement of the end user")
    focused_app: str = Field(description="Current focused app")


def util_get_enhanced_goal_statement(user_requirements, focused_app):
    """
    Perform actions based on user_requirements and focused_app
    Args:
        user_requirements: The source of the data to analyze.
        focused_app: The type of analysis to perform.
    Returns:
        A string describing the result of the analysis.
     """
    print("Received user goal:", user_requirements)
    print("Focused application:", focused_app)
    print("hello testing", user_requirements, focused_app)
    screenshot = get_screen_image(focused_app, additional_context=None, x=None, y=None,
                                  screenshot_size="Full Screen")
    prompt = (
        f"You are an AI Agent called Windows AI that is capable to operate freely all applications on Windows by only using natural language.\n"
        f"You will receive a  user requirements and will try to accomplish it using Windows. Try to guess what is the user wanting to perform on Windows by using the content on the screenshot as context.\n"
        f"Respond an improved user requirements statement tailored for Windows applications by analyzing the current status of the system and the next steps to perform. Be direct and concise, do not use pronouns.\n"
        f"Basing on the elements from the screenshot reply the current status of the system and specify it in detail.\n"
        f"Focused application: \"{focused_app}\".\nGoal: \"{user_requirements}\"."
    )
    enhanced_requirements = analyze_screenshot(screenshot, prompt)

    return enhanced_requirements


get_enhanced_goal_statement_tool = GetEnhancedGoalBaseTool().from_function(
    util_get_enhanced_goal_statement,
    "util_get_enhanced_goal_statement",
    "Tool that return enhanced goal statement based on user requirements and focused app",
    args_schema=ValidateEnhancedGoalParams,
)
