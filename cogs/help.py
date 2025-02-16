from cogs.classes.custom_paginator import CustomPaginator
import db
import time
from choicemanager import ChoicesManager
import help_commands as h
import textwrap
from logger import loggy
import textwrap
import unique_traits as ut
now = time.asctime()
from interactions.ext.paginators import Paginator
from interactions import listen, slash_command, InteractionContext, SlashCommandOption, OptionType, Embed, AutocompleteContext, slash_option, Extension
import crown_utilities



class Help(Extension):
    def __init__(self,bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        # self.bot.logger.info(f"Help cog loaded at {now}")
        loggy.info('Help Cog is ready')
    
    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)
            
    @slash_command(name="help", description="Learn the commands", options=[
                            SlashCommandOption(
                                    name="selection",
                                    description="select an option you need help with",
                                    type=OptionType.STRING,
                                    required=True,
                                    autocomplete=True
                                )
                            ]
        ,scopes=crown_utilities.guild_ids)
    async def help(self, ctx, selection: str):
        avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"
        language = self.bot.language_cache.get_user_language(db.users_col, ctx.author.id)
        
        if selection == "menu":
            #Create a paginator using the embed list above
            # {bot.get_text(ctx.author.id, "help.commands.ctap_commands", language)}
            embed1 = Embed(title=f"🎒 | Build Commands", description=h.CTAP_COMMANDS, color=0x7289da)
            embed1.set_thumbnail(url=avatar)

            embed2 = Embed(title=f"🏪 | Shop Commands", description=h.SHOP_COMMANDS, color=0x7289da)
            embed2.set_thumbnail(url=avatar)

            embed3 = Embed(title=f"💱 | Trade Commands", description=h.TRADE_COMMANDS, color=0x7289da)
            embed3.set_thumbnail(url=avatar)

            embed4 = Embed(title=f"⌨️ | Rewards Commands", description=h.REWARDS_COMMANDS, color=0x7289da)
            embed4.set_thumbnail(url=avatar)

            embed_list = [embed1, embed2, embed3, embed4]
            paginator = Paginator.create_from_embeds(self.bot, *embed_list)
            paginator.show_select_menu = True
            await paginator.send(ctx)
            # return

        if selection == "legend":
            #Create a paginator using the embed list above
            embed1 = Embed(title=f"🎴 | Card Emojis", description=h.CARD_LEGEND, color=0x7289da)
            embed1.set_thumbnail(url=avatar)

            embed2 = Embed(title=f"🎒 | Equipment Emojis", description=h.EQUIPMENT_LEGEND, color=0x7289da)
            embed2.set_thumbnail(url=avatar)

            embed3 = Embed(title=f"🪙 | Currency Emojis", description=h.CURRENCY_LEGEND, color=0x7289da)
            embed3.set_thumbnail(url=avatar)

            embed_list = [embed1, embed2, embed3]
            paginator = Paginator.create_from_embeds(self.bot, *embed_list)
            paginator.show_select_menu = True
            await paginator.send(ctx)

        if selection == "elements":
            embed_list = []
            for i in range(0, len(h.ELEMENTS_LIST), 5):
                    sublist = h.ELEMENTS_LIST[i:i + 5]
                    embedVar = Embed(title=f"What does each element do?",description="\n".join(sublist), color=0x7289da)
                    embedVar.set_footer(text=f"/play - to access the battle tutorial")
                    embed_list.append(embedVar)

            paginator = Paginator.create_from_embeds(self.bot, *embed_list)
            paginator.show_select_menu = True
            await paginator.send(ctx)

        if selection == "play":
            #Create a paginator using the embed list above
            embed1 = Embed(title=f"🆕 | Account Register, Delete & Lookup", description=h.CROWN_UNLIMITED_GAMES, color=0x7289da)
            embed1.set_thumbnail(url=avatar)

            embed2 = Embed(title=f"♾️ | PVE Game Modes", description=h.PVE_MODES, color=0x7289da)
            embed2.set_thumbnail(url=avatar)

            embed3 = Embed(title=f"🆚 | PVP Game Modes", description=h.PVP_MODES, color=0x7289da)
            embed3.set_thumbnail(url=avatar)

            embed_list = [embed1, embed2, embed3]
            paginator = Paginator.create_from_embeds(self.bot, *embed_list)
            paginator.show_select_menu = True
            await paginator.send(ctx)

        if selection == "universe":
            embedVar = Embed(title=f"🌍 Universe Info!", description=h.UNIVERSE_STUFF, color=0x7289da)
            embedVar.set_thumbnail(url=avatar)
            embedVar.set_footer(text=f"/play - to access the battle tutorial")
            await ctx.send(embed=embedVar)
            return

        if selection == "teams":
            #Create a paginator using the embed list above
            embed1 = Embed(title=f"🪖 | Guild Information", description=h.BOT_COMMANDS, color=0x7289da)
            embed1.set_thumbnail(url=avatar)

            embed2 = Embed(title=f"👨‍👩‍👧‍👦 | Family Information", description=h.FAMILY_COMMANDS, color=0x7289da)
            embed2.set_thumbnail(url=avatar)

            embed3 = Embed(title=f"🎏 | Association Information", description=h.ASSOCIATION_COMMANDS, color=0x7289da)
            embed3.set_thumbnail(url=avatar)

            embed_list = [embed1, embed2, embed3]
            paginator = Paginator.create_from_embeds(self.bot, *embed_list)
            paginator.show_select_menu = True
            await paginator.send(ctx)
        
        if selection == "options":
            embedVar = Embed(title=f"Play your way!", description=h.OPTION_COMMANDS, color=0x7289da)
            embedVar.set_thumbnail(url=avatar)
            embedVar.set_footer(text=f"/play - to access the battle tutorial")
            await ctx.send(embed=embedVar)
            return

        if selection == "classes":
            await classes(ctx)
            return
        
        if selection == "titles":
            await titles(ctx)
            return

        if selection =="arms":
            await arms(ctx)
            return

        if selection == "enhancers":
            await enhancers(ctx)
            return
            
        if selection == "manual":
            await animevs(ctx)
            return


    @help.autocomplete("selection")
    async def help_autocomplete(self, ctx: AutocompleteContext):
        """Dynamically generate choices based on user's language"""
        # Get user's language preference
        user_language = self.bot.language_cache.get_user_language(db.users_col, ctx.author.id)
        
        # Get all possible choices for user's language
        options = ChoicesManager.get_help_choices(self.bot.translator, user_language)
        choices = []

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

            if not universe:
                embed_list = []
                for trait in traits:
                    universe = db.queryUniverse({'TITLE': trait['NAME']})
                    embedVar = Embed(
                    title=f"{trait['NAME']} Trait",
                    description=textwrap.dedent(f"""
                    **{trait['EFFECT']}**:
                    {trait['TRAIT']}
                    """)
                    )

                    embed_list.append(embedVar)

                paginator = Paginator.create_from_embeds(self.bot, *embed_list)
                paginator.show_select_menu = True
                await paginator.send(ctx)
            else:
                universe = db.queryUniverse({'TITLE': universe})
                if not universe:
                    await ctx.send("That universe does not exist.")
                    return
                for trait in traits:
                    if trait['NAME'] == universe['TITLE']:
                        embedVar = Embed(
                            title=f"{trait['NAME']} Trait",
                            description=textwrap.dedent(f"""
                            **{trait['EFFECT']}**:
                            {trait['TRAIT']}
                            """)
                        )
                    await ctx.send(embed=embedVar)
                    return
                return
        except Exception as ex:
            loggy.error(f"Error in Traits command: {ex}")
            await ctx.send("There's an issue with your Traits List. Check with support.", ephemeral=True)
            return


    @traits.autocomplete("universe")
    async def traits_autocomplete(ctx: AutocompleteContext):
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



