import os
import db
import time
import translation_manager as tm
from language_cache import LanguageCache
import messages as m
import logging
from logger import loggy
from decouple import config
now = time.asctime()
import asyncio
from interactions import Task, IntervalTrigger, Client, Intents, const, Status, Activity, listen

logging.basicConfig()
cls_log = logging.getLogger(const.logger_name)
cls_log.setLevel(logging.WARNING)
translator = tm.TranslationManager(default_language="en")
language_cache = LanguageCache()

heartbeat_started = False
class CustomClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language_cache = language_cache
        self.translator = translator

    def get_text(self, user_id: int, key: str, language: str = None) -> str:
        """Get translated text for any user ID"""
        if language is None:
            language = self.language_cache.get_user_language(db.users_col, user_id)
        return self.translator.get_text(key, language)
    
bot = CustomClient(
    intents=Intents.MESSAGES | Intents.REACTIONS | Intents.GUILDS | Intents.TYPING | Intents.MESSAGE_CONTENT,
    sync_interactions=True,
    send_command_tracebacks=False,
    token=config('DISCORD_TOKEN' if config('ENV') == "production" else 'NEW_TEST_DISCORD_TOKEN')
    )


@listen()
async def on_ready():
    global heartbeat_started
    server_count = len(bot.guilds)
    await bot.change_presence(status=Status.ONLINE, activity=Activity(name=f"in {server_count} servers 🆚!\nGAME OVERHAUL HAS BEEN RELEASED! All accounts have been reset. Please use /register to start!", type=1))
    loggy.info('The bot is up and running')
    await bot.synchronise_interactions()
    if not heartbeat_started:
        check_heartbeat.start()
        heartbeat_started = True


async def load(ctx, extension):
    try:
        bot.load_extension(f'cogs.{extension}')
        await ctx.send(f"Successfully loaded {extension}")
    except Exception as e:
        await ctx.send(f"Failed to load {extension}: {e}")

async def unload(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f"Successfully unloaded {extension}")
    except Exception as e:
        await ctx.send(f"Failed to unload {extension}: {e}")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        try:
            bot.load_extension(f'cogs.{filename[:-3]}')
            loggy.info(f"Loaded extension: {filename[:-3]}")
        except Exception as e:
            loggy.error(f"Failed to load extension {filename}: {e}")


@listen()
async def on_disconnect():
    loggy.warning("Bot disconnected. Attempting to reconnect...")
    await asyncio.sleep(5)  # Wait before attempting to reconnect

async def restart_bot():
    loggy.info("Restarting bot...")
    await bot.stop()
    await asyncio.sleep(5)  # Wait before restarting
    await bot.start()

@Task.create(IntervalTrigger(minutes=5))
async def check_heartbeat():
    try:
        latency = bot.latency
        loggy.info(f'Heartbeat check - latency: {latency}')
        if latency and latency > 2.0:  # Adjusted threshold to 2 seconds
            loggy.warning('High latency detected, restarting bot...')
            await restart_bot()
    except Exception as e:
        loggy.error(f'Error during heartbeat check: {e}')
        await restart_bot()

# Run the bot
try:
    bot.start()
except KeyboardInterrupt:
    loggy.info("Bot stopped by user")
except Exception as e:
    loggy.error(f"An error occurred while running the bot: {e}")
finally:
    # Ensure the bot is properly closed
    if not bot.is_closed:
        asyncio.run(bot.stop())  # Use asyncio.run to properly close the bot


async def validate_user(ctx):
   query = {'DID': str(ctx.author.id)}
   valid = db.queryUser(query)

   if valid:
      return True
   else:
      msg = await ctx.send(m.USER_NOT_REGISTERED, delete_after=5)
      return False


def check_quest_wins(win_value, prestige_level):
   check = win_value - prestige_level#casperjayden
   if check <= 0:
      return 1
   else:
      return check


def add_universes_names_to_autocomplete_list():
   try:
      response = db.queryAllUniverses()
      list_of_universes = []
      for universe in response:
            list_of_universes.append({"name": universe["TITLE"], "value": universe["TITLE"]})
      return sorted(list_of_universes, key=lambda x: x['name'])
   except Exception as e:
      loggy.critical(e)
      return False



