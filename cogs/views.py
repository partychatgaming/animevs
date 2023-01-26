import textwrap
import discord
import crown_utilities
from discord.ext import commands
import bot as main
import db
import classes as data
import messages as m
import numpy as np
import help_commands as h
import unique_traits as ut
import destiny as d
# Converters
from discord import User
from discord import Member
from PIL import Image, ImageFont, ImageDraw
import requests
import random
from .classes.card_class import Card
from .classes.title_class import Title
from .crownunlimited import showcard, showsummon, cardback, enhancer_mapping, enhancer_suffix_mapping, passive_enhancer_suffix_mapping, title_enhancer_suffix_mapping, title_enhancer_mapping
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash import cog_ext, SlashContext
from discord_slash import SlashCommand
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from dinteractions_Paginator import Paginator



class Views(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Views Cog is ready!')

    async def cog_check(self, ctx):
        return await main.validate_user(ctx)

    @cog_ext.cog_slash(description="Equip a Card", guild_ids=main.guild_ids)
    async def equipcard(self, ctx, card: str):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        card_name = card
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)

        vault_query = {'DID': str(ctx.author.id)}
        vault = db.altQueryVault(vault_query)

        resp = db.queryCard({'NAME': {"$regex": f"^{str(card)}$", "$options": "i"}})

        card_name = resp["NAME"]
        # Do not Check Tourney wins
        if card_name in vault['CARDS']:
            response = db.updateUserNoFilter(user_query, {'$set': {'CARD': str(card_name)}})
            await ctx.send(f"**{card_name}** has been equipped.")
        else:
            await ctx.send(m.USER_DOESNT_HAVE_THE_CARD, hidden=True)


    @cog_ext.cog_slash(description="Select an operation from the menu!",
                    options=[
                        create_option(
                            name="name",
                            description="name of card, title, arm, summons, universe, hall, or house you want to view",
                            option_type=3,
                            required=True
                        ),
                        create_option(
                            name="selection",
                            description="Select an option!",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(
                                    name="🎴 It's a Card",
                                    value="cards",
                                ),
                                create_choice(
                                    name="🎗️ It's a Title",
                                    value="titles",
                                ),
                                create_choice(
                                    name="🦾 It's an Arm",
                                    value="arms",
                                ),
                                create_choice(
                                    name="🧬 It's a Summon",
                                    value="summons",
                                ),
                                create_choice(
                                    name="🌍 It's a Universe",
                                    value="universe",
                                ),
                                create_choice(
                                    name="👹 It's a Boss",
                                    value="boss",
                                ),
                                create_choice(
                                    name="🎏 It's a Hall",
                                    value="hall",
                                ),
                                create_choice(
                                    name="🏠 It's a House",
                                    value="house",
                                ),
                            ]
                        )
                    ], guild_ids=main.guild_ids)
    async def view(self, ctx, selection, name):
        if selection == "cards":
            await viewcard(self, ctx, name)
        if selection == "titles":
            await viewtitle(self, ctx, name)
        if selection == "arms":
            await viewarm(self, ctx, name)
        if selection == "summons":
            await viewsummon(self, ctx, name)
        if selection == "universe":
            await viewuniverse(self, ctx, name)
        if selection == "boss":
            await viewboss(self, ctx, name)
        if selection == "hall":
            await viewhall(self, ctx, name)
        if selection == "house":
            await viewhouse(self, ctx, name)


def setup(bot):
    bot.add_cog(Views(bot))