async def enhancers(ctx):
   avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"

   try:
      embedVar1 = Embed(title=f"Enhancer Type: Boosts",color=0x7289da)
      embedVar1.set_thumbnail(url=avatar)
      embedVar1.add_field(name="`BOOSTS`", value="**ATK** - Increase Attack By AP %.\n\n**DEF** Increase Defense by AP %.\n\n**HLT** - Increase Health By Flat AP + 16% of Missing Health.\n\n**STAM** - Increase Stamina by Flat AP\n\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)")
      embedVar1.set_footer(text=f"/help - Game Help")

      embedVar2 = Embed(title=f"Enhancer Type: Steals",color=0x7289da)
      embedVar2.set_thumbnail(url=avatar)
      embedVar2.add_field(name="`STEALS`", value="**FLOG**- Steal Opponent Attack and Add it to Your Attack by AP %\n\n**WITHER**- Steal Opponent Defense and Add it to Your Defense by AP %\n\n**LIFE**\nSteal Opponent Health and Add it to your Current Health by Flat AP + 9% of Opponent Current Health. \n\n**DRAIN** - Steal Opponent Stamina and Add it to your Stamina by Flat AP\n\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)")
      embedVar2.set_footer(text=f"/help - Game Help")

      embedVar3 = Embed(title=f"Enhancer Type: Sacrifice",color=0x7289da)
      embedVar3.set_thumbnail(url=avatar)
      embedVar3.add_field(name="`SACRIFICE`", value="**RAGE** - Decrease Your Defense by AP %, Increase All Moves AP by Amount of Decreased Defense\n\n**BRACE** - Decrease Your Attack by AP %, Increase All Moves AP By Amount of Decreased Attack\n\n**BZRK** - Decrease Your Current Health by AP %,  Increase Your Attack by Amount of Decreased Health\n\n**CRYSTAL** - Decrease Your Health by AP %, Increase Your Defense by Amount of Decreased Health\n\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)")
      embedVar3.set_footer(text=f"/help - Game Help")

      embedVar4 = Embed(title=f"Enhancer Type: Conversion",color=0x7289da)
      embedVar4.set_thumbnail(url=avatar)
      embedVar4.add_field(name="`CONVERSION`", value="**STANCE** - Swap Your Attack and Defense, Increase Your Defense By Flat AP\n\n**CONFUSE** - Swap Opponenet Attack and Defense, Decrease Opponent Defense by Flat AP\n\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)")
      embedVar4.set_footer(text=f"/help - Game Help")

      embedVar5 = Embed(title=f"Enhancer Type: Time Manipulation",color=0x7289da)
      embedVar5.set_thumbnail(url=avatar)
      embedVar5.add_field(
         name="`TIME MANIPULATION`", 
         value=(
            "**BLINK**  - Decreases Your Stamina by AP, Increases Opponent Stamina by AP.\n\n"
            "**SLOW** - Decreases the turn total by AP.\n\n"
            "**HASTE** - Increases the turn total by AP.\n\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)"
         )
      )
      embedVar5.set_footer(text="/help - Game Help")

      embedVar6 = Embed(title=f"Enhancer Type: Control",color=0x7289da)
      embedVar6.set_thumbnail(url=avatar)
      embedVar6.add_field(name="`CONTROL`", value="**SOULCHAIN** - You and Your Opponent's Stamina Equal AP\n\n**GAMBLE** - At the cost of your total stamina, You and Your Opponent's Health Equal between 500 & AP value\n\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)")
      embedVar6.set_footer(text=f"/help - Game Help")

      embedVar7 = Embed(title=f"Enhancer Type: Fortitude",color=0x7289da)
      embedVar7.set_thumbnail(url=avatar)
      embedVar7.add_field(name="`FORTITUDE`", value="**GROWTH**- Decrease Your Max Health by 10%, Increase Your Attack, Defense and AP Buff by AP\n\n**FEAR** - Decrease Your Max Health and Health by 20%, Decrease Opponent Attack, Defense, and reduce Opponent AP Buffs by AP\n\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)")
      embedVar7.set_footer(text=f"/help - Game Help")

      embedVar8 = Embed(title=f"Enhancer Type: Damage",color=0x7289da)
      embedVar8.set_thumbnail(url=avatar)
      embedVar8.add_field(name="`DAMAGE`", value="**WAVE** - Deal Flat AP Damage to Opponent. AP Decreases each turn (Can Crit). *If used on turn that is divisible by 10 you will deal 75% AP Damage.*\n\n**BLAST** - Deal Flat AP Damage to Opponent. AP Increases each turn.\n\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)")
      embedVar8.set_footer(text=f"/help - Game Help")

      embedVar9 = Embed(title=f"Enhancer Type: Divinity",color=0x7289da)
      embedVar9.set_thumbnail(url=avatar)
      embedVar9.add_field(name="`DIVINITY`", value="**CREATION** - Increase Max Health by Flat AP. AP Decreases each turn (Can Crit). *If used on turn that is divisible by 10 you will heal Health & Max Health for 75% AP.*\n\n**DESTRUCTION** - Decrease Your Opponent Max Health by Flat AP (only opponent on PET use). AP Increases each turn.\n\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)")
      embedVar9.set_footer(text=f"/help - Game Help")  

      embedVar = Embed(title=f"Card Enhancers", description=textwrap.dedent(f"""\
      __🦠Enhancer Abilities__
                                                                     
      Your Enhancer buffs or debuffs your opponent for 20 Stamina
      
      __Enhancer Categories__
      `BOOSTS`
      `STEALS`
      `SACRIFICE`
      `CONVERSION`
      `TIME MANIPULATION`
      `CONTROL`
      `FORTITUDE`
      `DAMAGE`
      `DIVINITY`

      [Join the Anime VS+ Support Server](https://discord.gg/pcn)                                                 
      """),color=0x7289da)
      embedVar.set_footer(text=f"/help - Game Help")
      embeds = [embedVar, embedVar1, embedVar2, embedVar3, embedVar4, embedVar5, embedVar6, embedVar7, embedVar8, embedVar9]
      paginator = CustomPaginator.create_from_embeds(self.bot, *embeds)
      paginator.show_select_menu = True
      await paginator.send(ctx)
      # await Paginator(self.bot=self.bot, ctx=ctx, pages=embeds, timeout=60).run()
      
   
   except Exception as ex:
            loggy.error(f"Error in enhancers: {ex}")
            await ctx.send("Hmm something ain't right. Check with support.", ephemeral=True)
            return

