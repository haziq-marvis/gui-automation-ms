from textwrap import dedent
from crewai import Agent
from tools.step_executor import execute_task
from tools_utils import get_enhanced_goal_statements, create_step_tool, validate_task_execution, step_enhancer

step_creator_case_example = ''' {{ .Response }} 
    {
      "actions": [
        {
          "act": "open_app",
          "step": "Firefox"
        },
        {
          "act": "press_key",
          "step": "Ctrl + T"
        },
        {
          "act": "text_entry",
          "step": "reddit.com"
        },
        {
          "act": "press_key",
          "step": "Enter"
        }
      ]
    }'''


class MarvisAgents:
    def app_selector(self):
        return Agent(
            role='Windows application analyzer',
            goal='Figure out the application title or windows title',
            backstory=dedent("""You are an Expert windows user working as assistant called App Selector that receives a list of programs and responds only respond with the best match."""),
            allow_delegation=False,
            LLM='gpt-4o',
            # tools=[get_app_title_tool],
            verbose=True
        )

    def _goal_enhancer(self):
        return Agent(
            role='Windows OS AI Goal Enhancer',
            goal='Analyze the user requirements and target_app to open target_app and enhance user requirements using tools.',
            backstory=dedent(
                """You are an expert windows user, that has access to a tool 'get_enhanced_goal_statement_tool', you use this tool to get enhanced goal and then proof-read it."""),
            allow_delegation=False,
            tools=[get_enhanced_goal_statements],
            LLM='gpt-4o',
            verbose=True,
            max_iter=3
        )

    def step_creator(self):
        return Agent(
            role='AI capable to operate the Windows 11 Operating System',
            goal='Call the tool provided and return the json output.',
            backstory=dedent(
                """You are an AI capable to operate the Windows 11 Operating System by using natural language.You will receive a description of the current state of the system and user's requirement."""),
            allow_delegation=False,
            tools=[create_step_tool],
            verbose=True,
            LLM='gpt-4o',
            response_template=step_creator_case_example,
            max_iter=3
        )

    def steps_executer(self):
        return Agent(
            role='AI capable to execute steps on the Windows 11 Operating System',
            goal='Use the tool provided to execute given task and return the execution status.',
            backstory=dedent(
                """You are an AI capable of executing steps on the Windows 11 Operating System. You will receive a detailed step to perform and you need to execute it accurately."""),
            allow_delegation=False,
            tools=[execute_task,],
            LLM='gpt-4o',
            verbose=True,
            max_iter=3
        )

    def execution_validator(self):
        return Agent(
            role='Expert AI agent capable to analyze execution of a task on the Windows 11 Operating System',
            goal='figure out if the given task (use step_action and step_description to know about task) has been executed successfully or not using tool attached. Reassign the task to other agent if needed.',
            backstory=dedent(
                """You are an AI capable of executing steps on the Windows 11 Operating System. You have access to a tool "validate_task_execution" that can capture screen to analyze if given task has been acheived or not."""),
            allow_delegation=True,
            tools=[validate_task_execution],
            verbose=True,
            LLM='gpt-4o',
            max_iter=1
        )

    def step_enhancer_agent(self):
        return Agent(
            role='Expert AI agent capable to suggest better step for acheiving a task on the Windows 11 Operating System',
            goal='Figure out a task that can be done to navigate from current system status to achieve end user goal, use attached tool to get step',
            backstory=dedent(
                """You are an AI capable of executing steps on the Windows 11 Operating System. You have access to a tool "step_enhancer" that can capture screen to return better step that can acheive the current task."""),
            allow_delegation=True,
            tools=[step_enhancer],
            verbose=True,
            LLM='gpt-4o',
            max_iter=1
        )

    def response_summarizer(self):
        return Agent(
            role='Expert AI agent capable to summarize the text provided on the Windows 11 Operating System',
            goal='Summarize provided text and return a concise blog-style response',
            backstory=dedent(
                """You are an AI capable of summarizing the text on the Windows 11 Operating System in 2-3 sentences."""),
            allow_delegation=True,
            # tools=[step_enhancer],
            verbose=True,
            LLM='gpt-4o',
            max_iter=1
        )

    def step_creater_new(self):
        return Agent(
            role='AI capable to operate the Windows 11 Operating System',
            goal='Call the tool provided and return the json output.',
            backstory=dedent(
                """You are an AI capable to operate the Windows 11 Operating System by using natural language.You will receive a description of the current state of the system and user's requirement."""),
            allow_delegation=False,
            tools=[create_step_tool],
            verbose=True,
            LLM='gpt-4o',
            response_template=step_creator_case_example,
            max_iter=3
        )