async def viewcard(self, ctx, card: str):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    card_name = card
    query = {'DID': str(ctx.author.id)}
    d = db.queryUser(query)
    card = db.queryCard({'NAME': {"$regex": f"^{str(card_name)}$", "$options": "i"}})
    try:
        if card:
            c = Card(card['NAME'], card['PATH'], card['PRICE'], card['EXCLUSIVE'], card['AVAILABLE'], card['IS_SKIN'], card['SKIN_FOR'], card['HLT'], card['HLT'], card['STAM'], card['STAM'], card['MOVESET'], card['ATK'], card['DEF'], card['TYPE'], card['PASS'][0], card['SPD'], card['UNIVERSE'], card['HAS_COLLECTION'], card['TIER'], card['COLLECTION'], card['WEAKNESS'], card['RESISTANT'], card['REPEL'], card['ABSORB'], card['IMMUNE'], card['GIF'], card['FPATH'], card['RNAME'])
            title = {'TITLE': 'CARD PREVIEW'}
            arm = {'ARM': 'CARD PREVIEW'}

            if c.is_universe_unbound():
                await ctx.send("You cannot view this card at this time. ", hidden=True)
                return
            c.set_price_message_and_card_icon()
            c.set_tip_and_view_card_message()
            att = 0
            defe = 0
            turn = 0

            active_pet = {}
            pet_ability_power = 0
            card_exp = 150

            
            if d['PERFORMANCE']:
                embedVar = discord.Embed(title=f"{c.card_icon} {c.price_message} {c.name}", description=textwrap.dedent(f"""\
                :mahjong: {c.tier}
                ❤️ {c.max_health}
                🗡️ {c.attack}
                🛡️ {c.defense}
                🏃 {c.speed}

                🩸 {c.passive_name}: {c.passive_type} {c.passive_num}{passive_enhancer_suffix_mapping[c.passive_type]}                

                {c.move1_emoji} {c.move1}: {c.move1ap}
                {c.move2_emoji} {c.move2}: {c.move2ap}
                {c.move3_emoji} {c.move3}: {c.move3ap}
                🦠 {c.move4}: {c.move4enh} {c.move4ap} {passive_enhancer_suffix_mapping[c.move4enh]}   

                ♾️ {c.set_trait_message()}
                """), colour=000000)
                embedVar.add_field(name="__Affinities__", value=f"{c.affinity_message}")
                embedVar.set_footer(text=f"{c.tip}")
                await ctx.send(embed=embedVar)

            else:
                card_file = showcard("non-battle", card, "none", c.max_health, c.health, c.max_stamina, c.stamina, c.resolved, title, c.focused,
                                    c.attack, c.defense, c.turn, c.move1ap, c.move2ap, c.move3ap, c.move4ap, c.move4enh, 0, None)

                embedVar = discord.Embed(title=f"", colour=000000)
                embedVar.add_field(name="__Affinities__", value=f"{c.set_affinity_message()}")
                embedVar.set_image(url="attachment://image.png")
                embedVar.set_thumbnail(url=c.set_universe_image())
                embedVar.set_author(name=textwrap.dedent(f"""\
                {c.card_icon} {c.price_message}
                Passive & Universe Trait
                🩸 {c.passive_name}: {c.passive_type} {c.passive_num}{passive_enhancer_suffix_mapping[c.passive_type]}
                ♾️ {c.set_trait_message()}
                🏃 {c.speed}
                """))
                embedVar.set_footer(text=f"{c.tip}")

                await ctx.send(file=card_file, embed=embedVar)
        else:
            await ctx.send(m.CARD_DOESNT_EXIST, hidden=True)
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


async def viewtitle(self, ctx, title: str):
    try:
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        title_name = title
        title = db.queryTitle({'TITLE': {"$regex": f"^{str(title)}$", "$options": "i"}})
        if title:
            t = Title(title['TITLE'], title['UNIVERSE'], title['PRICE'], title['EXCLUSIVE'], title['AVAILABLE'], title['ABILITIES'])            
            t.set_type_message_and_price_message()

            embedVar = discord.Embed(title=f"{crown_utilities.crest_dict[t.universe]} {t.name}\n{t.price_message}".format(self), colour=000000)
            if t.universe != "Unbound":
                embedVar.set_thumbnail(url=t.title_img)
            embedVar.add_field(name=f"**Unique Passive**", value=f"{t.set_title_embed_message()}", inline=False)
            embedVar.set_footer(text=f"{t.passive_type}: {title_enhancer_mapping[t.passive_type]}")
            await ctx.send(embed=embedVar)

        else:
            await ctx.send("That title doesn't exist.", hidden=True)
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

