from textwrap import dedent
from crewai import Agent
from tools import get_enhanced_goal_statement


class MarvisAgents:
    def _app_selector(self):
        return Agent(
            role='Windows application analyzer',
            goal='Figure out the application title or windows title',
            backstory=dedent("""You are an Expert windows user working as assistant called App Selector that receives a list of programs and responds only respond with the best match."""),
            allow_delegation=False,
            verbose=True
        )

    def _goal_enhancer(self):
        return Agent(
            role='Windows OS AI Goal Enhancer',
            goal='Analyze the received user requirements that has to be accomplished using Windows OS.',
            backstory=dedent("""Respond an improved user requirement statement tailored for Windows OS applications."""),
            allow_delegation=False,
            tools=[get_enhanced_goal_statement],
            verbose=True
        )

    def _screenshot_analyzer(self):
        return Agent(
            role='Screenshot analyzer',
            goal='Analyze the screenshot and provide the details',
            backstory=dedent("""You are an Expert in analyzing screenshots and providing the details"""),
            allow_delegation=False,
            verbose=True
        )