async def titles(ctx):
    avatar = "https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"
    try:
        # Boosts
        embedVar1 = Embed(title="Title Category: Boosts", color=0x7289da)
        embedVar1.set_thumbnail(url=avatar)
        embedVar1.add_field(name="`ATK`", value="Increases your attack by % each turn", inline=False)
        embedVar1.add_field(name="`DEF`", value="Increases your defense by % each turn", inline=False)
        embedVar1.add_field(name="`STAM`", value="Increases your stamina by % each turn", inline=False)
        embedVar1.add_field(name="`HLT`", value="Heals you for % of your current health each turn\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)", inline=False)
        embedVar1.set_footer(text="/help - Game Help")

        # Steals
        embedVar2 = Embed(title="Title Category: Steals", color=0x7289da)
        embedVar2.set_thumbnail(url=avatar)
        embedVar2.add_field(name="`LIFE`", value="Steals % of your opponent's health each turn", inline=False)
        embedVar2.add_field(name="`DRAIN`", value="Drains % of opponent's stamina each turn", inline=False)
        embedVar2.add_field(name="`FLOG`", value="Steals % of opponent's attack each turn", inline=False)
        embedVar2.add_field(name="`WITHER`", value="Steals % of opponent's defense each turn\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)", inline=False)
        embedVar2.set_footer(text="/help - Game Help")

        # Sacrifice
        embedVar3 = Embed(title="Title Category: Sacrifice", color=0x7289da)
        embedVar3.set_thumbnail(url=avatar)
        embedVar3.add_field(name="`RAGE`", value="Decreases your defense to increase your AP by % each turn", inline=False)
        embedVar3.add_field(name="`BRACE`", value="Decreases your attack to increase your AP by % each turn", inline=False)
        embedVar3.add_field(name="`BZRK`", value="Decreases your health to increase your attack by % each turn", inline=False)
        embedVar3.add_field(name="`CRYSTAL`", value="Decreases your health to increase your defense by % each turn\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)", inline=False)
        embedVar3.set_footer(text="/help - Game Help")

        # Conversion
        embedVar4 = Embed(title="Title Category: Conversion", color=0x7289da)
        embedVar4.set_thumbnail(url=avatar)
        embedVar4.add_field(name="`STANCE`", value="Swaps your attack and defense stats, increasing your attack by % each turn", inline=False)
        embedVar4.add_field(name="`CONFUSE`", value="Swaps opponent's attack and defense stats, decreasing their attack by % each turn\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)", inline=False)
        embedVar4.set_footer(text="/help - Game Help")

        # Time Manipulation
        embedVar5 = Embed(title="Title Category: Time Manipulation", color=0x7289da)
        embedVar5.set_thumbnail(url=avatar)
        embedVar5.add_field(name="`SLOW`", value="Decreases turn count by Turn", inline=False)
        embedVar5.add_field(name="`HASTE`", value="Increases turn count by Turn\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)", inline=False)
        embedVar5.set_footer(text="/help - Game Help")

        # Control
        embedVar6 = Embed(title="Title Category: Control", color=0x7289da)
        embedVar6.set_thumbnail(url=avatar)
        embedVar6.add_field(name="`SOULCHAIN`", value="Prevents focus stat buffs", inline=False)
        embedVar6.add_field(name="`GAMBLE`", value="Randomizes focus stat buffs\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)", inline=False)
        embedVar6.set_footer(text="/help - Game Help")

        # Fortitude
        embedVar7 = Embed(title="Title Category: Fortitude", color=0x7289da)
        embedVar7.set_thumbnail(url=avatar)
        embedVar7.add_field(name="`GROWTH`", value="Decreases your max health to increase your attack, defense, and AP by Flat AP each turn", inline=False)
        embedVar7.add_field(name="`FEAR`", value="Decreases your max health to decrease your opponent's attack, defense, and AP by Flat AP each turn\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)", inline=False)
        embedVar7.set_footer(text="/help - Game Help")

        # Protection Manipulation
        embedVar8 = Embed(title="Title Category: Protections", color=0x7289da)
        embedVar8.set_thumbnail(url=avatar)
        embedVar8.add_field(name="`BLITZ`", value="Hit through parries", inline=False)
        embedVar8.add_field(name="`FORESIGHT`", value="Parried hits deal 10% damage to yourself", inline=False)
        embedVar8.add_field(name="`OBLITERATE`", value="Hit through shields", inline=False)
        embedVar8.add_field(name="`IMPENETRABLE SHIELD`", value="Shields cannot be penetrated", inline=False)
        embedVar8.add_field(name="`PIERCE`", value="Hit through all barriers", inline=False)
        embedVar8.add_field(name="`SYNTHESIS`", value="Hits to your barriers store 50% of damage dealt, you heal from this amount on resolve", inline=False)
        embedVar8.add_field(name="`STRATEGIST`", value="Hits through all guards / protections", inline=False)
        embedVar8.add_field(name="`SHARPSHOOTER`", value="Attacks never miss\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)", inline=False)
        embedVar8.set_footer(text="/help - Game Help")

        # Elemental
        embedVar9 = Embed(title="Title Category: Elemental", color=0x7289da)
        embedVar9.set_thumbnail(url=avatar)
        embedVar9.add_field(name="`SPELL SHIELD`", value="All shields will absorb elemental damage healing you", inline=False)
        embedVar9.add_field(name="`ELEMENTAL BUFF`", value="Increase elemental damage by 50%", inline=False)
        embedVar9.add_field(name="`ELEMENTAL DEBUFF`", value="Decrease opponent's elemental damage by 50%", inline=False)
        embedVar9.add_field(name="`DIVINITY`", value="Ignore elemental effects until resolved\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)", inline=False)
        embedVar9.set_footer(text="/help - Game Help")

        # IQ
        embedVar10 = Embed(title="Title Category: IQ", color=0x7289da)
        embedVar10.set_thumbnail(url=avatar)
        embedVar10.add_field(name="`IQ`", value="Increases focus buffs by %", inline=False)
        embedVar10.add_field(name="`HIGH IQ`", value="Continues focus buffs after resolve", inline=False)
        embedVar10.add_field(name="`SINGULARITY`", value="Increases resolve buff by %\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)", inline=False)
        embedVar10.set_footer(text="/help - Game Help")

        embedVar = Embed(title="Title Effects", description=textwrap.dedent(f"""\
        __🎗️Title Effects__
        
        Your Title buffs your card or debuffs your opponent at the start of your turn or during focus
        
        __Title Categories__
        1.`BOOSTS`
        2.`STEALS`
        3.`SACRIFICE`
        4.`CONVERSION`
        5.`TIME MANIPULATION`
        6.`CONTROL`
        7.`FORTITUDE`
        8.`PROTECTION MANIPULATION`
        9.`ELEMENTAL`
        10.`IQ`

        [Join the Anime VS+ Support Server](https://discord.gg/pcn)
        """), color=0x7289da)
        embedVar.set_footer(text="/help - Game Help")
        embeds = [embedVar, embedVar1, embedVar2, embedVar3, embedVar4, embedVar5, embedVar6, embedVar7, embedVar8, embedVar9, embedVar10]
        paginator = CustomPaginator.create_from_embeds(self.bot, *embeds)
        paginator.show_select_menu = True
        await paginator.send(ctx)
    except Exception as ex:
                loggy.error(f"Error in titles: {ex}")
                await ctx.send("Hmm something ain't right. Check with support.", ephemeral=True)
                return

