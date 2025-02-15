# language_cog.py
import interactions
from interactions import listen, Extension, slash_command, SlashContext, OptionType, slash_option, InteractionContext
from language_cache import LanguageCache
from translation_manager import TranslationManager
from logger import loggy

class LanguageCog(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.language_cache = LanguageCache()
        self.translator = TranslationManager()

    @listen()
    async def on_ready(self):
        print('Language Cog is ready!')
        loggy.info('Language Cog is ready')
        
    def get_text(self, ctx: SlashContext, key: str) -> str:
        """Get translated text for the user"""
        from db import users_col  # Import your MongoDB collection
        user_language = self.language_cache.get_user_language(users_col, ctx.author.id)
        return self.translator.get_text(key, user_language)

    @slash_command(name="setlanguage", description="Set your preferred language")
    @slash_option(
        name="language",
        description="Choose your language",
        required=True,
        opt_type=OptionType.STRING,
        choices=[
            interactions.SlashCommandChoice(name="English", value="en"),
            interactions.SlashCommandChoice(name="Español", value="es"),
            interactions.SlashCommandChoice(name="Français", value="fr"),
            interactions.SlashCommandChoice(name="Deutsch", value="de"),
            
        ]
    )
    async def setlanguage(self, ctx: InteractionContext, language: str):
        from db import users_col  # Import your MongoDB collection
        
        self.language_cache.set_user_language(users_col, ctx.author.id, language)
        confirmation = self.get_text(ctx, "messages.language_changed")
        await ctx.send(confirmation)

# # Example usage in another cog
# class GameCog(Extension):
#     def __init__(self, client):
#         self.client = client
#         self.language_cache = LanguageCache()
#         self.translator = TranslationManager()

#     @slash_command(name="start", description="Start a new game")
#     async def start_game(self, ctx: SlashContext):
#         # Get translated text using the cached language
#         welcome_msg = self.get_text(ctx, "messages.game_start")
#         await ctx.send(welcome_msg)

#     def get_text(self, ctx: SlashContext, key: str) -> str:
#         from db import users_col
#         user_language = self.language_cache.get_user_language(users_col, ctx.author.id)
#         return self.translator.get_text(key, user_language)
