import asyncio
import uuid

import db
import time
import textwrap
import help_guide as guide
from logger import loggy
import unique_traits as ut
from interactions.ext.paginators import Paginator
from interactions import (listen, slash_command, InteractionContext, SlashCommandOption, OptionType, Embed,
                          AutocompleteContext, slash_option, Extension, ActionRow, Button, ButtonStyle,
                          ContainerComponent, TextDisplayComponent, SeparatorComponent, SectionComponent,
                          ThumbnailComponent, StringSelectMenu, StringSelectOption)
import crown_utilities
now = time.asctime()

GUIDE_ART = "https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"
GUIDE_TIMEOUT = 30 * 60          # seconds the guide keeps answering clicks
TOPIC_COLORS = {
    "home": 0x5865F2, "start": 0x2ECC71, "battles": 0xE74C3C, "damage": 0xE67E22, "cards": 0x7289DA,
    "classes": 0x9B59B6, "elements": 0x1ABC9C, "enhancers": 0x2ECC71, "gear": 0xF1C40F, "modes": 0x3498DB,
    "economy": 0xF1C40F, "guilds": 0x95A5A6, "universes": 0x1ABC9C, "settings": 0x95A5A6, "commands": 0x5865F2,
}
QUICK_TOPICS = ("start", "battles", "damage", "commands")


def _guide_view(uid, topic, page_index, pages):
    """The whole guide message for one page (Components V2 container)."""
    parts = []
    if topic == "home":
        parts.append(SectionComponent(components=[TextDisplayComponent(guide.home_text())],
                                      accessory=ThumbnailComponent(GUIDE_ART)))
    else:
        emoji, title, _, _ = guide.TOPIC_INDEX[topic]
        page_title, body = pages[page_index]
        counter = f" · page {page_index + 1} of {len(pages)}" if len(pages) > 1 else ""
        parts.append(TextDisplayComponent(f"## {emoji} {title}\n-# {page_title}{counter}"))
        parts.append(TextDisplayComponent(crown_utilities.clip(body, 3300)))
    parts.append(SeparatorComponent(divider=True))

    options = [StringSelectOption(label="Home", value="home", description="All topics", emoji="🏠", default=topic == "home")]
    for key, emoji, title, blurb, _ in guide.TOPICS:
        options.append(StringSelectOption(label=title, value=key, description=blurb[:100], emoji=emoji, default=key == topic))
    parts.append(ActionRow(StringSelectMenu(*options, placeholder="📚 Choose a topic…", custom_id=f"{uid}|topic")))

    if topic == "home":
        buttons = []
        for key in QUICK_TOPICS:
            emoji, title, _, _ = guide.TOPIC_INDEX[key]
            style = ButtonStyle.GREEN if key == "start" else ButtonStyle.GREY
            buttons.append(Button(style=style, label=title, emoji=emoji, custom_id=f"{uid}|go|{key}"))
        parts.append(ActionRow(*buttons))
    else:
        buttons = []
        if len(pages) > 1:
            buttons.append(Button(style=ButtonStyle.GREY, label="Back", emoji="◀️", custom_id=f"{uid}|prev", disabled=page_index == 0))
            buttons.append(Button(style=ButtonStyle.BLUE, label="Next", emoji="▶️", custom_id=f"{uid}|next", disabled=page_index >= len(pages) - 1))
        buttons.append(Button(style=ButtonStyle.GREY, label="Home", emoji="🏠", custom_id=f"{uid}|home"))
        parts.append(ActionRow(*buttons))
    return ContainerComponent(*parts, accent_color=TOPIC_COLORS.get(topic, 0x5865F2))


def _guide_ids(uid):
    return [f"{uid}|topic", f"{uid}|prev", f"{uid}|next", f"{uid}|home"] + [f"{uid}|go|{key}" for key in QUICK_TOPICS]