async def viewarm(self, ctx, arm: str):
    arm_name = arm
    arm = db.queryArm({'ARM': {"$regex": f"^{str(arm_name)}$", "$options": "i"}})
    try:
        if arm:
            element_available = ['BASIC', 'SPECIAL', 'ULTIMATE']
            arm_arm = arm['ARM']
            arm_show = arm['UNIVERSE']
            arm_price = arm['PRICE']
            exclusive = arm['EXCLUSIVE']
            element = arm['ELEMENT']
            if element:
                element_name = element.title()
                element = crown_utilities.set_emoji(element)

            if arm_show != 'Unbound':
                arm_show_img = db.queryUniverse({'TITLE': arm_show})['PATH']
            arm_passive = arm['ABILITIES'][0]
                # Arm Passive
            o_arm_passive_type = list(arm_passive.keys())[0]
            o_arm_passive_value = list(arm_passive.values())[0]

            message=""
            
            price_message ="" 
            if exclusive:
                price_message = "_Priceless_"
            else:
                price_message = f"_Shop & Drop_"

            if o_arm_passive_type == 'BASIC':
                typetext = 'Basic'
                message=f"{arm_arm} is a basic attack arm"
            elif o_arm_passive_type == 'SPECIAL':
                typetext = 'Special'
                message=f"{arm_arm} is a special attack arm"
            elif o_arm_passive_type == 'ULTIMATE':
                typetext = 'Ultimate'
                message=f"{arm_arm} is an ultimate attack arm"
            elif o_arm_passive_type == 'ULTIMAX':
                typetext = 'Ultimax'
                message=f"{arm_arm} is a ULTIMAX arm"
            elif o_arm_passive_type == 'SHIELD':
                typetext = 'Shield'
                message=f"{arm_arm} is a SHIELD arm"
            elif o_arm_passive_type == 'BARRIER':
                typetext = 'Barrier'
                message=f"{arm_arm} is an BARRIER arm"
            elif o_arm_passive_type == 'PARRY':
                typetext = 'Parry'
                message=f"{arm_arm} is a PARRY arm"
            elif o_arm_passive_type == 'MANA':
                typetext = 'Mana'
                message=f"{arm_arm} is a MANA arm"
            elif o_arm_passive_type == 'SIPHON':
                typetext = 'Siphon'
                message=f"{arm_arm} is a SIPHON arm"




            embedVar = discord.Embed(title=f"{crown_utilities.crest_dict[arm_show]} {arm_arm}\n{price_message}".format(self), colour=000000)
            if arm_show != "Unbound":
                embedVar.set_thumbnail(url=arm_show_img)
            if o_arm_passive_type in element_available:
                # embedVar.add_field(name=f"Arm Move Element", value=f"{element}", inline=False)
                embedVar.add_field(name=f"{typetext} {element_name} Attack", value=f"{element} **{arm_arm}**: **{o_arm_passive_value}**", inline=False)
                embedVar.set_footer(text=f"The new {typetext} attack will reflect on your card when equipped")

            else:
                embedVar.add_field(name=f"Unique Passive", value=f"Increases {typetext} by **{o_arm_passive_value}**", inline=False)
                embedVar.set_footer(text=f"{o_arm_passive_type}: {enhancer_mapping[o_arm_passive_type]}")

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


