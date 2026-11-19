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


startup_done = False


@listen()
async def on_ready():
    """
    Runs on every READY (the first connect and any full reconnect), so the
    one-time work is guarded.  Application commands are already synced by the
    client itself (sync_interactions=True); syncing them again here only
    doubled the start-up API traffic.
    """
    global startup_done
    server_count = len(bot.guilds)
    try:
        await bot.change_presence(status=Status.ONLINE, activity=Activity(name=f"in {server_count} servers 🆚!\nGAME OVERHAUL HAS BEEN RELEASED! All accounts have been reset. Please use /register to start!", type=1))
    except Exception as ex:
        loggy.warning(f"Could not set presence: {ex}")
    loggy.info('The bot is up and running')
    if not startup_done:
        startup_done = True
        check_heartbeat.start()
        # Index creation talks to MongoDB; keep it off the event loop.
        try:
            created = await asyncio.to_thread(db.ensure_indexes)
            loggy.info(f"Database indexes ensured: {len(created)}")
        except Exception as ex:
            loggy.warning(f"Could not ensure database indexes: {ex}")


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

for filename in sorted(os.listdir('./cogs')):
    if filename.endswith('.py'):
        try:
            bot.load_extension(f'cogs.{filename[:-3]}')
            loggy.info(f"Loaded extension: {filename[:-3]}")
        except Exception as e:
            loggy.error(f"Failed to load extension {filename}: {e}")


@listen()
async def on_disconnect():
    # The client reconnects (and resumes) by itself; nothing to do but note it.
    loggy.warning("Bot disconnected; the client will reconnect automatically.")


@Task.create(IntervalTrigger(minutes=5))
async def check_heartbeat():
    """
    Log the gateway latency.

    This used to "restart" the bot when latency went over 2 seconds by calling
    bot.stop() and then bot.start() from inside the running bot.  bot.start()
    cannot run inside an event loop, so the restart never happened: the bot just
    shut down, every battle in progress died, and the process exited.  The
    client already reconnects on its own when the gateway connection is bad.
    """
    try:
        latency = bot.latency
        if latency and latency > 2.0:
            loggy.warning(f'High gateway latency: {latency:.2f}s')
        else:
            loggy.info(f'Heartbeat check - latency: {latency}')
    except Exception as e:
        loggy.error(f'Error during heartbeat check: {e}')


# Run the bot (blocks until the bot shuts down)
try:
    bot.start()
except KeyboardInterrupt:
    loggy.info("Bot stopped by user")
except Exception as e:
    loggy.error(f"An error occurred while running the bot: {e}")


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



