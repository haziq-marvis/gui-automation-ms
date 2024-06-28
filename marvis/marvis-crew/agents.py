from textwrap import dedent
from crewai import Agent


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
            role='Windows AI Goal Enhancer',
            goal='Analyze the received goal that has to be accomplished using Windows.',
            backstory=dedent("""Respond an improved goal statement tailored for Windows applications."""),
            allow_delegation=False,
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