import custom_logging
from cogs.classes.custom_paginator import CustomPaginator
import db
import time
import classes as data
import messages as m
from bson.int64 import Int64
import textwrap
from logger import loggy
import textwrap
import unique_traits as ut
from cogs.quests import Quests
now = time.asctime()
import asyncio
import uuid
from interactions import ActionRow, Button, ButtonStyle, listen, slash_command, Embed, Extension, cooldown, Buckets
import crown_utilities

emojis = ['👍', '👎']

class Register(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        loggy.info('Register cog is ready')
    
    @slash_command(description="Register for Anime VS+", scopes=crown_utilities.guild_ids)
    async def register(self, ctx):
        await ctx.defer()
        server_created = db.queryServer({"GNAME": str(ctx.author.guild)})
        if db.queryUser({"DID": str(ctx.author.id)}):
            await ctx.send(f"{ctx.author.mention} You already have a Anime VS+ Account!")
            return 

        else:
            disname = str(ctx.author)
            did = str(ctx.author.id)
            name = disname.split("#",1)[0]
            is_admin = False
            is_creator = False
            admin_did = ['339423274117103617','306429381948211210','570660973640286211','263564778914578432']
            if did in admin_did:
                is_admin = True
                is_creator = True
            summon_info = {
                "NAME": "Chick",
                "LVL": 1,
                "EXP": 0,
                "Peck": 100,
                "TYPE": "PHYSICAL",
                "BOND": 0,
                "BONDEXP": 0,
                "PATH": "https://res.cloudinary.com/dkcmq8o15/image/upload/v1638814575/Pets/CHICK.png"
            }
            user = {
                'DISNAME': disname, 
                'NAME': name, 
                'DID': did, 
                'AVATAR': str(ctx.author.avatar_url), 
                'SERVER': str(ctx.author.guild), 
                'FAMILY': did,
                'FAMILY_DID': did,
                'BALANCE': Int64(100000),
                'IS_ADMIN': is_admin,
                'CREATOR': is_creator,
            }
            r_response = db.createUsers(data.newUser(user))

            if not server_created:
                create_server_query = {'GNAME': str(ctx.author.guild.name)}
                created_server = db.createServer(data.newServer(create_server_query))
                server_query = {'GNAME': str(ctx.author.guild)}
                update_server_query = {
                    '$inc': {'SERVER_BALANCE': 10000},
                    '$addToSet': {'SERVER_PLAYERS': str(ctx.author.id)}
                }
                updated_server = db.updateServer(server_query, update_server_query)


        if r_response:
            try:
                _uuid = str(uuid.uuid4())
                accept_buttons = [
                    Button(
                        style=ButtonStyle.GREEN,
                        label="Continue",
                        custom_id=f"{_uuid}|yes"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="End Registration Here",
                        custom_id=f"{_uuid}|no"
                    )
                ]

                embed = Embed(title="🆚 Anime VS+ Registration", description="Collect your favorite anime and video game characters, incredible items and unique summons to dominate the multiverse.", color=0x7289da)

                action_row = ActionRow(*accept_buttons)

                message = await ctx.send(embed=embed, components=[action_row])

                def check(component: Button):
                    return str(component.ctx.author.id) == str(ctx.author.id)

                try:
                    button_ctx = await self.bot.wait_for_component(components=[action_row], check=check, timeout=120)
                    # await button_ctx.ctx.defer()

                    if button_ctx.ctx.custom_id == f"{_uuid}|no":
                        embed = Embed(title="Anime VS+ Registration", description="Your registration has been cancelled.", color=0x7289da)
                        await message.edit(components=[], embed=embed)
                        return

                    if button_ctx.ctx.custom_id == f"{_uuid}|yes":
                        await message.edit(components=[], embed=embed)
                        universe_data = db.queryAllUniverse()
                        universe_embed_list = []
                        for uni in universe_data:
                            available = ""
                            if uni['HAS_CROWN_TALES'] == True:
                                traits = ut.formatted_traits
                                mytrait = {}
                                traitmessage = ''
                                o_show = uni['TITLE']
                                universe = o_show
                                for trait in traits:
                                    if trait['NAME'] == o_show:
                                        mytrait = trait
                                    if o_show == 'Pokemon':
                                        if trait['NAME'] == 'Pokemon':
                                            mytrait = trait
                                if mytrait:
                                    traitmessage =f"*{mytrait['EFFECT']}*"
                                available =f"{crown_utilities.crest_dict[uni['TITLE']]}"
                                
                                embedVar = Embed(title=f"{uni['TITLE']}", description=textwrap.dedent(f"""                                                                                         
                                **{available}** Select A Starting Universe!
                                Select a universe to earn *3* 🎴 Cards and 🦾 Arms to begin! 

                                [ℹ️]__Don't overthink it!__
                                *You can always earn cards, arms, titles and more from all universes later!*

                                """))
                                embedVar.add_field(name="♾️ | Unique Universe Trait", value=f"{traitmessage}")
                                embedVar.set_image(url=uni['PATH'])
                                embedVar.set_footer(text="You can earn items in all universes! This is just a starting point!")
                                universe_embed_list.append(embedVar)
                            
                    paginator = CustomPaginator.create_from_embeds(self.bot, *universe_embed_list, custom_buttons=["Register"], paginator_type="Register")
                    paginator.show_select_menu = True
                    await paginator.send(ctx)
                
                except asyncio.TimeoutError:
                    await message.edit(components=[], embed=embed, content="You took too long to respond.")
                    await ctx.send(f"{ctx.author.mention} your Registration was cancelled. You must interact before the timeout!")
                    db.deleteUser({"DID": str(ctx.author.id)})
                    return

            except Exception as ex:
                custom_logging.debug(ex)
                await ctx.send(f"{ctx.author.mention} your Registration was cancelled. You must interact before the timeout!")
                
        else:
            db.deleteUser(str(ctx.author.id))
            await ctx.send(m.RESPONSE_NOT_DETECTED, delete_after=3)


    @slash_command(description="Delete your account")
    async def deleteaccount(self, ctx):
        _uuid = uuid.uuid4()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            await ctx.send("You are not registered. Please register with /register")
        
        player = crown_utilities.create_player_from_data(a_registered_player)
        accept_buttons = [
            Button(
                style=ButtonStyle.GREEN,
                label="Yes",
                custom_id=f"{_uuid}|yes"
            ),
            Button(
                style=ButtonStyle.BLUE,
                label="No",
                custom_id=f"{_uuid}|no"
            )
        ]
        accept_buttons_action_row = ActionRow(*accept_buttons)

        team = db.queryTeam({'TEAM_NAME': player.guild.lower()})

        msg = await ctx.send(f"{ctx.author.mention}, are you sure you want to delete your account?", components=[accept_buttons_action_row])

        def check(component: Button) -> bool:
            return component.ctx.author == ctx.author

        try:
            button_ctx = await self.bot.wait_for_component(components=[accept_buttons_action_row], timeout=300, check=check)

            if button_ctx.ctx.custom_id == f"{_uuid}|no":
                embed = Embed(title="Account Not Deleted", description="Your account has not been deleted.", color=0x00ff00)
                await button_ctx.ctx.send(embed=[embed])
                return

            if button_ctx.ctx.custom_id == f"{_uuid}|yes":
                loggy.info(f"Delete account command executed by {ctx.author}")
                delete_user_resp = db.deleteUser(player.did)
                if player.guild != "PCG":
                    transaction_message = f"{player.did} left the game."
                    team_query = {'TEAM_NAME': player.guild}
                    new_value_query = {
                        '$pull': {
                            'MEMBERS': player.did,
                            'OFFICERS': player.did,
                            'CAPTAINS': player.did,
                        },
                        '$addToSet': {'TRANSACTIONS': transaction_message},
                        '$inc': {'MEMBER_COUNT': -1}
                        }
                    response = db.deleteTeamMember(team_query, new_value_query, str(ctx.author.id))
                market_items = db.queryAllMarketByParam({'ITEM_OWNER': player.did})
                if market_items:
                    for market_item in market_items:
                        db.deleteMarketEntry({"ITEM_OWNER": player.did, "MARKET_CODE": market_item['MARKET_CODE']})
                embed = Embed(title="Account Deleted", description="Your account has been deleted. Thank you for playing!", color=0x00ff00)
                await button_ctx.ctx.send(embed=embed)
        except Exception as ex:
            loggy.critical(ex)
            custom_logging.debud(ex)
            embed = Embed(title="Error", description="Something went wrong. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed)


    @slash_command(name="daily", description="Receive your daily reward and quests", scopes=crown_utilities.guild_ids)
    @cooldown(Buckets.USER, 1, 86400)
    async def daily(self, ctx):
        try:
            await ctx.defer()
            query = {'DID': str(ctx.author.id)}
            user_data = db.queryUser(query)
            player = crown_utilities.create_player_from_data(user_data)

            milestone_message = await Quests.milestone_check(player, "DAILY", 1)

            aicon = crown_utilities.prestige_icon(player.prestige)
            dailyamount = 100000
            daily_bonus = int(dailyamount * (player.rebirth + 1) + (1000000 * player.prestige))
                
            await crown_utilities.bless(daily_bonus, player.did)
            difference = daily_bonus - dailyamount

            
            if ctx.author.guild:
                server_query = {'GNAME': player.did}
                update_server_query = {
                    '$inc': {'SERVER_BALANCE': daily_bonus}
                }
                updated_server = db.updateServer(server_query, update_server_query)
            
            bonus_message =f"❤️‍🔥 | *+🪙{'{:,}'.format(difference)}*" if difference > 0 else ""
            player.quests = db.queryUser({"DID": str(player.did)})["QUESTS"]
            current_quests = player.quests

            # Update quests with QUEST_FLAG as true
            for quest in crown_utilities.quest_list:
                if quest['QUEST_FLAG']:
                    matching_quest = next((q for q in current_quests if q['TYPE'] == quest['TYPE']), None)
                    if matching_quest:
                        matching_quest['AMOUNT'] = 0
                        matching_quest['COMPLETED'] = False
                    else:
                        current_quests.append(quest)

            # Prepare the update data
            update_data = {
                'QUESTS': current_quests,
                'BOSS_FOUGHT': False,
                'VOTED': False
            }

            # Update the user's quests in the database
            await asyncio.to_thread(db.updateUserNoFilter, query, {'$set': update_data})

            # Determine the retry message and update RETRIES accordingly
            retry_message = f"🆚 | Rematches : {player.retries}"
            if player.retries >= 25:
                await asyncio.to_thread(db.updateUserNoFilter, query, {'$set': {'RETRIES': 25}})
            else:
                await asyncio.to_thread(db.updateUserNoFilter, query, {'$inc': {'RETRIES': 2}})
                retry_message = f"🆚 | Rematches : {player.retries} **+ 2**"

            quest_messages = []
            for quest in crown_utilities.quest_list:
                quest_messages.append(f"🆕 {quest['NAME']} 💎 {quest['REWARD']:,}")

            embedVar = Embed(title=f"☀️ Daily Rewards!", description=textwrap.dedent(f"""\
            Welcome back, {ctx.author.mention}!
            {retry_message}
            🪙 | +{'{:,}'.format(daily_bonus)}
            """), color=0xf1c40f)

            if milestone_message:
                # milestone message is a list of strings
                embedVar.add_field(name="🏆 **Milestone**", value="\n".join(milestone_message), inline=False
                                    )
            embedVar.add_field(name="📜 **New Quests** */quest*", value="\n".join(quest_messages), inline=False)
            embedVar.add_field(name="Vote for Anime VS+!", value="🗳️ | **/vote** to earn daily rewards!", inline=False)
            embedVar.add_field(name="Patch Notes", value="📜 | Fixed the issue where you aren't able to add items to the marketplace or trade. Enjoy!\n**Codes for special unlocks coming soon!**", inline=False)
            embedVar.set_footer(text=f"☀️ | You can vote twice a Day with /daily!")
            await ctx.send(embed=embedVar)
        except Exception as ex:
            custom_logging.debug(ex)
            return
    

def setup(bot):
    Register(bot)