async def viewsummon(self, ctx, summon: str):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    pet = db.queryPet({'PET': {"$regex": f"^{str(summon)}$", "$options": "i"}})
    try:
        if pet:
            pet_pet = pet['PET']
            pet_show = pet['UNIVERSE']
            pet_image = pet['PATH']

            if pet_show != 'Unbound':
                pet_show_img = db.queryUniverse({'TITLE': pet_show})['PATH']
            pet_passive = pet['ABILITIES'][0]
                # Summon Passive
            o_pet_passive_name = list(pet_passive.keys())[0]
            o_pet_passive_value = list(pet_passive.values())[0]
            o_pet_passive_type = list(pet_passive.values())[1]

            message=""
            
            if o_pet_passive_type == 'ATK':
                typetext = "Attack"
                message=f"{pet_pet} is a ATK Summon"
                value=f"{o_pet_passive_name}: Increase {typetext} by {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]}"
            elif o_pet_passive_type == 'DEF':
                typetext = "Defense"
                mmessage=f"{pet_pet} is a DEF Summon"
                value=f"{o_pet_passive_name}: Increase {typetext} by {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]}"
            elif o_pet_passive_type == 'STAM':
                typetext = "Stamina"
                message=f"{pet_pet} is a STAM Summon"
                value=f"{o_pet_passive_name}: Increase {typetext} by {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]}"
            elif o_pet_passive_type == 'HLT':
                typetext = "Health"
                message=f"{pet_pet} is a HLT Summon"
                value=f"{o_pet_passive_name}: Increase {typetext} by {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]}"
            elif o_pet_passive_type == 'LIFE':
                typetext = "of Opponents Health"
                message=f"{pet_pet} is a LIFE Summon"
                value=f"{o_pet_passive_name}: Steals {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} {typetext}"
            elif o_pet_passive_type == 'DRAIN':
                typetext = "of Opponents Stamina"
                message=f"{pet_pet} is a DRAIN Summon"
                value=f"{o_pet_passive_name}: Steals {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} {typetext}"
            elif o_pet_passive_type == 'FLOG':
                typetext = "of Opponents Attack"
                message=f"{pet_pet} is a FLOG Summon"
                value=f"{o_pet_passive_name}: Steals {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} {typetext}"
            elif o_pet_passive_type == 'WITHER':
                typetext = "of Opponents Defense"
                message=f"{pet_pet} is a WITHER Summon"
                value=f"{o_pet_passive_name}: Steals {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} {typetext}"
            elif o_pet_passive_type == 'RAGE':
                typetext = f"Defense to gain {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} AP"
                message=f"{pet_pet} is a RAGE Summon"
                value=f"{o_pet_passive_name}: Sacrifice {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} {typetext}"
            elif o_pet_passive_type == 'BRACE':    
                typetext = f"Attack to gain {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} AP"        
                message=f"{pet_pet} is a BRACE Summon"
                value=f"{o_pet_passive_name}: Sacrifice {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} {typetext}"
            elif o_pet_passive_type == 'BZRK':    
                typetext = f"Health to gain {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} Attack"        
                message=f"{pet_pet} is a BZRK Summon"
                value=f"{o_pet_passive_name}: Sacrifice {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} {typetext}"
            elif o_pet_passive_type == 'CRYSTAL':    
                typetext = f"Health to gain {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} Defense"        
                message=f"{pet_pet} is a CRYSTAL Summon"
                value=f"{o_pet_passive_name}: Sacrifice {o_pet_passive_value}{enhancer_suffix_mapping[o_pet_passive_type]} {typetext}"
            elif o_pet_passive_type == 'GROWTH':    
                typetext = f"Max Health to gain {round(o_pet_passive_value * .5)}{enhancer_suffix_mapping[o_pet_passive_type]} Attack, Defense, and AP"      
                message=f"{pet_pet} is a GROWTH Summon"
                value=f"{o_pet_passive_name}: Sacrifice 10% {typetext}"
            elif o_pet_passive_type == 'STANCE':
                typetext = "Attack and Defense, Increase"
                message=f"{pet_pet} is a STANCE Summon"
                value=f"{o_pet_passive_name}: Swap {typetext} Defense by {o_pet_passive_value}"
            elif o_pet_passive_type == 'CONFUSE':
                typetext = "Opponent Attack And Defense, Decrease Opponent"
                message=f"{pet_pet} is a CONFUSE Summon"
                value=f"{o_pet_passive_name}: Swap {typetext} Defense by {o_pet_passive_value}"
            elif o_pet_passive_type == 'BLINK':
                typetext = "Decrease Your Stamina, Increase Opponent Stamina"
                message=f"{pet_pet} is a BLINK Summon"
                value=f"{o_pet_passive_name}: {typetext} by {o_pet_passive_value}"
            elif o_pet_passive_type == 'SLOW':
                typetext = "Decrease Your Stamina by"
                message=f"{pet_pet} is a SLOW Summon"
                value=f"{o_pet_passive_name}: {typetext} by {o_pet_passive_value}, Swap Stamina with Opponent"
            elif o_pet_passive_type == 'HASTE':
                typetext = "Increase Opponent Stamina by"
                message=f"{pet_pet} is a HASTE Summon"
                value=f"{o_pet_passive_name}: {typetext} by {o_pet_passive_value}, Swap Stamina with Opponent"
            elif o_pet_passive_type == 'SOULCHAIN':
                typetext = "Stamina"
                message=f"{pet_pet} is a SOULCHAIN Summon"
                value=f"{o_pet_passive_name}: Set both players {typetext} equal to {o_pet_passive_value}"
            elif o_pet_passive_type == 'FEAR':
                typetext = f"Max Health to reduce {round(o_pet_passive_value * .5)}{enhancer_suffix_mapping[o_pet_passive_type]} Opponent Attack, Defense, and AP"
                message=f"{pet_pet} is a FEAR Summon"
                value=f"{o_pet_passive_name}: Sacrifice 10% {typetext}"
            elif o_pet_passive_type == 'GAMBLE':
                typetext = "Health"
                message=f"{pet_pet} is a GAMBLE Summon"
                value=f"{o_pet_passive_name}: Set both players {typetext} equal to {o_pet_passive_value}"
            elif o_pet_passive_type == 'BLAST':
                typetext = "Deals Increasing AP * Turn Count Damage "
                message=f"{pet_pet} is a BLAST Summon"
                value=f"{o_pet_passive_name}: {typetext} starting at {o_pet_passive_value}"
            elif o_pet_passive_type == 'WAVE':
                typetext = "Deals Decreasing AP / Turn Count Damage"
                message=f"{pet_pet} is a WAVE Summon"
                value=f"{o_pet_passive_name}: {typetext} starting at {o_pet_passive_value}"
            elif o_pet_passive_type == 'DESTRUCTION':
                typetext = "Destroys Increasing AP * Turn Count Max Health"
                message=f"{pet_pet} is a DESTRUCTION Summon"
                value=f"{o_pet_passive_name}: {typetext} starting at {o_pet_passive_value}"
            elif o_pet_passive_type == 'CREATION':
                typetext = "Grants Decreasing AP / Turn Count Max Health"
                message=f"{pet_pet} is a CREATION Summon"
                value=f"{o_pet_passive_name}: {typetext} starting at {o_pet_passive_value}"

            explanation = f"{o_pet_passive_type}: {enhancer_mapping[o_pet_passive_type]}"  


            summon_file = showsummon(pet_image, pet_pet, value, 0, 0)
            embedVar = discord.Embed(title=f"Summon".format(self), colour=000000)
            if pet_show != "Unbound":
                embedVar.set_thumbnail(url=pet_show_img)
                        
            embedVar.set_image(url="attachment://pet.png")

            await ctx.send(file=summon_file, hidden=True)

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