async def arms(ctx):
    avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"
    try:
        embedVar10 = Embed(title=f"Arm Enhancer Type: Ability",color=0x7289da)
        embedVar10.set_thumbnail(url=avatar)
        embedVar10.add_field(name="`OFFENSE`", value="💥 **BASIC** - Equip a new Basic Attack and Element \n\n☄️ **SPECIAL** - Equip a new Special Attack and Element \n\n🏵️ **ULTIMATE** - Equip a new Ultimate Attack and Element \n\n💮 **ULTIMAX** - Increase Attack Move AP and ATK & DEF by Value \n\n🪬 **MANA** - Increase Attack Move AP and Enhancer AP by Percentage \n\n💉 **SIPHON** - Heal for 10% DMG + AP\n\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)")
        embedVar10.set_footer(text=f"/help - Game Help")
        
        embedVar11 = Embed(title=f"Arm Enhancer Type: Protections",color=0x7289da)
        embedVar11.set_thumbnail(url=avatar)
        embedVar11.add_field(name="`DEFENSE`", value="💠 **BARRIER** - Blocks all Attack Damage until player Attacks or is Destoyed (Enhancers Exempt)\n\n🌐 **SHIELD**- Grant Damage absorbing Shield until destroyed \n\n🔄 **PARRY** - Reflects 50% Damage back to Attacker, reduce incoming damage by 25%\n\n[Join the Anime VS+ Support Server](https://discord.gg/pcn)")
        embedVar11.set_footer(text=f"/help - Game Help")
        
        embedVar = Embed(title=f"Arm Enhancements", description=textwrap.dedent(f"""\
        🦾__Arm Types__
                                                                        
        Your Arm grants you either a protection or ability enhancement in battle.
        
        __Protection Arms__
        🌐 **Shield**
        💠 **Barrier**
        🔄 **Parry** 
        
        __Ability Arms__
        💥 **BASIC**
        ☄️ **SPECIAL**
        🏵️ **ULTIMATE**
        💮 **ULTIMAX**
        🪬 **MANA**
        💉 **SIPHON** 

        [Join the Anime VS+ Support Server](https://discord.gg/pcn)                                                 
        """),color=0x7289da)
        embedVar.set_footer(text=f"/help - Game Help")

        embeds = [embedVar ,embedVar11, embedVar10]
        paginator = CustomPaginator.create_from_embeds(self.bot, *embeds)
        paginator.show_select_menu = True
        await paginator.send(ctx)

    except Exception as ex:
                loggy.error(f"Error in enhancers: {ex}")
                await ctx.send("Hmm something ain't right. Check with support.", ephemeral=True)
                return

