from typing import List
from interactions import SlashCommandChoice

class ChoicesManager:
    @staticmethod
    def get_help_choices(translator, language: str) -> List[SlashCommandChoice]:
        """Generate help command choices based on language"""
        return [
            SlashCommandChoice(
                name=translator.get_text("help.choices.play", language),
                value="play"
            ),
            SlashCommandChoice(
                name=translator.get_text("help.choices.legend", language),
                value="legend"
            ),
            SlashCommandChoice(
                name=translator.get_text("help.choices.classes", language),
                value="classes"
            ),
            SlashCommandChoice(
                name=translator.get_text("help.choices.titles", language),
                value="titles"
            ),
            SlashCommandChoice(
                name=translator.get_text("help.choices.arms", language),
                value="arms"
            ),
            SlashCommandChoice(
                name=translator.get_text("help.choices.enhancers", language),
                value="enhancers"
            ),
            SlashCommandChoice(
                name=translator.get_text("help.choices.elements", language),
                value="elements"
            ),
            SlashCommandChoice(
                name=translator.get_text("help.choices.menu", language),
                value="menu"
            ),
            SlashCommandChoice(
                name=translator.get_text("help.choices.universe", language),
                value="universe"
            ),
            SlashCommandChoice(
                name=translator.get_text("help.choices.teams", language),
                value="teams"
            ),
            SlashCommandChoice(
                name=translator.get_text("help.choices.options", language),
                value="options"
            ),
            SlashCommandChoice(
                name=translator.get_text("help.choices.manual", language),
                value="manual"
            ),
        ]