async def viewuniverse(self, ctx, universe: str):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    try:
        universe_name = universe
        universe = db.queryUniverse({'TITLE': {"$regex": f"^{universe_name}$", "$options": "i"}})
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
                traitmessage = f"**{mytrait['EFFECT']}**: {mytrait['TRAIT']}"
                

            embedVar = discord.Embed(title=f":earth_africa: | {universe_title} :crossed_swords: {fights} :fire: {dungeon_fights} ", description=textwrap.dedent(f"""
            {crest} | **{ownermessage}**
            
            🗒️ | **Details**
            :crown: | **Tales Build** 
            :reminder_ribbon: | **Title** - {ttitle}
            :mechanical_arm: | **Arm** - {tarm}
            🧬 | **Universe Summon ** - {upet}
            
            :fire: | **Dungeon Build**
            :reminder_ribbon: | **Title** - {dtitle}
            :mechanical_arm: | **Arm** - {darm}
            🧬 | **Dungeon Summon ** - {dpet}
            
            :japanese_ogre: | **Universe Boss**
            :flower_playing_cards: | **Card** - {boss}
            {bossmessage}
            :infinity: | **Universe Trait** - {traitmessage}
            """), colour=000000)
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


async def viewhouse(self, ctx, house: str):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    house = db.queryHouse({'HOUSE': {"$regex": f"^{str(house)}$", "$options": "i"}})
    if house:
        house_house = house['HOUSE']
        house_price = house['PRICE']
        house_img = house['PATH']
        house_multiplier = house['MULT']

        message=""
        
        price_message ="" 
        price_message = f":coin: {'{:,}'.format(house_price)}"


        embedVar = discord.Embed(title=f"{house_house}\n{price_message}".format(self), colour=000000)
        embedVar.set_image(url=house_img)
        embedVar.add_field(name="Income Multiplier", value=f"Family earns **{house_multiplier}x** :coin: per match!", inline=False)
        embedVar.set_footer(text=f"/houses - House Menu")

        await ctx.send(embed=embedVar)

    else:
        await ctx.send(m.HOUSE_DOESNT_EXIST, delete_after=3)


async def viewhall(self, ctx, hall: str):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    hall = db.queryHall({'HALL':{"$regex": f"^{str(hall)}$", "$options": "i"}})
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
        price_message = f":coin: {'{:,}'.format(hall_price)}"


        embedVar = discord.Embed(title=f"{hall_hall}\n{price_message}", colour=000000)
        embedVar.set_image(url=hall_img)
        embedVar.add_field(name="Bounty Fee", value=f"**{'{:,}'.format(hall_fee)}** :yen: per **Raid**!", inline=False)
        embedVar.add_field(name="Multiplier", value=f"Association earns **{hall_multiplier}x** :coin: per match!", inline=False)
        embedVar.add_field(name="Split", value=f"**Guilds** earn **{hall_split}x** :coin: per match!", inline=False)
        embedVar.add_field(name="Defenses", value=f"**Shield** Defense Boost: **{hall_def}x**", inline=False)
        embedVar.set_footer(text=f"/halls - Hall Menu")

        await ctx.send(embed=embedVar)

    else:
        await ctx.send(m.HALL_DOESNT_EXIST, delete_after=3)