async def classes(ctx):
    avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"
        
    class_descriptions = [
            (crown_utilities.class_emojis['SUMMONER'], "Summoner", "Can use Summon from start of battle.\nSummon attacks are boosted based on Card Tier.\nBarrier and Paryy Summons gain 1 charge per tier\nAttack Summons Boost Damage by (20% * Card Tier) AP\n\nCommon - 20%/40%/60%\nRare - 80%/100%\nLegendary - 120%/140%\nMythic - 160%/180%\nGod - 200%\n\nSummons gain double XP after Battle\n[Join the Anime VS+ Support Server](https://discord.gg/pcn) "),
            (crown_utilities.class_emojis['ASSASSIN'], "Assassin", "Starts each fight with up to 6 Sneak Attacks, These cost 0 Stamina, Penetrate all protections and have increased Critical Chance\n\nCommon - 2 Attack\nRare - 3 Attacks\nLegendary - 4 Attacks\nMythic - 5 Attacks\nGod - 6 Attacks.\n\nOn Blitz gain additional Sneak Attacks.\n[Join the Anime VS+ Support Server](https://discord.gg/pcn) "),
            (crown_utilities.class_emojis['FIGHTER'], "Fighter", "Starts each fight with up to 6 Parries and double the value of Shield and Barrier Arms\n\nCommon - 3 Parry\nRare - 4 Parries\nLegendary - 5 Parries\nMythic - 6 Parries\nGod - 7 Parries.\n\nGain 2 Parries with each Physical Damage Proc\n[Join the Anime VS+ Support Server](https://discord.gg/pcn) "),
            (crown_utilities.class_emojis['RANGER'], "Ranger", "Starts each fight with up to 6 Barriers & can attack without disengaging Barriers\n\nCommon - 2 Barriers\nRare - 3 Barriers\nLegendary - 4 Barriers\nMythic - 5 Barriers\nGod - 6 Barriers.\n\nGun & Ranged Damage Increased.\n[Join the Anime VS+ Support Server](https://discord.gg/pcn) "),
            (crown_utilities.class_emojis['TANK'], "Tank", "Starts each fight with (Card Tier * 250) + Card Level Shield & gain the same Shield on Resolve\n\nCommon - 250/500/750 Shield\nRare - 1000/1250\nLegendary - 1500/1750\nMythic - 2000/2250\nGod - 2500.\n\nTriples Defense on Block\n[Join the Anime VS+ Support Server](https://discord.gg/pcn) "),
            (crown_utilities.class_emojis['SWORDSMAN'], "Swordsman", "On Resolve, Gain up to 6 Critical Strikes\n\nCommon - 2 Attack\nRare - 3 Attacks\nLegendary - 4 Attacks\nMythic - 5 Attacks\nGod - 6 Attacks\n\nSword & Bleed damage boosted.\n[Join the Anime VS+ Support Server](https://discord.gg/pcn) "),
            (crown_utilities.class_emojis['MONSTROSITY'], "Monstrosity", "On Resolve gain up to 5 Double Strikes\n\nCommon - 1 Attack\nRare - 2 Attacks\nLegendary - 3 Attacks\nMythic - 4 Attacks\nGod - 5 Attacks.\n[Join the Anime VS+ Support Server](https://discord.gg/pcn) "),
            (crown_utilities.class_emojis['MAGE'], "Mage", "Increases Elemental damage up to 60%\n\nCommon - 35%\nRare - 45%\nLegendary - 50%\nMythic - 55%\nGod - 60%\nElemental damage effects are enhanced\n[Join the Anime VS+ Support Server](https://discord.gg/pcn) "),
            (crown_utilities.class_emojis['HEALER'], "Healer", "Stores up to 70% of damage taken and heals Health and Max Health each Focus\n\nCommon - 30%\nRare - 40%\nLegendary - 50%\nMythic - 60%\nGod - 70%\n\nLifesteal abilities are boosted\n\nStacked Status effects removed on Focus\n[Join the Anime VS+ Support Server](https://discord.gg/pcn) "),
            (crown_utilities.class_emojis['TACTICIAN'], "Tactician", "Enter Focus using Block to craft Strategy Points\n\n1: Gain Parry, Barrier and Shield based on Tier\n\n**Common**\n*1 Parry, 1 Barrier, 100/200/300 Shield*\n**Rare**\n*2 Parry, 2 Barrier, 400/500 Shield*\n**Legendary**\n*3 Parry, 3 Barrier, 600/700 Shield*\n**Mythic**\n*4 Parry, 4 Barrier, 800/900 Shield*\n**God**\n*5 Parry, 5 Barrier, 1000 Shield*\n\n2: Disable Opponents Talisman\n\n3: Craft Tactician Talisman [Bypass All Affinities]\n\n4: Gain 1 Critical Strike and Destroy Opponents Protections\n\n5: Disable Opponents Summon and they become weak to all your Dmg\n[Join the Anime VS+ Support Server](https://discord.gg/pcn) "),
        ]
        
    embed_list = []
    embedVar = Embed(title=f"Classes", description=textwrap.dedent(f"""\
    🥋 **Card Class**
                                                                    
    Your Class grants you a boost in battle
    The boost is determined by your Card Tier Range
                                                                    
    Common : [1 - 3]
    Rare : [4 - 5]
    Legendary : [6 - 7]
    Mythical : [8 - 9]
    God : [10]

    [Join the Anime VS+ Support Server](https://discord.gg/pcn)                                                    
    """),color=0x7289da)
    embed_list.append(embedVar)
    for emoji, title, description in class_descriptions:
            embedVar = Embed(title=title, description=f"{emoji} {description}", color=0x7289da)
            embedVar.set_thumbnail(url=avatar)
            embed_list.append(embedVar)

    paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list)
    paginator.show_select_menu = True
    await paginator.send(ctx)

    # @slash_command(description="Anime VS+ Manual", scopes=crown_utilities.guild_ids)

