from textwrap import dedent
from crewai import Agent
from tools.get_enhanced_goal_statement import get_enhanced_goal_statement_tool, activate_windowt_by_title_tool
from tools.get_app_title import get_app_title_tool
from tools_utils import get_enhanced_goal_statements, create_step_tool

class MarvisAgents:
    def app_selector(self):
        return Agent(
            role='Windows application analyzer',
            goal='Figure out the application title or windows title',
            backstory=dedent("""You are an Expert windows user working as assistant called App Selector that receives a list of programs and responds only respond with the best match."""),
            allow_delegation=False,
            # tools=[get_app_title_tool],
            verbose=True
        )

    def _goal_enhancer(self):
        return Agent(
            role='Windows OS AI Goal Enhancer',
            goal='Analyze the user requirements and target_app to open target_app and enhance user requirements using tools.',
            backstory=dedent("""You are an expert windows user, that has access to a tool 'get_enhanced_goal_statement_tool', you use this tool to get enhanced goal and then proof-read it."""),
            allow_delegation=False,
            tools=[get_enhanced_goal_statements],
            verbose=True
        )

    def step_creator(self):
        return Agent(
            role='AI capable to operate the Windows 11 Operating System',
            goal='Call the tool provided and return the json output.',
            backstory=dedent("""You are an AI capable to operate the Windows 11 Operating System by using natural language.You will receive a description of the current state of the system and user's requirement."""),
            allow_delegation=False,
            tools=[create_step_tool],
            verbose=True
        )
