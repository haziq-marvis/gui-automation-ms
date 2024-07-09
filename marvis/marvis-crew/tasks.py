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
        print("calleddddddddddddddddd")
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
        print("user requirementtttttttttt", user_requirement)
        return Task(
            description=dedent(
                f"""An efficient assistant who has access to a tool that can take detailed requirements 'create_step_tool', you use the tool to create detailed json with the natural language steps to achieve the goal.

            **Parameters**: 
            - user_requirements: {user_requirement}
            - target_app: {target_app}
            - detailed_requirements: {detailed_requirements}
            **Note**:
            Share all the detailed steps, back with me, do not remove anything. You ll get 100$ for complete answer.
            """),
            expected_output=f"Response from the utility form of a json to achieve the goal.The json must include only an act and its step, should be in the format created by the tool.",
            agent=agent
        )

    def steps_execution_task(self, agent, action, step_description, original_goal, assistant_goal, app_name, instructions, previous_step=None, next_step=None, assistant_identity=""):
        return Task(
            description=dedent(
                f"""An efficient assistant who has access to a tool that can execute a given action 'execute_task'. You use the tool to perform the step provided.

                **Parameters**: 
                - step_action: {action}
                - step_description: {step_description}
                - original_goal: {original_goal}
                - assistant_goal: {assistant_goal}
                - app_name: {app_name}
                - instructions: {instructions}
                - previous_step: {previous_step}
                - next_step: {next_step}

                **Note**:
                Execute each task carefully, retry in case of failure.
                """),
            expected_output="Execution status of the step.",
            agent=agent
        )

    def execution_validator(self, agent, action, step_description, original_goal, assistant_goal, app_name, instructions, previous_step=None, next_step=None, assistant_identity=""):
        return Task(
            description=dedent(
                f"""An efficient assistant who has access to a tool 'validate_task_execution' that can analyze if a step has successfully performed or not.

                **Parameters**: 
                - step_action: {action}
                - step_description: {step_description}
                - original_goal: {original_goal}
                - assistant_goal: {assistant_goal}
                - app_name: {app_name}
                - instructions: {instructions}
                - previous_step: {previous_step}
                - next_step: {next_step}

                **Note**:
                Judge if a task was successfully achieved or not. You’ll get 100$ for complete execution.
                """),
            expected_output="Judgement if a task has been successfully performed or not.",
            agent=agent
        )

    def step_enhancer_task(self, agent, step_action, step_description, original_goal, assistant_goal, app_name, instructions):
        return Task(
            description=dedent(
                f"""An efficient windows expert who has access to a tool 'step_enhancer' that can enhance a step in case of its failed execution.

                **Parameters**: 
                - step_action: {step_action}
                - step_description: {step_description}
                - original_goal: {original_goal}
                - assistant_goal: {assistant_goal}
                - app_name: {app_name}
                - instructions: {instructions}

                **Note**:
                Return the same step again if it is 100% correct and can be retried. You’ll get 100$ for complete execution.
                """),
            expected_output="Improved task that can be successfully done in current system state.",
            agent=agent
        )

    def step_enhancer_task(self, agent, step_action, step_description, original_goal, assistant_goal, app_name, instructions):
        return Task(
            description=dedent(
                f"""An efficient windows expert who has access to a tool 'step_enhancer' that can enhance a step in case of its failed execution.

                **Parameters**: 
                - step_action: {step_action}
                - step_description: {step_description}
                - original_goal: {original_goal}
                - assistant_goal: {assistant_goal}
                - app_name: {app_name}
                - instructions: {instructions}

                **Note**:
                Return the same step again if it is 100% correct and can be retried. You’ll get 100$ for complete execution.
                """),
            expected_output="Improved task that can be successfully done in current system state.",
            agent=agent
        )

    def text_summarizer(self, agent, text):
        return Task(
            description=dedent(
                f"""An efficient assistant who can summarize the the provided text in blog text format for this provided text "{text}" in 2-3 sentences.

            **Parameters**: 
            - text: {text}
            **Note**:
            Provide a concise and understandable summary in 2-3 sentences.
            """),
            expected_output=f"Summarize this text statement: {text}.",
            agent=agent
        )