async def animevs(ctx):
    try:
        avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"


        embedVar1 = Embed(title=f"About Anime VS+",color=0x7289da)
        
        embedVar1.set_thumbnail(url=avatar)
        
        embedVar1.add_field(name="**About The Game!**", value=textwrap.dedent(f"""\
            
        **Anime VS+** is a Multiplatform Card Game exploring **Universes** from your favorite Video Game and Anime Series!

        Explore Tales, Dungeons, and Bosses! Play **Solo**, or with **Friends**!
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)"""))
        
        embedVar0 = Embed(title=f"Getting Started", description=textwrap.dedent(f"""\
        Players begin with 3 cards and arms from their **Starting Universe**.
                                                                        
        You always begin with **Luffy**, **Ichigo** and **Naruto**
        
        You also gain Starting Titles from your universe. 
                                                                        
        The Title **Starter** and the Arm **Stock** are also added.
        
        Your first Summon **Chick** will be joining as well!
            
        Play **Single Player** and **Multiplayer** Modes to earn 🪙
        Buy and equip better Items to Conquer the Multiverse!
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)                                                                  
        """), color=0x7289da)
        
        embedVar0.set_thumbnail(url=avatar)

        embedVar3 = Embed(title=f"Card Basics", description=textwrap.dedent(f"""\
        __Card Basics__
        ♾️ **Universe Traits**
        Universe specific abilities activated during battle. 
        Use **/traits** for a full list.
        
        🥋 **Card Class**
        Your Class determines your speciality in battle
        Use /help to find information on **Classes**
                                                                            
        🀄 **Card Tier**
        Card Tier Determines Base Stats, Class Level and Enhancer Values.
        - **Common:** Level 1 [Tier 1-3]
        - **Rare:** Level 2 [Tier 4-5]
        - **Legendary:** Level 3 [Tier 6-7]
        - **Mythical:** Level 4 [Tier 8-9]
        - **God:** Level 5 [Tier 10]
                                                                            
        🔱**Card Level**
        As you battle your card will level up, increasing Stats and Ability Power 
                                                                            
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)"""), color=0x7289da)
        
        embedVar3.set_thumbnail(url=avatar)

        embedVar3_s = Embed(title=f"Card Stats", description=textwrap.dedent(f"""\
        __Card Stats__                                                       
        - [HP]**Health: When your health reaches 0 you lose
        - [ST]**Stamina:** Used to perform attacks and skills
        - [ATK]**Attack:** Increases damage dealt
        - [DEF]**Defense:** Reduces damage taken
        - [EVA]**Evasion:** Increases chance to dodge attacks
        - [AP]**Ability Power:** Determines the strength of your abilities

        __Card Affinities__
        🔅 **Affinities**
        Affinities determine how you card reacts to **Damage types**
        - Weaknesses: Take more damage
        - Resistances: Take less damage
        - Immunities: Immune to damage
        - Repels: Reflects damage back
        - Absorb: Absorbs damage as Health 
                                                                            
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)"""), color=0x7289da)
        
        embedVar3_s.set_thumbnail(url=avatar)

        embedVar3_1 = Embed(title=f"Card Moveset", description=textwrap.dedent(f"""\
        __Attack Moves__
        Attacks inflict damage on the opponent and apply elemental effects.
        Each Attack matches an **Emoji** and **Stamina Cost** in the Movelist.
        - 💥 Basic Attack _uses 10 stamina_
        - ☄️ Special Attack _uses 30 stamina_
        - 🏵️ Ultimate Attack _uses 80 stamina_
                                                                                
        🔅**Elemental Damage**
        Attacks have bonus effects based on the 🔅**Element** Type
        Use /help to find information on **Elements**
                                                                                
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)"""), color=0x7289da)
        
        embedVar3_1.set_thumbnail(url=avatar)

        embedVar3_2 = Embed(title=f"Card Skills", description=textwrap.dedent(f"""\
        __Skills__
        **Enhancer**
        Enhancers either boost your stats or inflict status effects on your opponent. Use **/help** for full list of **Enhancers** and their effects.
        - 🦠 Enhancer _uses 20 stamina_
        
        **Block**
        Doubles Defense for 1 turn
        - 🛡️ Block _uses 20 stamina_ 
                                                                                
        **Blitz**
        Enters Focus, trades healing for increased Stat boost
        - 💢 Blitz _uses all stamina, can only be used after focus with < 50 stamina_ 
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)"""), color=0x7289da)
        
        embedVar3_2.set_thumbnail(url=avatar)
        
        embedVar11 = Embed(title=f"Card Types", description=textwrap.dedent(f"""
        __Card Types__                                                                           
        🎴 **Universe Cards** - Purchasable in the **Shop** and Drops in **Tales**
        🃏 **Card Skins** - Create in the **/craft**
        👺 **Dungeon Cards** - Drops in **Dungeons**
        ✨ **Destiny Cards** - Earned via **Destinies**
        👹 **Boss Cards** - Exchange for **Boss Souls**                                                                                                                           

        ✨ **Destinies**
        Card Specific Quests in scenarios that earn **Destiny Cards**
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)"""), color=0x7289da)
        
        embedVar11.set_thumbnail(url=avatar)
        
        embedVar17 = Embed(title=f"Damage Calculation", description=textwrap.dedent(f"""    
        __Damage Calculation__                                                                                                                                                             
        🗯️**Engagements** Each of your ATK Moves deals damage based on the **Engagement**.
        - **Brave Engagement**: Opponent DEF > My ATK x 2 [Deal %33-%50 of AP]
        - **Cautious Engagement**: Opponent DEF > My ATK [Deal %50-%90 AP]
        - **Nuetral Engagement**: Your ATK and DEF are nuetral. [Deal %75-%120 AP]
        - **Aggressive Engagement**: My ATK > Opponent DEF [Deal %120-%150 AP]
        - **Lethal Engagement**: Your ATK > Opponent DEF x 2 Deal $150-%200 AP
        
        The Engagement is a factor of Attack + Move Ap vs Opponent Defense
        When your attack is higher than your oppoenents defense you will deal more damage
        
        🏃**Speed**
        Your cards speed determines your evasion stat.
        Evasion [70+]: gain 5% evasion per 10 Speed
        Slow [30-]: lose 5% evasion per 10 Speed
        - **God** Cards SPD [75+]
        - **Fast** Cards SPD [70-100]
        - **Nuetral** Cards SPD [31-69]
        - **Slow** Cards SPD [0-30]
        
        🧮**Strike Calculation**
        Your ability also deals damage based on the type of **Strike**
        Strike is determined by your Move Accuracy vs Opponent Evasion
        :palm_down_hand: **Miss** - You completely miss... No Damage
        :anger: **Chip** - You barely strike. 30% Damage Reduction
        :bangbang: **Connects** - Your ability strikes. No Reduction
        🗯️ **Hits** - Land a significant Strike. 20% Increase
        💥 **Critical Hit** - You land a lethal blow. 250% Increase
    
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)"""), color=0x7289da)
        
        embedVar17.set_thumbnail(url=avatar)

        embedVar4 = Embed(title=f"Titles & Arms", description=textwrap.dedent(f"""\
        __Titles** & **Arms__
        Modify your or the Opponents **Stats** by applying **Enhancers** during battle.
        
        🎗️ **Title Exlusivity**
        **Titles** apply enhancers at the **start** of your turn or during **Focus State**
        ⚠️ Titles are only effective on cards from the same Universe or Unbound!
        Titles can only be earned via playing through the various game modes
        
        🦾 **Arm Durability**
        Arms are effective across the Multiverse, however they do break! Turning into **Gems**
        ⚠️ Arms from a different universe will break at a faster rate!
        Stock up on **Asrms** and repair **Durability** in the **/blacksmith**
        🪔 Elemental Arms also provide **Essence**. Use **Essence** to craft **Talismans**

        👑 **Universe Buff** :Match Your Titles and Arms to your **Card Universe**.
        **Buff**: **Base Stats** + 100 + (Class Level * 5%) **HLT**, **ATK** & **DEF**.

        ✨ **Destiny Universe Buff** Destiny Cards gain an additional **Buff**.
        **Buff**: **Universe Buff** + 500 + (Card Tier * 5%) **HLT**, **ATK** & **DEF**.
        
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)""") ,color=0x7289da)
        
        embedVar4.set_thumbnail(url=avatar)

        embedVar4_1 = Embed(title=f"Talismans & Summons ", description=textwrap.dedent(f"""\
        📿**Talismans**
        Talismans nullify the affinities of the chosen **Element**. 
        **/attune** and equip /**talismans** from stored **Essence**
        
        🧬 **Summons**
        Can assist during battle with an **Elemental Attack** or **Defensive Boost**.
        Earn **Summons** through Tales, Dungeon and Boss **Drops** or through trade with other Players!
        Battle with your **Summon** to gain **EXP** to increase Summon **Ability Power**. 

        [Join the Anime VS+ Support Server](https://discord.gg/pcn)""") ,color=0x7289da)
        
        embedVar4_1.set_thumbnail(url=avatar)

        embedVar5 = Embed(title=f"Battle Mechanics", description=textwrap.dedent(f"""\
        Players take turns dealing damage using one of their 5 **Abilities**.
        
        🌀 **Stamina** costs are standard across all Cards 
        _See Card Mechanics page for details_.
        
        ⚕️ **Recovery**
        When Players have used all of their **Stamina** they enter **Focus State**.
        Sacrifice 1 turn to Heal and Reduce Stacked Damage Effects

        The Match is over when a players **Health** reaches 0.
        
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)""") ,color=0x7289da)
        
        embedVar5.set_thumbnail(url=avatar)

        embedVar6 = Embed(title=f"Focus, Blitz & Resolve", description=textwrap.dedent(f"""\
        🌀 **Focus**
        Players can take advantage of **Focus State** to ⚕️**Recover**.
        **Focus State** sacrifices a turn to Level Up Stats, increase **Stamina** to 90, and **Recover** some **Health**.
        The amount of Attack and Defense gained is based on your **Fortitude**[Missing Health]
                                                                                        
        💢 **Blitz**
        Players can take advantage of **Blitz** to overwhelm their opponent
        After your first focus you can blitz, sacrifice all your remaining Stamina to Level Up Stats.
        **Blitz** activates when yo have <50 Stamina, it replaces your **Focus State**
        The amount of Attack and Defense gained is based on your **Evasion** stat
                                                                                        
        ⚡**Resolve**
        Once in **Focus State** players can **Resolve**!
        **Resolved Characters** transform to greatly increase attack and health while sacrificing defense.
        **Resolved Characters** can call on Summons to aid them in battle.
        ⚡ Resolve _uses 1 turn_. You no longer stack Focus Stats

        **Summon Assistance!**
        Summons Enhancers either use an Elemental Attack or Grant the player a Defensive Arm. Summon moves do not end the player turn!
        🧬 Summon __activates once per focus after resolve__

        [Join the Anime VS+ Support Server](https://discord.gg/pcn)""") ,color=0x7289da)
        
        embedVar6.set_thumbnail(url=avatar)
        
        embedVar16 = Embed(title=f"Difficulty & Progression", description=textwrap.dedent(f"""\
        ⚙️**Difficulty**
        Anime VS+ allows you to tailor your experience to your desired level.
        
        **3 Difficulties**
        **Easy** *Play the game freely and casually*
        - Lower Enemy Scaling
        - No Destinies, Dungeons, Bosses, Drops, Raids or Abyss
        
        **Normal** *Play Anime VS+ the Intended Way*
        - **/play** to earn levels and items
        - Standard drop rates for items in game modes
        - Rebirth for increase in base stats and drop rates
        
        **Hard** *Not for the faint of Heart*
        - Normal Mode but with increasing scaling, drops and rewards
        - Clout

        [Join the Anime VS+ Support Server](https://discord.gg/pcn)"""),color=0x7289da)
        
        embedVar16.set_thumbnail(url=avatar)

        embedVar7 = Embed(title=f"Game Modes", description=textwrap.dedent(f"""\
        __PVE Game Modes__
        **🆘 The Tutorial** - Learn Anime VS+ battle system
        **⚡ Randomize** - Select and start a Random Game Mode Below
        **🗺️ Adventure** - /Explore through the multiverse in a map-based RPG mode
        **⚔️ Tales** - Normal battle mode to earn cards, accessories and more
        **👺 Dungeon** - Hard battle mode to earn dungeon cards, dungeon accessories, and more
        **📽️ Scenario** - Battle through unique scenarios to earn Cards and Moves
        **💀 Raid** - Battle through High Level scenarios to earn Mythical Cards and Moves
        **🌌 Explore** - Random Encounter battles to earn rare cards and major rewards (Explore Determines your Adventure Universe!)
        
        __PVP Game Modes__
        **/pvp** - Battle a rival in PVP mode
        *More PVP modes coming soon!*
                                                                
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)"""),color=0x7289da)
        
        embedVar7.set_thumbnail(url=avatar)


        embedVar9 = Embed(title=f"Presets",description=textwrap.dedent(f"""\
        Save your favorite builds in your **Preset**
        **/menu** tselect **View Preset** option, select a preset with **1-5**
        Select **Save Preset** to save a new Build!
        
        **Preset Builds**
        You can bring your preset builds into Duo Battles!
                                                                        

        [Join the Anime VS+ Support Server](https://discord.gg/pcn)""") ,color=0x7289da)
        
        embedVar9.set_thumbnail(url=avatar)

        embedVar10 = Embed(title=f"Economy",description=textwrap.dedent(f"""\
        **Marketplace**
        Use **/marketplace** to access the **Market!**!
        Use the marketplace to buy and sell Cards, Arms and Summons!
                                                                        
        **Trading**
        **/trade** will allow you to trade Cards, Arms and Summons with other players.
        Add items to the open trade using the buttons on the item menu *ex. /cards*
        **/tradecoins** allows you to add or remove coins from the trade

        **Dismantle**
        Dismantle Cards, Titles and Arms into :gem:**Gems**. and 🪔**Essense**
        
        **Blacksmith**
        **/blacksmith** to purchase Card Levels, Card Tiers, Arm Durability and **Storage**!

        **Currency**
        🪙 - Coins = Coins can be used to purchase Cards, Titles and Arms from the Marketplace. You can use them to trade and sell items to other players!
        💎 - Gems - When Items break they turn into **Gems**, You can also dismantle items from your inventory into **Gems**! 
        🪔 Essence - Essence can be used to craft Elemental Talismans
        
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)""") ,color=0x7289da)
        
        embedVar10.set_thumbnail(url=avatar)
        
        embedVar15 = Embed(title=f"Guilds", description=textwrap.dedent(f"""\
        **Guilds Explained**
        - Use **/guild** to lookup any Anime VS+ Guild!
        - **Guild Members** earn extra 🪙 towards the **Guild Bank** 

        **Creating A Guild**
        - Use **/createguild** and create a **Guild Name**
        - **/recruit** your friends to join your newly named **Guild** !
        - Players can use **/apply** to join as well!
        
        **Guild Bonusus**
        - Guildmates gain an extra **50 Attack** and **Defense** playing Co-Op Together !
        - Guilds earn additional 🪙 for every **Tales**, **Dungeon** and **Boss** Victory
        
        **Guild Economy**
        - Players across **Anime VS+** can **/donate** 🪙 to their favorite Guilds!
        - Guild Owners can ****/pay**** their members a wage.
        
        **Guild Buffs**
        - Quest Buff: Start Quest from the required fight in the Tale, not for dungeons
        - Level Buff: Each fight will grant you a level up
        - Stat Buff: Add 100 ATK & DEF, 100 AP, and 500 HLT
        - Rift Buff: Rifts will always be available

        Guild Position Explanations
        - Owner: All operations
        - Officer: Can Add members, Delete members, Pay members, Buy, Swap, and Toggle Buffs
        - Captain: Can Toggly Buffs, Pay members
        - Member: No operations
                                                                        
        [Join the Anime VS+ Support Server](https://discord.gg/pcn)"""),color=0x7289da)
        
        embedVar15.set_thumbnail(url=avatar)

        # embedVar12 = Embed(title=f"Families",description=textwrap.dedent(f"""\
        # **Families Explained**
        # - When you create an AnimeVs+ account you start a family
        # - Use **/family** to lookup any Anime VS+ Family!
        
        # **Marriage**
        # - Two players with a strong bond can come together and form a **Family**
        # - Use **/marry** to start a marriage proposal to your chosen **Partner**
        # - If they accept, they will join your dfamily
        # - **2 Kids** can be adopted into the family to create a 4 player Maximum.
        
        # **Family Bonuses**
        # - Family Members gain an extra **100 Health** when playing Co-Op Together !
        # - Family Members earn extra 🪙 towards the **Family Bank**.
        # - Families can **/invest** their income together.
        # - Heads of Household and Partners can pay **/allowance** to Family members. 
        
        # **Housing**
        # - The **Family Bank** can be used to buy **Houses**
        # - **Houses** increase your 🪙 earned via **Mutlipliers**
        # - **/invest** your income to buy bigger **Houses** and earn more 🪙 across the game.
        # - Use the *Real Estate Menu** to buy and sell Estates
        
        # **Family Summon**
        # - Family members can equip the Family Summon to aid them in battle!
        
        # Family Position Explanations
        # - Head of Household: All operations.
        # - Partner: Can equip/update family summon, change equipped house.
        # - Kids: Can equip family summon.
        # """) ,color=0x7289da)
        
        # embedVar12.set_thumbnail(url=avatar)

        # embedVar13 = Embed(title=f"Associations",description=textwrap.dedent(f"""\
        # **Association Explained**
        # - Associations in Anime VS+ are formed by an Oath between two Guild Owners
        # - The Oathgiver becomes the **Founder** and the Oathreciever becomes the ****Sworn and Shield****.
        # - The **Shield** defends the Association from raiding players.
        # - Both teams become enlisted as **Swords** of the new **Association**
        # - Their respective members become **Blades**
        # - The Founder & Sworn may /ally with other Teams increasing the size and power of the Association.
        # - These are the **Owners** and can **/sponsor** other teams allied with the Association.
        # - **Associations** earn money by winning **PvP** matches, Income from **Universe Crest** and defending against **Raids**
        
        # **Universe Crest** 
        # - When a member of a Association defeats a **Dungeon** or **Boss** they earn the **Universe Crest** from that Universe.
        # - This Crest will earn the Association **Passive Income** whenever someone goes into that universe in all servers!
        
        # **Association Bonuses**
        # - Associations earn extra income towards the **Association Bank**
        # - Associations increase the earned income in **PvP**
        # - Associations can Raid
        # - Associations can earn passive income owning **Universe Crest**
        # - Associations can purchase **Halls**
        
        # **Halls**
        # - The **Association Bank** can be used to purchase **Halls**
        # - Increase the Income earned to Associations via **Multipliers**
        # - Increase the income earned to **Blades** via **Splits**
        # - Increase the defense of the **Shield**
        # - Increase the **Bounty** cost to raid the **Association**
        # """) ,color=0x7289da)
        
        # embedVar13.set_thumbnail(url=avatar)
        
        # embedVar14 = Embed(title=f"Raids",description=textwrap.dedent(f"""\
        # **Raids Explained**
        # - Players aligned with a Association can use /raid to claim bounties from other guilds
        # - Victory claims the bounty and resets the Associations victory multiplier !
        # - Income from Raids is limited to the bounty offered from the Association.
        # - To take money from a **Association Bank** players must compete in PvP
        
        # Raiding an Association is no easy feat and must be done **Without Summons**
        
        # **Raid Benefits**
        # - Earn Large Bounties from guilds.
        # - Earn Wins for your Anime VS+ **Guild**
        
        # **Shield  Defense Explained**
        # - The **Shield** has a big repsonsible to defend the **Association** from raids, earning income from **Challengers**.
        # - The **Shield** exist within the Association hall as the **Current Equipped Build** of the **Shield Player**.
        # - As the **Shield**, whenever your Avatar succesfully defends a raid you earn 🪙
        # - With each victory you will build a streak earning both respect and more 🪙 via **Multipliers**.
        
        # **Shield Benefits**
        # - Earn income by defending your Association from raiders
        # - Guild has a 30% reduction in buff cost
        # - Earn respect by increasing the Association victory streak 
        
        # """) ,color=0x7289da)
        
        # embedVar14.set_thumbnail(url=avatar)

        embeds = [embedVar1, embedVar0, embedVar3, embedVar3_s, embedVar3_1, embedVar3_2, embedVar11, embedVar17, embedVar4, embedVar4_1, embedVar5, embedVar6, embedVar16, embedVar7, embedVar9, embedVar10, embedVar15]
        paginator = Paginator.create_from_embeds(self.bot, *embeds)
        paginator.show_select_menu = True
        await paginator.send(ctx)
    except Exception as ex:
        loggy.error(f"Error in animevs command: {ex}")
        await ctx.send("Hmm something ain't right. Check with support.", ephemeral=True)
        return


def setup(bot):
    Help(bot)





