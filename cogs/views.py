import textwrap
import crown_utilities
import db
import messages as m
import numpy as np
import help_commands as h
import unique_traits as ut
import destiny as d
import random
from .classes.card_class import Card
from .classes.title_class import Title
from .classes.arm_class import Arm
from .classes.summon_class import Summon
from interactions.ext.paginators import Paginator
from interactions import Client, ActionRow, Button, ButtonStyle, File, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension, global_autocomplete, AutocompleteContext, slash_option
import re
import io
from io import BytesIO





class Views(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Views Cog is ready!')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    @slash_command(description="Equip a Card", options=[
            SlashCommandOption(
                name="card",
                description="Type in the name of the card you want to equip",
                type=OptionType.STRING,
                required=True,
            )
    ])
    async def equipcard(self, ctx, card: str):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        card_name = card
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)

        resp = db.queryCard({'NAME': {"$regex": f"^{str(card)}$", "$options": "i"}})

        card_name = resp["NAME"]

        if card_name in user['CARDS']:
            response = db.updateUserNoFilter(user_query, {'$set': {'CARD': str(card_name)}})
            embed = Embed(title=f"🎴 Card Successfully Equipped", description=f"{card_name} has been equipped.", color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            await ctx.send(m.USER_DOESNT_HAVE_THE_CARD, hidden=True)


    @slash_command(description="Type a card name, title, arm, universe, house, hall, or boss to view it!")
    @slash_option(
        name="name",
        description="Type in the name of the card, title, arm, universe, house, hall, or boss you want to view",
        opt_type=OptionType.STRING,
        required=False,
    )
    @slash_option(
        name="advanced_search",
        description="Advanced search for lists of characters and accessories",
        opt_type=OptionType.STRING,
        required=False,
        autocomplete=True,
    )
    async def view(self, ctx: InteractionContext, name: str = "", advanced_search: str = ""):
        await ctx.defer()
        if not await crown_utilities.player_check(ctx):
            return
        try:
            if advanced_search:
                if advanced_search:
                    response = await advanced_card_search(self, ctx, advanced_search)
                    return
            
            if name:
                response = db.viewQuery(f"^{str(name)}$")
                if response:
                    if len(response) == 1:
                        if response[0]['TYPE'] == "CARDS":
                            await viewcard(self, ctx, response[0]['DATA'])
                        if response[0]['TYPE'] == "TITLES":
                            await viewtitle(self, ctx, response[0]['DATA'])
                        if response[0]['TYPE'] == "ARM":
                            await viewarm(self, ctx, response[0]['DATA'])
                        if response[0]['TYPE'] == "PET":
                            await viewsummon(self, ctx, response[0]['DATA'])
                        if response[0]['TYPE'] == "UNIVERSE":
                            await viewuniverse(self, ctx, response[0]['DATA'])
                        if response[0]['TYPE'] == "BOSS":
                            await viewboss(self, ctx, response[0]['DATA'])
                        if response[0]['TYPE'] == "HALL":
                            await viewhall(self, ctx, response[0]['DATA'])
                        if response[0]['TYPE'] == "HOUSE":
                            await viewhouse(self, ctx, response[0]['DATA'])
                        return
                    else:
                        list_of_results = []
                        counter = 0
                        if response:
                            for result in response:
                                if result['TYPE'] == "CARDS":
                                    list_of_results.append({'TYPE': 'CARD', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the card 🎴 {result['DATA']['NAME']}?", 'DATA': result['DATA']})
                                
                                if result['TYPE'] == "TITLES":
                                    list_of_results.append({'TYPE': 'TITLE', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the title 🎗️ {result['DATA']['TITLE']}?", 'DATA': result['DATA']})
                                
                                if result['TYPE'] == "ARM":
                                    list_of_results.append({'TYPE': 'ARM', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the arm 🦾 {result['DATA']['ARM']}?", 'DATA': result['DATA']})
                                
                                if result['TYPE'] == "PET":
                                    list_of_results.append({'TYPE': 'PET', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the summon 🧬 {result['DATA']['PET']}?", 'DATA': result['DATA']})
                                
                                if result['TYPE'] == "UNIVERSE":
                                    list_of_results.append({'TYPE': 'UNIVERSE', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the universe 🌍 {result['DATA']['TITLE']}?", 'DATA': result['DATA']})
                                
                                if result['TYPE'] == "BOSS":
                                    list_of_results.append({'TYPE': 'BOSS', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the boss 👹 {result['DATA']['NAME']}?", 'DATA': result['DATA']})
                                
                                if result['TYPE'] == "HALL":
                                    list_of_results.append({'TYPE': 'HALL', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the hall ⛩️ {result['DATA']['HALL']}?", 'DATA': result['DATA']})
                                
                                if result['TYPE'] == "HOUSE":
                                    list_of_results.append({'TYPE': 'HOUSE', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the house 🏠 {result['DATA']['HOUSE']}?", 'DATA': result['DATA']})
                            
                        if list_of_results:
                            message = [f"{result['TEXT']}\n\n" for result in list_of_results]
                            me = ''.join(message)
                            embedVar = Embed(title="Did you mean?...", description=textwrap.dedent(f"""\
                            {me}
                            """), color=0xf1c40f)

                            buttons = []
                            
                            for result in list_of_results:
                                if result['TYPE'] == "CARD":
                                    buttons.append(
                                        Button(
                                            style=ButtonStyle.BLUE,
                                            label=f"🎴 {result['DATA']['NAME']}",
                                            custom_id=f"{str(result['NUMBER'])}"
                                        )
                                    )
                                
                                if result['TYPE'] == "TITLE":
                                    buttons.append(
                                        Button(
                                            style=ButtonStyle.BLUE,
                                            label=f"🎗️ {result['DATA']['TITLE']}",
                                            custom_id=f"{str(result['NUMBER'])}"
                                        )
                                    )
                                
                                if result['TYPE'] == "ARM":
                                    buttons.append(
                                        Button(
                                            style=ButtonStyle.BLUE,
                                            label=f"🦾 {result['DATA']['ARM']}",
                                            custom_id=f"{str(result['NUMBER'])}"
                                        )
                                    )
                                
                                if result['TYPE'] == "PET":
                                    buttons.append(
                                        Button(
                                            style=ButtonStyle.BLUE,
                                            label=f"🐦 {result['DATA']['PET']}",
                                            custom_id=f"{str(result['NUMBER'])}"
                                        )
                                    )
                                
                                if result['TYPE'] == "UNIVERSE":
                                    buttons.append(
                                        Button(
                                            style=ButtonStyle.BLUE,
                                            label=f"🌍 {result['DATA']['TITLE']}",
                                            custom_id=f"{str(result['NUMBER'])}"
                                        )
                                    )
                                
                                if result['TYPE'] == "BOSS":
                                    buttons.append(
                                        Button(
                                            style=ButtonStyle.BLUE,
                                            label=f"👹 {result['DATA']['NAME']}",
                                            custom_id=f"{str(result['NUMBER'])}"
                                        )
                                    )
                                
                                if result['TYPE'] == "HALL":
                                    buttons.append(
                                        Button(
                                            style=ButtonStyle.BLUE,
                                            label=f"⛩️ {result['DATA']['HALL']}",
                                            custom_id=f"{str(result['NUMBER'])}"
                                        )
                                    )
                                
                                if result['TYPE'] == "HOUSE":
                                    buttons.append(
                                        Button(
                                            style=ButtonStyle.BLUE,
                                            label=f"🏠 {result['DATA']['HOUSE']}",
                                            custom_id=f"{str(result['NUMBER'])}"
                                        )
                                    )

                            buttons.append(
                                Button(
                                style=ButtonStyle.RED,
                                label="❌ Cancel",
                                custom_id="cancel"
                            ))
                            
                            buttons_action_row = ActionRow(*buttons)

                            msg = await ctx.send(embed=embedVar, components=[buttons_action_row])
                            
                            def check(component: Button) -> bool:
                                return button_ctx.author == ctx.author

                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[buttons_action_row, buttons], timeout=300, check=check)
                                
                                for result in list_of_results:
                                    if button_ctx.custom_id == str(result['NUMBER']):
                                        await msg.edit(components=[])
                                        
                                        await view_selection(self, ctx, result)
                                        return                 
                                if button_ctx.custom_id == "cancel":
                                    await msg.edit(components=[])
                                    
                                    return
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("You took too long to respond.", hidden=True)
                                return
                        else:
                            pass

                if not response:
                    results = db.viewQuerySearch(f".*{str(name)}.*")
                    list_of_results = []
                    counter = 0
                    if results:
                        for result in results:
                            if result['TYPE'] == "CARDS":
                                list_of_results.append({'TYPE': 'CARD', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the card 🎴 {result['DATA']['NAME']}?", 'DATA': result['DATA']})
                            
                            if result['TYPE'] == "TITLES":
                                list_of_results.append({'TYPE': 'TITLE', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the title 🎗️ {result['DATA']['TITLE']}?", 'DATA': result['DATA']})
                            
                            if result['TYPE'] == "ARM":
                                list_of_results.append({'TYPE': 'ARM', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the arm 🦾 {result['DATA']['ARM']}", 'DATA': result['DATA']})
                            
                            if result['TYPE'] == "PET":
                                list_of_results.append({'TYPE': 'PET', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the summon 🐦 {result['DATA']['PET']}", 'DATA': result['DATA']})
                            
                            if result['TYPE'] == "UNIVERSE":
                                list_of_results.append({'TYPE': 'UNIVERSE', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the universe 🌍 {result['DATA']['TITLE']}", 'DATA': result['DATA']})
                            
                            if result['TYPE'] == "BOSS":
                                list_of_results.append({'TYPE': 'BOSS', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the boss 👹 {result['DATA']['NAME']}", 'DATA': result['DATA']})
                            
                            if result['TYPE'] == "HALL":
                                list_of_results.append({'TYPE': 'HALL', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the hall ⛩️ {result['DATA']['HALL']}", 'DATA': result['DATA']})
                            
                            if result['TYPE'] == "HOUSE":
                                list_of_results.append({'TYPE': 'HOUSE', 'NUMBER': result['INDEX'], 'TEXT': f"Did you mean the house 🏠 {result['DATA']['HOUSE']}", 'DATA': result['DATA']})
                        
                    if list_of_results:
                        message = [f"{result['TEXT']}\n\n" for result in list_of_results]
                        me = ''.join(message)
                        embedVar = Embed(title="Did you mean?...", description=textwrap.dedent(f"""\
                        {me}
                        """), color=0xf1c40f)

                        buttons = []
                        
                        for result in list_of_results:
                            if result['TYPE'] == "CARD":
                                buttons.append(
                                    Button(
                                        style=ButtonStyle.BLUE,
                                        label=f"🎴 {result['DATA']['NAME']}",
                                        custom_id=f"{str(result['NUMBER'])}"
                                    )
                                )
                            
                            if result['TYPE'] == "TITLE":
                                buttons.append(
                                    Button(
                                        style=ButtonStyle.BLUE,
                                        label=f"🎗️ {result['DATA']['TITLE']}",
                                        custom_id=f"{str(result['NUMBER'])}"
                                    )
                                )
                            
                            if result['TYPE'] == "ARM":
                                buttons.append(
                                    Button(
                                        style=ButtonStyle.BLUE,
                                        label=f"🦾 {result['DATA']['ARM']}",
                                        custom_id=f"{str(result['NUMBER'])}"
                                    )
                                )
                            
                            if result['TYPE'] == "PET":
                                buttons.append(
                                    Button(
                                        style=ButtonStyle.BLUE,
                                        label=f"🐦 {result['DATA']['PET']}",
                                        custom_id=f"{str(result['NUMBER'])}"
                                    )
                                )
                            
                            if result['TYPE'] == "UNIVERSE":
                                buttons.append(
                                    Button(
                                        style=ButtonStyle.BLUE,
                                        label=f"🌍 {result['DATA']['TITLE']}",
                                        custom_id=f"{str(result['NUMBER'])}"
                                    )
                                )
                            
                            if result['TYPE'] == "BOSS":
                                buttons.append(
                                    Button(
                                        style=ButtonStyle.BLUE,
                                        label=f"👹 {result['DATA']['NAME']}",
                                        custom_id=f"{str(result['NUMBER'])}"
                                    )
                                )
                            
                            if result['TYPE'] == "HALL":
                                buttons.append(
                                    Button(
                                        style=ButtonStyle.BLUE,
                                        label=f"⛩️ {result['DATA']['HALL']}",
                                        custom_id=f"{str(result['NUMBER'])}"
                                    )
                                )
                            
                            if result['TYPE'] == "HOUSE":
                                buttons.append(
                                    Button(
                                        style=ButtonStyle.BLUE,
                                        label=f"🏠 {result['DATA']['HOUSE']}",
                                        custom_id=f"{str(result['NUMBER'])}"
                                    )
                                )

                        buttons.append(Button(
                            style=ButtonStyle.RED,
                            label="❌ Cancel",
                            custom_id="cancel"
                        ))

                        components = ActionRow(*buttons)
                        

                        msg = await ctx.send(embed=embedVar, components=components)
                        
                        def check(component: Button) -> bool:
                            return component.ctx.author == ctx.author

                        try:
                            button_ctx  = await self.bot.wait_for_component(components=components, check=check, timeout=300)
                            event = button_ctx.ctx

                            for result in list_of_results:
                                if event.custom_id == str(result['NUMBER']):
                                    await msg.edit(components=[])
                                    # await event.defer(ignore_check=True)
                                    await view_selection(self, ctx, result)
                                    return                 
                            if event.custom_id == "cancel":
                                await msg.delete()
                                # await event.defer(ignore_check=True)
                                return
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                            await ctx.send("You took too long to respond.", hidden=True)
                            return
                    else:
                        pass

                regex_pattern = r'.*\belements\b.*'
                
                if re.match(regex_pattern, name):
                    embedVar = Embed(title= f"What does each element do?", description=h.ELEMENTS, color=0x7289da)
                    embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
                    await ctx.send(embed=embedVar)
                    return

                if re.search(r"(manual|help|guide)", name):
                    await self.bot.animevs(ctx)
                    return

                if re.search(r"(enhancers|passives|talents)", name):
                    await self.bot.enhancers(ctx)
                    return

                
                await ctx.send("No results found.", hidden=True)
                return

            if not advanced_search and not name:
                embed = Embed(title="Whoops!", description="Please enter a Name or an Advanced Search term.", color=0xff0000)
                await ctx.send(embed=embed)
                return
        
        except Exception as ex:
            print(ex)
            embed = Embed(title="View Error", description="Something went wrong. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed)
            return

    @view.autocomplete("advanced_search")
    async def view_autocomplete(self, ctx: AutocompleteContext):        
        choices = []
        options = crown_utilities.autocomplete_advanced_search
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


    async def direct_selection(self, ctx, results):
        print("Hello Direct Selection")
        message = [f"{result['TEXT']}\n\n" for result in results]
        me = ''.join(message)
        embedVar = Embed(title="Did you mean?...", description=textwrap.dedent(f"""\
        {me}
        """), color=0xf1c40f)

        buttons = []
        
        for result in results:
            if result['TYPE'] == "CARDS":
                buttons.append(
                    Button(
                        style=ButtonStyle.BLUE,
                        label=f"🎴 {result['DATA']['NAME']}",
                        custom_id=f"{str(result['NUMBER'])}"
                    )
                )
            
            if result['TYPE'] == "TITLES":
                buttons.append(
                    Button(
                        style=ButtonStyle.BLUE,
                        label=f"🎗️ {result['DATA']['TITLE']}",
                        custom_id=f"{str(result['NUMBER'])}"
                    )
                )
            
            if result['TYPE'] == "ARM":
                buttons.append(
                    Button(
                        style=ButtonStyle.BLUE,
                        label=f"🦾 {result['DATA']['ARM']}",
                        custom_id=f"{str(result['NUMBER'])}"
                    )
                )
            
            if result['TYPE'] == "PET":
                buttons.append(
                    Button(
                        style=ButtonStyle.BLUE,
                        label=f"🐦 {result['DATA']['PET']}",
                        custom_id=f"{str(result['NUMBER'])}"
                    )
                )
            
            if result['TYPE'] == "UNIVERSE":
                buttons.append(
                    Button(
                        style=ButtonStyle.BLUE,
                        label=f"🌍 {result['DATA']['TITLE']}",
                        custom_id=f"{str(result['NUMBER'])}"
                    )
                )
            
            if result['TYPE'] == "BOSS":
                buttons.append(
                    Button(
                        style=ButtonStyle.BLUE,
                        label=f"👹 {result['DATA']['NAME']}",
                        custom_id=f"{str(result['NUMBER'])}"
                    )
                )
            
            if result['TYPE'] == "HALL":
                buttons.append(
                    Button(
                        style=ButtonStyle.BLUE,
                        label=f"⛩️ {result['DATA']['HALL']}",
                        custom_id=f"{str(result['NUMBER'])}"
                    )
                )
            
            if result['TYPE'] == "HOUSE":
                buttons.append(
                    Button(
                        style=ButtonStyle.BLUE,
                        label=f"🏠 {result['DATA']['HOUSE']}",
                        custom_id=f"{str(result['NUMBER'])}"
                    )
                )

        buttons.append(Button(
            style=ButtonStyle.RED,
            label="❌ Cancel",
            custom_id="cancel"
        ))
        buttons_action_row = ActionRow(*buttons)

        msg = await ctx.send(embed=embedVar, components=[buttons_action_row])
        
        def check(component: Button) -> bool:
            return button_ctx.author == ctx.author

        try:
            button_ctx  = await self.bot.wait_for_component(components=[buttons_action_row, buttons], timeout=300, check=check)

            if button_ctx.custom_id in ["0", "1", "2", "3", "4"]:
                if results["NUMBER"] == int(button_ctx.custom_id):
                    await view_selection(ctx, results["DATA"])
                    return
            if button_ctx.custom_id == "cancel":
                await msg.delete()    
                return
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("You took too long to respond.", hidden=True)
            return


    @slash_command(description="View all available Universes and their cards, summons, destinies, and accessories")
    async def universes(self, ctx: InteractionContext):
        
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        try:
            universe_data = list(db.queryAllUniverse())
            universe_subset = random.sample(universe_data, k=min(len(universe_data), 25))

            # user = db.queryUser({'DID': str(ctx.author.id)})
            universe_embed_list = []
            for uni in universe_subset:
                available = ""
                # if len(uni['CROWN_TALES']) > 2:
                if uni['CROWN_TALES']:
                    available = f"{crown_utilities.crest_dict[uni['TITLE']]}"
                    
                    tales_list = ", ".join(uni['CROWN_TALES'])

                    embedVar = Embed(title= f"{uni['TITLE']}", description=textwrap.dedent(f"""
                    {crown_utilities.crest_dict[uni['TITLE']]} **Number of Fights**: ⚔️ **{len(uni['CROWN_TALES'])}**

                    ⚔️ **Tales Order**: {tales_list}
                    """))
                    embedVar.set_image(url=uni['PATH'])
                    universe_embed_list.append(embedVar)
                

            buttons = [
                Button(style=3, label="🎴 Cards", custom_id="cards"),
                Button(style=1, label="🎗️ Titles", custom_id="titles"),
                Button(style=1, label="🦾 Arms", custom_id="arms"),
                Button(style=1, label="🧬 Summons", custom_id="summons"),
                Button(style=2, label="✨ Destinies", custom_id="destinies")
            ]
            custom_action_row = ActionRow(*buttons)

            async def custom_function(self, button_ctx):
                universe_name = str(button_ctx.origin_message.embeds[0].title)
                await button_ctx.defer(ignore=True)
                if button_ctx.author == ctx.author:
                    if button_ctx.custom_id == "cards":
                        await cardlist(self, ctx, universe_name)
                        #self.stop = True
                    if button_ctx.custom_id == "titles":
                        await titlelist(self, ctx, universe_name)
                        #self.stop = True
                    if button_ctx.custom_id == "arms":
                        await armlist(self, ctx, universe_name)
                        #self.stop = True
                    if button_ctx.custom_id == "summons":
                        await summonlist(self, ctx, universe_name)
                        #self.stop = True
                    if button_ctx.custom_id == "destinies":
                        await destinylist(self, ctx, universe_name)
                        #self.stop = True
                else:
                    await ctx.send("This is not your command.")


            await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=universe_embed_list, customActionRow=[
                custom_action_row,
                custom_function,
            ]).run()


        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))


    @slash_command(description="View all Homes for purchase")
    async def houses(self, ctx: InteractionContext):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return
        try:
            house_data = db.queryAllHouses()

            house_list = []
            for homes in house_data:
                house_list.append(
                    f"🏠 | **{homes['HOUSE']}**\n🪙 | **COST: **{'{:,}'.format(homes['PRICE'])}\n:part_alternation_mark: | **MULT: **{homes['MULT']}x\n_______________")

            total_houses = len(house_list)

            embed_list = []
            for i in range(0, len(house_list), 5):
                sublist = house_list[i:i + 5]
                embedVar = Embed(title=f"🏠 House List",description="\n".join(sublist), color=0x7289da)
                embedVar.set_footer(text=f"{total_houses} Total Houses\n/view *House Name* `🏠 It's a House` - View House Details")
                embed_list.append(embedVar)

            paginator = Paginator.create_from_embeds(self.bot, *embed_list)
            await paginator.send(ctx)
        except Exception as ex:
            print(ex)
            embed = Embed(title="Houses Error", description="Something went wrong. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed)
            return


    @slash_command(description="View all Halls for purchase")
    async def halls(self, ctx: InteractionContext):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        try:
            hall_data = db.queryAllHalls()

            hall_list = []
            for homes in hall_data:
                hall_list.append(f"🎏 | **{homes['HALL']}**\n🛡️ | **DEF: **{homes['DEFENSE']}\n🪙 | **COST: **{'{:,}'.format(homes['PRICE'])}\n:part_alternation_mark: | **MULT: **{homes['MULT']}x\n💰 | **SPLIT: **{'{:,}'.format(homes['SPLIT'])}x\n:yen: | **FEE: **{'{:,}'.format(homes['FEE'])}\n_______________")

            total_halls = len(hall_list)

            embed_list = []
            for i in range(0, len(hall_list), 5):
                sublist = hall_list[i:i+5]
                embedVar = Embed(title=f"🎏 Hall List", description="\n".join(sublist), color=0x7289da)
                embedVar.set_footer(text=f"{total_halls} Total Halls\n/view Hall Name `🎏 It's A Hall` - View Hall Details")
                embed_list.append(embedVar)


            paginator = Paginator.create_from_embeds(self.bot, *embed_list)
            await paginator.send(ctx)
        except Exception as e:
            print(e)
            embed = Embed(title="Halls Error", description="Something went wrong. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed)
            return


def setup(bot):
    Views(bot)


async def view_selection(self, ctx, result):
    if result['TYPE'] == "CARD":
        await viewcard(self, ctx, result['DATA'])
        return
    
    if result['TYPE'] == "TITLE":
        await viewtitle(self, ctx, result['DATA'])
        return
    
    if result['TYPE'] == "ARM":
        await viewarm(self, ctx, result['DATA'])
        return
    
    if result['TYPE'] == "PET":
        await viewsummon(self, ctx, result['DATA'])
        return
    
    if result['TYPE'] == "UNIVERSE":
        await viewuniverse(self, ctx, result['DATA'])
        return
    
    if result['TYPE'] == "BOSS":
        await viewboss(self, ctx, result['DATA'])
        return
    
    if result['TYPE'] == "HALL":
        await viewhall(self, ctx, result['DATA'])
        return
    
    if result['TYPE'] == "HOUSE":
        await viewhouse(self, ctx, result['DATA'])
        return


async def viewcard(self, ctx, data):
    query = {'DID': str(ctx.author.id)}
    d = db.queryUser(query)
    card = data
    try:
        if card:
            if "FPATH" not in card:
                card['FPATH'] = card['PATH']

            c = crown_utilities.create_card_from_data(card)
            title = {'TITLE': 'CARD PREVIEW'}
            arm = {'ARM': 'CARD PREVIEW'}

            if c.is_universe_unbound():
                await ctx.send("You cannot view this card at this time. ", hidden=True)
                return
            c.set_tip_and_view_card_message()
            evasion = c.get_evasion()
            evasion_message = f"{c.speed}"
            if c.speed >= 70 or c.speed <=30:
                if c.speed >= 70:     
                    if d['PERFORMANCE']:
                        evasion_message = f"{c.speed}: *{round(c.evasion)}% evasion*"
                    else:
                        evasion_message = f"{c.speed}: {round(c.evasion)}% evasion"
                elif c.speed <= 30:
                    if d['PERFORMANCE']:
                        evasion_message = f"{c.speed}: *{c.evasion}% evasion*"
                    else:
                        evasion_message = f"{c.speed}: {c.evasion}% evasion"
            att = 0
            defe = 0
            turn = 0

            active_pet = {}
            pet_ability_power = 0
            card_exp = 150

            # Temporarily removed ♾️ {c.set_trait_message()}
            if d['PERFORMANCE']:
                embedVar = Embed(title=f"{c.drop_emoji} {c.price_message} {c.name} [{crown_utilities.class_emojis[c.card_class]}]", description=textwrap.dedent(f"""\
                {crown_utilities.class_emojis[c.card_class]} | {c.class_message}
                🀄 | {c.tier}
                ❤️ | {c.max_health}
                🗡️ | {c.attack}
                🛡️ | {c.defense}
                🏃 | {evasion_message}

                {c.move1_emoji} | {c.move1}: {c.move1ap}
                {c.move2_emoji} | {c.move2}: {c.move2ap}
                {c.move3_emoji} | {c.move3}: {c.move3ap}
                🦠 | {c.move4}: {c.move4enh} {c.move4ap} {crown_utilities.enhancer_suffix_mapping[c.move4enh]}

                🩸 | {c.passive_name}: {c.passive_type} {c.passive_num}{crown_utilities.passive_enhancer_suffix_mapping[c.passive_type]}
                """), color=000000)
                embedVar.add_field(name="__Affinities__", value=f"{c.set_affinity_message()}")
                embedVar.set_footer(text=f"{c.tip}")
                await ctx.send(embed=embedVar)

            else:
                embedVar = Embed(title=f"", color=000000)
                embedVar.add_field(name="__Affinities__", value=f"{c.set_affinity_message()}")
                embedVar.add_field(name="__Class__", value=f"{crown_utilities.class_emojis[c.card_class]} {c.class_message}", inline=False)
                embedVar.set_image(url="attachment://image.png")
                embedVar.set_thumbnail(url=c.set_universe_image())
                embedVar.set_author(name=textwrap.dedent(f"""\
                {c.drop_emoji} {c.price_message}
                
                Passive
                🩸 {c.passive_name}: {c.passive_type} {c.passive_num}{crown_utilities.passive_enhancer_suffix_mapping[c.passive_type]}
                🏃 {evasion_message}
                """))
                embedVar.set_footer(text=f"{c.tip}")
                image_binary = c.showcard("non-battle", "none", title, 0, 0)
                image_binary.seek(0)
                card_file = File(file_name="image.png", file=image_binary)
                await ctx.send(file=card_file, embed=embedVar)
                image_binary.close()
        else:
            embed = Embed(title=f"🎴 Whoops!", description=f"That card does not exist.", color=000000)
            await ctx.send(embed=embed)
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        return
        embedVar = Embed(title=f"🎴 Whoops!", description=f"There was an issue with loading the card.", color=000000)
        await ctx.send(embed=embedVar)


async def viewtitle(self, ctx, data):
    try:
        if data:
            user = db.queryUser({"DID": str(ctx.author.id)})
            player = crown_utilities.create_player_from_data(user)
            t = crown_utilities.create_title_from_data(data)
            t.set_unlock_method_message(player)

            embedVar = Embed(title=f"🎗️ | {t.name}\n{crown_utilities.crest_dict[t.universe]} | {t.universe}".format(self), color=000000)
            if t.universe != "Unbound":
                embedVar.set_thumbnail(url=t.title_img)
            embedVar.add_field(name=f"**Title Effects**", value="\n".join(t.title_messages), inline=False)
            embedVar.add_field(name=f"**How To Unlock**", value=f"{t.unlock_method_message}", inline=False)
            await ctx.send(embed=embedVar)

        else:
            embed = Embed(title="🎗️ Whoops!", description="That title does not exist.", color=000000)
            await ctx.send(embed=embed)
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))


async def viewarm(self, ctx, data):
    arm = data
    try:
        if arm:
            a = Arm(arm['ARM'], arm['UNIVERSE'], arm['PRICE'], arm['ABILITIES'], arm['EXCLUSIVE'], arm['AVAILABLE'], arm['ELEMENT'])
            embedVar = Embed(title=f"🦾 | {a.name}\n{crown_utilities.crest_dict[a.universe]} | {a.universe}\n{a.price_message}".format(self), color=000000)
            if a.universe != "Unbound":
                embedVar.set_thumbnail(url=a.show_img)

            if a.is_move():
                # embedVar.add_field(name=f"Arm Move Element", value=f"{element}", inline=False)
                embedVar.add_field(name=f"{a.type_message} {a.element.title()} Attack", value=f"{a.element_emoji} | **{a.name}**: **{a.passive_value}**\n *{a.element_ability}*", inline=False)
                # embedVar.add_field(name=f":sunny: | Elemental Effect", value=f"*{a.element_ability}*", inline=False)
                embedVar.set_footer(text=f"The new {a.type_message} attack will reflect on your card when equipped")

            else:
                embedVar.add_field(name=f"Unique Passive", value=f"Increases {a.type_message} by **{a.passive_value}**", inline=False)
                embedVar.set_footer(text=f"{a.passive_type}: {crown_utilities.enhancer_mapping[a.passive_type]}")

            await ctx.send(embed=embedVar)

        else:
            await ctx.send(m.ARM_DOESNT_EXIST, hidden=True)
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        return


async def viewsummon(self, ctx, data):
    pet = data
    try:
        if pet:
            s = crown_utilities.create_summon_from_data(pet)
            # s.set_messages()

            image_binary = crown_utilities.showsummon(s.path, s.name, s.value, 0, 0)
            image_binary.seek(0)
            summon_file = File(file_name="summon.png", file=image_binary)
            embedVar = Embed(title=f"Summon".format(self), color=000000)
            if s.is_not_universe_unbound:
                embedVar.set_thumbnail(url=s.show_img)
                        
            embedVar.set_image(url="attachment://summon.png")

            await ctx.send(file=summon_file)

        else:
            await ctx.send(m.PET_DOESNT_EXIST, hidden=True)
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        return


async def viewuniverse(self, ctx, data):
    try:
        universe = data
        universe_name = universe['TITLE']
        ttitle = "Starter"
        tarm = "Stock"
        dtitle = "Reborn"
        darm = "Reborn Stock"
        dpet = "Chick"
        boss = "Bossless"
        crest = crown_utilities.crest_dict['Unbound']
        prerec = ""
        owner = "PCG"
        traits = ut.traits
        if universe:
            universe_title= universe['TITLE']
            fights = len(universe['CROWN_TALES'])
            dungeon_fights = len(universe['DUNGEONS'])
            crest = crown_utilities.crest_dict[universe_title]
            universe_image = universe['PATH']
            ttitle = universe['UTITLE']
            tarm = universe['UARM']
            dtitle = universe['DTITLE']
            darm = universe['DARM']
            upet = universe['UPET']
            dpet = universe['DPET']
            boss = universe['UNIVERSE_BOSS']
            tier = universe['TIER']
            bossmessage = f"*/view {boss} 👹 It's A Boss*"
            if boss == "":
                bossmessage = f"No {universe_title} Boss available yet!"
            prerec = universe['PREREQUISITE']
            
            prerecmessage = f"Compelete the {prerec} Tale to unlock this Universe!"
            if prerec == "":
                if tier == 9:
                    prerec = "Crown Rift"
                    prerecmessage = "Complete Battles To Open Crown Rifts!"
                else:
                    prerec = "Starter Universe"
                    prerecmessage = "Complete this Tale to unlock rewards!"
            owner = universe['GUILD']
            ownermessage = f"{universe_title} is owned by the {owner} Guild!"
            if owner == "PCG":
                owner = "Crest Unclaimed"
                ownermessage = "*Complete the **Dungeon** and Claim this Universe for your Guild!*"
                
            
            mytrait = {}
            traitmessage = ''
            for trait in traits:
                if trait['NAME'] == universe_title:
                    mytrait = trait
                if universe_title == 'Kanto Region' or universe_title == 'Johto Region' or universe_title == 'Kalos Region' or universe_title == 'Unova Region' or universe_title == 'Sinnoh Region' or universe_title == 'Hoenn Region' or universe_title == 'Galar Region' or universe_title == 'Alola Region':
                    if trait['NAME'] == 'Pokemon':
                        mytrait = trait
            if mytrait:
                traitmessage = f"**{mytrait['EFFECT']}**| {mytrait['TRAIT']}"
                

            embedVar = Embed(title=f"🌍 | {universe_title} ⚔️ {fights} 🔥 {dungeon_fights} ", description=textwrap.dedent(f"""
            {crest} | **{ownermessage}**
            
            :japanese_ogre: | **Universe Boss**
            🎴 | **Card** - {boss}
            {bossmessage}
            :infinity: | **Universe Trait** - {traitmessage}
            """), color=000000)
            embedVar.set_image(url=universe_image)
            embedVar.set_footer(text=f"{universe_title} Details")

            await ctx.send(embed=embedVar)

        else:
            await ctx.send(m.UNIVERSE_DOES_NOT_EXIST)
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        await ctx.send(f"Error when viewing universe. Alert support. Thank you!")
        return


async def viewhouse(self, ctx, data):
    house = data
    if house:
        house_house = house['HOUSE']
        house_price = house['PRICE']
        house_img = house['PATH']
        house_multiplier = house['MULT']

        message=""
        
        price_message ="" 
        price_message = f"🪙 {'{:,}'.format(house_price)}"


        embedVar = Embed(title=f"{house_house}\n{price_message}".format(self), color=000000)
        embedVar.set_image(url=house_img)
        embedVar.add_field(name="Income Multiplier", value=f"Family earns **{house_multiplier}x** 🪙 per match!", inline=False)
        embedVar.set_footer(text=f"/houses - House Menu")

        await ctx.send(embed=embedVar)

    else:
        await ctx.send(m.HOUSE_DOESNT_EXIST, delete_after=3)


async def viewhall(self, ctx, data):
    hall = data
    if hall:
        hall_hall = hall['HALL']
        hall_price = hall['PRICE']
        hall_img = hall['PATH']
        hall_multiplier = hall['MULT']
        hall_fee = hall['FEE']
        hall_split = hall['SPLIT']
        hall_def = hall['DEFENSE']

        message=""
        
        price_message ="" 
        price_message = f"🪙 {'{:,}'.format(hall_price)}"


        embedVar = Embed(title=f"{hall_hall}\n{price_message}", color=000000)
        embedVar.set_image(url=hall_img)
        embedVar.add_field(name="Bounty Fee", value=f"**{'{:,}'.format(hall_fee)}** :yen: per **Raid**!", inline=False)
        embedVar.add_field(name="Multiplier", value=f"Association earns **{hall_multiplier}x** 🪙 per match!", inline=False)
        embedVar.add_field(name="Split", value=f"**Guilds** earn **{hall_split}x** 🪙 per match!", inline=False)
        embedVar.add_field(name="Defenses", value=f"**Shield** Defense Boost: **{hall_def}x**", inline=False)
        embedVar.set_footer(text=f"/halls - Hall Menu")

        await ctx.send(embed=embedVar)

    else:
        await ctx.send(m.HALL_DOESNT_EXIST, delete_after=3)


async def viewboss(self, ctx, data):
    try:
        uboss = data
        if uboss:
            uboss_name = uboss['NAME']
            uboss_show = uboss['UNIVERSE']
            uboss_title = uboss['TITLE']
            uboss_arm = uboss['ARM']
            uboss_desc = uboss['DESCRIPTION'][3]
            uboss_pic = uboss['PATH']
            uboss_pet = uboss['PET']
            uboss_card = uboss['CARD']

            arm = db.queryArm({'ARM': uboss_arm})
            arm_passive = arm['ABILITIES'][0]
            arm_passive_type = list(arm_passive.keys())[0]
            arm_passive_value = list(arm_passive.values())[0]

            title = db.queryTitle({'TITLE': uboss_title})
            title_passive = title['ABILITIES'][0]
            title_passive_type = list(title_passive.keys())[0]
            title_passive_value = list(title_passive.values())[0]
            
            pet = db.querySummon({'PET': uboss_pet})
            pet_ability = pet['ABILITIES'][0]
            pet_ability_name = list(pet_ability.keys())[0]
            pet_ability_type = list(pet_ability.values())[1]
            pet_ability_value = list(pet_ability.values())[0]

            traits = ut.traits

            if uboss_show != 'Unbound':
                uboss_show_img = db.queryUniverse({'TITLE': uboss_show})['PATH']
            message= uboss_desc
            
            mytrait = {}
            traitmessage = ''
            for trait in traits:
                if trait['NAME'] == uboss_show:
                    mytrait = trait
                if uboss_show == 'Kanto Region' or uboss_show == 'Johto Region' or uboss_show == 'Kalos Region' or uboss_show == 'Unova Region' or uboss_show == 'Sinnoh Region' or uboss_show == 'Hoenn Region' or uboss_show == 'Galar Region' or uboss_show == 'Alola Region':
                    if trait['NAME'] == 'Pokemon':
                        mytrait = trait
            if mytrait:
                traitmessage = f"**{mytrait['EFFECT']}**| {mytrait['TRAIT']}"
            
            embedVar = Embed(title=f":japanese_ogre: | {uboss_name}\n🌍 | {uboss_show} Boss", description=textwrap.dedent(f"""
            *{message}*
            
            🎴 | **Card** - {uboss_card}
            🎗️ | **Title** - {uboss_title}: **{title_passive_type}** - {title_passive_value}
            🦾 | **Arm** - {uboss_arm}: **{arm_passive_type}** - {arm_passive_value}
            🧬 | **Summon** - {uboss_pet}: **{pet_ability_type}**: {pet_ability_value}
            
            :infinity: | **Universe Trait** - {traitmessage}
            """), color=000000)
            if uboss_show != "Unbound":
                embedVar.set_thumbnail(url=uboss_show_img)
            embedVar.set_image(url=uboss_pic)

            await ctx.send(embed=embedVar)


        else:
            await ctx.send(m.BOSS_DOESNT_EXIST, delete_after=3)
        
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        await ctx.send(f"Error when viewing boss. Alert support. Thank you!")
        return


async def advanced_card_search(self, ctx, advanced_search_item):
    try:
        if advanced_search_item in crown_utilities.elements:
            cards = [x for x in db.queryCardsByElement(advanced_search_item)]
            suffix = "Element"
        elif advanced_search_item in crown_utilities.class_mapping:
            cards = [x for x in db.queryCardsByClass(advanced_search_item)]
            suffix = "Class"
        else:
            cards = [x for x in db.queryCardsByPassive(advanced_search_item)]
            suffix = "Passive / Enhancer"

        all_cards = []
        embed_list = []

        sorted_card_list = sorted(cards, key=lambda card: card["NAME"])
        for index, card in enumerate(sorted_card_list):
            moveset = card['MOVESET']
            move3 = moveset[2]
            move2 = moveset[1]
            move1 = moveset[0]
            basic_attack_emoji = crown_utilities.set_emoji(list(move1.values())[2])
            super_attack_emoji = crown_utilities.set_emoji(list(move2.values())[2])
            ultimate_attack_emoji = crown_utilities.set_emoji(list(move3.values())[2])
            
            class_info = card['CLASS']
            class_emoji = crown_utilities.class_emojis[class_info]
            class_message = class_info.title()

            
            universe_crest = crown_utilities.crest_dict[card['UNIVERSE']]
                
            available = ""
            if card['DROP_STYLE'] == "DESTINY" or card['DROP_STYLE'] == "SCENARIO":
                emoji = "✨"

            if card['DROP_STYLE'] == "DUNGEON":
                emoji = "🔥"

            if card['DROP_STYLE'] == "TALES":
                emoji = "🎴"

            if card['DROP_STYLE'] == "BOSS":
                emoji = "👹"

            all_cards.append(f"{universe_crest} : 🀄 **{card['TIER']}** **{card['NAME']}** [{class_emoji}] {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n❤️ {card['HLT']} 🗡️ {card['ATK']} 🛡️ {card['DEF']}\n")

        for i in range(0, len(all_cards), 10):
            sublist = all_cards[i:i+10]
            embedVar = Embed(title=f"Advanced Search by {advanced_search_item.capitalize()} {suffix}", description="\n".join(sublist), color=0x7289da)
            embed_list.append(embedVar)

        pagination = Paginator.create_from_embeds(self.bot, *embed_list, timeout=160)
        await pagination.send(ctx)
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        embed = Embed(title="View Error", description="Error when advance searching. Alert support. Thank you!", color=0xff0000)
        await ctx.send(embed=embed)