async def viewboss(self, ctx, boss : str):
    try:
        uboss_name = boss
        uboss = db.queryBoss({'NAME': {"$regex": str(uboss_name), "$options": "i"}})
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
            
            pet = db.queryPet({'PET': uboss_pet})
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
                traitmessage = f"**{mytrait['EFFECT']}**: {mytrait['TRAIT']}"
            
            embedVar = discord.Embed(title=f":japanese_ogre: | {uboss_name}\n:earth_africa: | {uboss_show} Boss", description=textwrap.dedent(f"""
            *{message}*
            
            :flower_playing_cards: | **Card** - {uboss_card}
            :reminder_ribbon: | **Title** - {uboss_title}: **{title_passive_type}** - {title_passive_value}
            :mechanical_arm: | **Arm** - {uboss_arm}: **{arm_passive_type}** - {arm_passive_value}
            :dna: | **Summon** - {uboss_pet}: **{pet_ability_type}**: {pet_ability_value}
            
            :infinity: | **Universe Trait** - {traitmessage}
            """), colour=000000)
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


enhancer_mapping = {'ATK': 'Increase Attack %',
'DEF': 'Increase Defense %',
'STAM': 'Increase Stamina',
'HLT': 'Heal yourself or companion',
'LIFE': 'Steal Health from Opponent',
'DRAIN': 'Drain Stamina from Opponent',
'FLOG': 'Steal Attack from Opponent',
'WITHER': 'Steal Defense from Opponent',
'RAGE': 'Lose Defense, Increase Attack',
'BRACE': 'Lose Attack, Increase Defense',
'BZRK': 'Lose Health, Increase Attack',
'CRYSTAL': 'Lose Health, Increase Defense',
'GROWTH': 'Lose Health, Increase Attack & Defense',
'STANCE': 'Swap your Attack & Defense, Increase Attack',
'CONFUSE': 'Swap Opponent Attack & Defense, Decrease Opponent Defense',
'BLINK': 'Decrease your  Stamina, Increase Target Stamina',
'SLOW': 'Decrease Opponent Stamina, Swap Stamina with Opponent',
'HASTE': ' Increase your Stamina, Swap Stamina with Opponent',
'FEAR': 'Decrease your Health, Decrease Opponent Attack and Defense',
'SOULCHAIN': 'You and Your Opponent Stamina Link',
'GAMBLE': 'You and Your Opponent Health Link',
'WAVE': 'Deal Damage, Decreases over time',
'CREATION': 'Heals you, Decreases over time',
'BLAST': 'Deals Damage, Increases over time',
'DESTRUCTION': 'Decreases Opponent Max Health, Increases over time',
'BASIC': 'Increase Basic Attack AP',
'SPECIAL': 'Increase Special Attack AP',
'ULTIMATE': 'Increase Ultimate Attack AP',
'ULTIMAX': 'Increase All AP Values',
'MANA': 'Increase Enchancer AP',
'SHIELD': 'Blocks Incoming DMG, until broken',
'BARRIER': 'Nullifies Incoming Attacks, until broken',
'PARRY': 'Returns 25% Damage, until broken',
'SIPHON': 'Heal for 10% DMG inflicted + AP'
}


enhancer_suffix_mapping = {'ATK': '%',
'DEF': '%',
'STAM': ' Flat',
'HLT': '%',
'LIFE': '%',
'DRAIN': ' Flat',
'FLOG': '%',
'WITHER': '%',
'RAGE': '%',
'BRACE': '%',
'BZRK': '%',
'CRYSTAL': '%',
'GROWTH': '%',
'STANCE': ' Flat',
'CONFUSE': ' Flat',
'BLINK': ' Flat',
'SLOW': ' Flat',
'HASTE': ' Flat',
'FEAR': '%',
'SOULCHAIN': ' Flat',
'GAMBLE': ' Flat',
'WAVE': ' Flat',
'CREATION': ' Flat',
'BLAST': ' Flat',
'DESTRUCTION': ' Flat',
'BASIC': ' Flat',
'SPECIAL': ' Flat',
'ULTIMATE': ' Flat',
'ULTIMAX': ' Flat',
'MANA': ' %',
'SHIELD': ' DMG 🌐',
'BARRIER': ' Blocks 💠',
'PARRY': ' Counters 🔄',
'SIPHON': ' Healing 💉'
}