class Help(Extension):
    def __init__(self,bot):
        self.bot = bot
        self._command_list = None

    @listen()
    async def on_ready(self):
        loggy.info('Help Cog is ready')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    def command_list(self):
        """name -> description for every registered slash command (read once from the bot)."""
        if self._command_list is None:
            found = {}
            try:
                for cmd in self.bot.application_commands:
                    name = str(getattr(cmd, "name", "") or "")
                    if name and " " not in name:
                        found[name] = str(getattr(cmd, "description", "") or "").strip()
            except Exception as ex:
                loggy.warning(f"help: could not list commands: {ex}")
            self._command_list = found
        return self._command_list

    @slash_command(name="help", description="Learn everything about Anime VS+: battles, cards, modes, commands", options=[
                            SlashCommandOption(
                                    name="topic",
                                    description="Jump straight to a topic (optional)",
                                    type=OptionType.STRING,
                                    required=False,
                                    autocomplete=True
                                )
                            ]
        ,scopes=crown_utilities.guild_ids)
    async def help(self, ctx, topic: str = ""):
        """Interactive guide: a topic menu, pages with Back / Next, and Home."""
        uid = uuid.uuid4().hex[:12]
        state = {"topic": guide.resolve_topic(topic), "page": 0}

        def render():
            pages = [] if state["topic"] == "home" else guide.pages_for(state["topic"], self.command_list())
            if state["topic"] != "home" and not pages:
                state["topic"] = "home"
            state["page"] = max(0, min(state["page"], max(0, len(pages) - 1)))
            return _guide_view(uid, state["topic"], state["page"], pages), len(pages)

        try:
            view, _ = render()
            await ctx.send(components=[view], ephemeral=True)
        except Exception as ex:
            loggy.error(f"help: could not open the guide: {type(ex).__name__}: {ex}")
            await ctx.send(f"Something went wrong opening the guide. Ask in the {guide.SUPPORT}.", ephemeral=True)
            return

        ids = _guide_ids(uid)
        while True:
            try:
                event = await self.bot.wait_for_component(components=ids, timeout=GUIDE_TIMEOUT)
            except asyncio.TimeoutError:
                return
            ictx = event.ctx
            action = ictx.custom_id.split("|", 1)[1]
            try:
                if action == "topic":
                    state["topic"] = guide.resolve_topic((ictx.values or ["home"])[0])
                    state["page"] = 0
                elif action == "home":
                    state["topic"], state["page"] = "home", 0
                elif action.startswith("go|"):
                    state["topic"], state["page"] = guide.resolve_topic(action[3:]), 0
                elif action == "next":
                    state["page"] += 1
                elif action == "prev":
                    state["page"] -= 1
                view, _ = render()
                await ictx.edit_origin(components=[view])
            except Exception as ex:
                loggy.warning(f"help: page change failed: {type(ex).__name__}: {ex}")
                try:
                    await ictx.defer(edit_origin=True, suppress_error=True)
                except Exception:
                    pass

    @help.autocomplete("topic")
    async def help_autocomplete(self, ctx: AutocompleteContext):
        typed = (ctx.input_text or "").lower()
        choices = [{"name": "🏠 Home (all topics)", "value": "home"}]
        for key, emoji, title, blurb, _ in guide.TOPICS:
            choices.append({"name": f"{emoji} {title}: {blurb}"[:100], "value": key})
        if typed:
            choices = [c for c in choices if typed in c["name"].lower() or typed in c["value"]]
        await ctx.send(choices=choices[:25])


    @slash_command(name="traits", description="List of Universe Traits", scopes=crown_utilities.guild_ids)
    @slash_option(
    name="universe",
    description="Universe to list traits for",
    opt_type=OptionType.STRING,
    required=False,
    autocomplete=True
    )
    async def traits(self, ctx: InteractionContext, universe: str = ""):
        try:
            traits = ut.formatted_traits

            def trait_embed(trait):
                return Embed(
                    title=f"♾️ {trait['NAME']} Trait",
                    description=f"**{trait['EFFECT']}**\n{trait['TRAIT']}",
                    color=0x1ABC9C,
                ).set_footer(text="/help universes · how traits fit into battles")

            if not universe:
                embed_list = [trait_embed(trait) for trait in traits]
                paginator = Paginator.create_from_embeds(self.bot, *embed_list)
                paginator.show_select_menu = True
                await paginator.send(ctx)
                return

            wanted = universe.strip().lower()
            match = next((t for t in traits if str(t['NAME']).lower() == wanted), None)
            if match is None:
                await ctx.send(f"I couldn't find a trait for **{universe}**. Use `/traits` without a universe to see them all.", ephemeral=True)
                return
            await ctx.send(embed=trait_embed(match))
        except Exception as ex:
            loggy.error(f"Error in Traits command: {ex}")
            await ctx.send("There's an issue with your Traits List. Check with support.", ephemeral=True)
            return


    @traits.autocomplete("universe")
    async def traits_autocomplete(self, ctx: AutocompleteContext):
        choices = []
        options = crown_utilities.get_cached_universes()
        """
        for option in options
        if ctx.input_text is empty, append the first 24 options in the list to choices
        if ctx.input_text is not empty, append the first 24 options in the list that match the input to choices as typed
        """
            # Iterate over the options and append matching ones to the choices list
        for option in options:
                if not ctx.input_text:
                    # If input_text is empty, append the first 24 options to choices
                    if len(choices) < 24:
                        choices.append(option)
                    else:
                        break
                else:
                    # If input_text is not empty, append the first 24 options that match the input to choices
                    if option["name"].lower().startswith(ctx.input_text.lower()):
                        choices.append(option)
                        if len(choices) == 24:
                            break

        await ctx.send(choices=choices)


def setup(bot):
    Help(bot)
