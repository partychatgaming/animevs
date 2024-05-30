import crown_utilities
import custom_logging
import db
import messages as m
from interactions import User
import asyncio
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

class Quests(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Quests Cog is ready!')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)


    @slash_command(name="quests", description="View your current quests")
    async def questboard(self, ctx):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return
        try:
            player = crown_utilities.create_player_from_data(registered_player)
            quest_messages = []
            if player.quests:
                for quest in player.quests:
                    completed = "🟢" if quest["COMPLETED"] else "🔴"
                    quest_messages.append(f"{quest['NAME']} {quest['AMOUNT']}/{quest['COMPLETE']} - {completed}")
                embedVar = Embed(title=f"📜 Quest Board", description="\n".join(quest_messages), color=0x00ff00)
            else:
                embedVar = Embed(title="📜 Quest Board", description="You have no quests at this time", color=0x00ff00)
            await ctx.send(embed=embedVar)
        except Exception as ex:
            custom_logging.print_exception(ex)
            embed = Embed(title="Error", description="There was an error getting your quests", color=0xff0000)
            await ctx.send(embed=embed)

    
    async def quest_check(player, quest_type):
        player_data = db.queryUser({"DID": str(player.did)})
        quest_list = []
        if player_data:
            player = crown_utilities.create_player_from_data(player_data)
            quest_list = player.quests

        for quest in quest_list:
            if quest["TYPE"] == quest_type:
                amount_completed = quest["AMOUNT"]
                amount_required = quest["COMPLETE"]
                if (amount_completed + 1) == amount_required:
                    print("Quest Completed")
                    quest["COMPLETED"] = True
                    update_query = {'$inc': {'QUESTS.$[type].' + 'AMOUNT': 1}, 
                                    '$set': {'QUESTS.$[type].COMPLETED': True}}
                    filter_query = [{'type.' + 'TYPE': quest["TYPE"]}]
                    bless = await crown_utilities.bless(quest['REWARD'], str(player.did))
                    response = db.updateUser({"DID": str(player.did)}, update_query, filter_query)
                    return f"Congratulations! You have completed your {quest['NAME'].title()} quest and have received 💎 {int(quest['REWARD']):,} as a reward"
                else:
                    print("Quest Updated")
                    update_query = {'$inc': {'QUESTS.$[type].' + 'AMOUNT': 1}}
                    filter_query = [{'type.' + 'TYPE': quest["TYPE"]}]
                    response = db.updateUser({"DID": str(player.did)}, update_query, filter_query)
                    return ""
        return ""


    async def milestone_check(player, milestone_type, amount=None, universe_title=None):
        # Misc Milestone Types
        # TRADE
        # MARKETPLACE
        # CARDS_OWNED
        # TITLES_OWNED
        # ARMS_OWNED
        # TALISMANS_OWNED
        # SUMMONS_OWNED
        # TUTORIAL
        # BLACKSMITH
        # ROLL
        # DAILY
        # DONATION

        universe_milestones = []
        message = []

        # This is a check for milestones in the players QUESTS array
        # This will check for misc milestones and universe milestones
        initiated_milestones = await initiate_milestone_checks(player, universe_title)

        player.quests = db.queryUser({"DID": str(player.did)})["QUESTS"]
        # This is a check for misc milestones, if universe_title is None
        await asyncio.sleep(1)
        if not universe_title:
            for quest in player.quests:
                if "MISC_MILESTONES" in quest:
                    for milestone in quest["MISC_MILESTONES"]:
                        if milestone["TYPE"] == milestone_type and not milestone["COMPLETED"]:
                            amount_completed = milestone["AMOUNT"]
                            amount_required = milestone["COMPLETE"]
                            
                            if (amount_completed + amount) >= amount_required:
                                milestone["COMPLETED"] = True
                                # Increment the amount of the milestone for all that matches TYPE
                                update_query = {
                                    '$inc': {'QUESTS.$[quest].MISC_MILESTONES.$[milestone].' + 'AMOUNT': amount},
                                }
                                filter_query = [
                                    {'quest.MISC_MILESTONES': {'$exists': True}},
                                    {'milestone.TYPE': milestone["TYPE"]}                                
                                ]
                                response = await asyncio.to_thread(db.updateUser,{"DID": str(player.did)}, update_query, filter_query)
                                
                                # Only complete the milestone if the NAME is the same
                                update_query = {
                                    '$set': {'QUESTS.$[quest].MISC_MILESTONES.$[milestone].COMPLETED': True}
                                }
                                filter_query = [
                                    {'quest.MISC_MILESTONES': {'$exists': True}},
                                    {'milestone.NAME': milestone["NAME"]}                                
                                ]
                                bless = await crown_utilities.bless(milestone['REWARD'], str(player.did))
                                response = await asyncio.to_thread(db.updateUser,{"DID": str(player.did)}, update_query, filter_query) 
                                
                                
                                message.append(f"Congratulations! You have completed your {milestone['NAME'].title()} milestone and have received 🪙 {int(milestone['REWARD']):,} as a reward")
                            else:
                                update_query = {
                                    '$inc': {'QUESTS.$[quest].MISC_MILESTONES.$[milestone].' + 'AMOUNT': amount}
                                }
                                filter_query = [
                                    {'quest.MISC_MILESTONES': {'$exists': True}},
                                    {'milestone.TYPE': milestone["TYPE"]}
                                ]
                                response = await asyncio.to_thread(db.updateUser,{"DID": str(player.did)}, update_query, filter_query)
            return message
        else:
            for universe in player.quests["UNIVERSES"]:
                if universe["UNIVERSE"] == universe_title:
                    universe_milestones = universe["MILESTONES"]
                    break


            # This is a check for the damage milestones
            for milestone in universe_milestones:
                if milestone["TYPE"] == milestone_type and not milestone["COMPLETED"]:
                    amount_completed = milestone["AMOUNT"]
                    amount_required = milestone["COMPLETE"]
                    if (amount_completed + amount) >= amount_required:
                        print("Milestone Completed")
                        milestone["COMPLETED"] = True
                        update_query = {'$inc': {'QUESTS.UNIVERSES.$[type].' + 'AMOUNT': amount}, 
                                        '$set': {'QUESTS.UNIVERSES.$[type].COMPLETED': True}}
                        filter_query = [{'type.' + 'TYPE': milestone["TYPE"]}]
                        bless = await crown_utilities.bless(milestone['REWARD'], str(player.did))
                        response = db.updateUser({"DID": str(player.did)}, update_query, filter_query)
                        message.append(f"Congratulations! You have completed your {milestone['NAME'].title()} milestone and have received 🪙 {int(milestone['REWARD']):,} as a reward")
                    else:
                        print("Milestone Updated")
                        update_query = {'$inc': {'QUESTS.UNIVERSES.$[type].' + 'AMOUNT': amount}}
                        filter_query = [{'type.' + 'TYPE': milestone["TYPE"]}]
                        response = db.updateUser({"DID": str(player.did)}, update_query, filter_query)
            return message


async def initiate_milestone_checks(player_class, universe_title=None): 
    await milestones_exist_check(player_class)
    
    # If a universe title is provided, check if the universe exists in the player's quests
    # If it doesn't, add the universe to the player's milestones in the UNIVERSES array
    if universe_title:
        universe_exists = milestone_universe_exist(player_class, universe_title)

        if not universe_exists:
            message = f"Welcome to {crown_utilities.crest_dict[universe_title]} {universe_title}! You will now start earning milestone awards in this universe as you battle in game modes in this universe."

            # Initialize universe insertion with empty milestones list
            universe_insertion = {
                "UNIVERSE": universe_title,
                "MILESTONES": []
            }

            # Define the damage check milestones
            damage_check = [
                (1000, 10000), (5000, 100000), (10000, 500000), (50000, 10000000),
                (100000, 50000000), (500000, 80000000), (1000000, 500000000),
                (5000000, 800000000), (10000000, 1000000000), (50000000, 9000000000),
                (100000000, 25000000000), (500000000, 50000000000), (1000000000, 100000000000)
            ]

            # Add damage milestones for each element
            for element in crown_utilities.elements:
                for damage, reward in damage_check:
                    milestone = {
                        "TYPE": element,
                        "AMOUNT": 0,
                        "COMPLETE": damage,
                        "REWARD": reward,
                        "COMPLETED": False,
                        "NAME": f"{crown_utilities.set_emoji(element)} {element.title()} {damage:,} Damage Dealt Milestone",
                        "UNIVERSE": universe_title
                    }
                    universe_insertion["MILESTONES"].append(milestone)

            # Define and add milestones for different battle modes
            modes = {
                "TALES": [
                    (5, 50000), (10, 100000), (25, 500000), (50, 1000000),
                    (75, 5000000), (150, 10000000), (300, 50000000), (450, 100000000),
                    (1000, 5000000000), (10000, 9000000000), (50000, 90000000000), (100000, 90000000000)
                ],
                "DUNGEON": [
                    (5, 100000), (10, 500000), (25, 1000000), (50, 5000000),
                    (80, 10000000), (100, 500000000), (150, 800000000), (250, 1000000000),
                    (500, 5000000000), (750, 9000000000), (1500, 100000000000), (5000, 500000000000)
                ],
                "SCENARIO": [
                    (5, 50000), (10, 100000), (25, 500000), (50, 1000000),
                    (100, 5000000), (150, 10000000), (300, 50000000), (450, 100000000),
                    (1000, 5000000000), (10000, 9000000000), (50000, 90000000000), (100000, 90000000000)
                ],
                "EXPLORE": [
                    (5, 50000), (10, 100000), (25, 500000), (50, 1000000),
                    (100, 5000000), (150, 10000000), (300, 50000000), (450, 100000000),
                    (1000, 5000000000), (10000, 9000000000), (50000, 90000000000), (100000, 90000000000)
                ]
            }

            for mode, milestones in modes.items():
                for complete, reward in milestones:
                    milestone = {
                        "TYPE": mode,
                        "AMOUNT": 0,
                        "COMPLETE": complete,
                        "REWARD": reward,
                        "COMPLETED": False,
                        "NAME": f"{complete} {mode.capitalize()} Completed Milestone",
                        "UNIVERSE": universe_title
                    }
                    universe_insertion["MILESTONES"].append(milestone)

            # Add the universe insertion to the player's quests
            await asyncio.to_thread(db.updateUserNoFilter,{"DID": player_class.did}, {"$push": {"QUESTS.UNIVERSES": universe_insertion}})
            return message
        return None


async def milestones_exist_check(player_class):
    milestones_exist = any(quest.get("MILESTONE_FLAG", False) for quest in player_class.quests)

    if not milestones_exist:
        milestone_field = {
            "TYPE": "MILESTONES",
            "AMOUNT": 0,
            "COMPLETE": 0,
            "REWARD": 0,
            "COMPLETED": False,
            "NAME": "Milestone",
            "MODE": "Milestone",
            "RANK": "N/A",
            "QUEST_FLAG": False,
            "MILESTONE_FLAG": True,
            "UNIVERSES": [],
            "MISC_MILESTONES": [],
        }

        milestone_templates = [
            {
                "TYPE": "TRADE",
                "milestones": [
                    (5, 50000, "5 Trades Completed Milestone"), 
                    (10, 100000, "10 Trades Completed Milestone"), 
                    (25, 500000, "25 Trades Completed Milestone"), 
                    (50, 5000000, "50 Trades Completed Milestone"), 
                    (100, 100000000, "100 Trades Completed Milestone"), 
                    (125, 500000000, "125 Trades Completed Milestone"), 
                    (150, 1000000000, "150 Trades Completed Milestone"), 
                    (200, 5000000000, "200 Trades Completed Milestone"), 
                    (250, 10000000000, "250 Trades Completed Milestone"), 
                    (500, 50000000000, "500 Trades Completed Milestone"), 
                    (1000, 100000000000, "1000 Trades Completed Milestone"), 
                    (5000, 500000000000, "5000 Trades Completed Milestone")
                ]
            },
            {
                "TYPE": "MARKETPLACE",
                "milestones": [
                    (5, 50000, "5 Marketplace Posts Completed Milestone"), 
                    (10, 100000, "10 Marketplace Posts Completed Milestone"), 
                    (25, 500000, "25 Marketplace Posts Completed Milestone"), 
                    (50, 1000000, "50 Marketplace Posts Completed Milestone"), 
                    (100, 5000000, "100 Marketplace Posts Completed Milestone"), 
                    (150, 10000000, "150 Marketplace Posts Completed Milestone"), 
                    (300, 50000000, "300 Marketplace Posts Completed Milestone"), 
                    (450, 100000000, "450 Marketplace Posts Completed Milestone"), 
                    (1000, 5000000000, "1000 Marketplace Posts Completed Milestone"), 
                    (10000, 9000000000, "10000 Marketplace Posts Completed Milestone"), 
                    (50000, 90000000000, "50000 Marketplace Posts Completed Milestone")
                ]
            },
            {
                "TYPE": "CARDS_OWNED",
                "milestones": [
                    (5, 50000, "5 Cards Acquired Milestone"), 
                    (10, 100000, "10 Cards Acquired Milestone"), 
                    (25, 500000, "25 Cards Acquired Milestone"), 
                    (50, 1000000, "50 Cards Acquired Milestone"), 
                    (100, 5000000, "100 Cards Acquired Milestone"), 
                    (150, 10000000, "150 Cards Acquired Milestone"), 
                    (300, 50000000, "300 Cards Acquired Milestone"), 
                    (450, 100000000, "450 Cards Acquired Milestone"), 
                    (1000, 5000000000, "1000 Cards Acquired Milestone"), 
                    (10000, 9000000000, "10000 Cards Acquired Milestone"), 
                    (50000, 90000000000, "50000 Cards Acquired Milestone")
                ]
            },
            {
                "TYPE": "TITLES_OWNED",
                "milestones": [
                    (5, 100000, "5 Titles Acquired Milestone"), 
                    (10, 500000, "10 Titles Acquired Milestone"), 
                    (20, 1000000, "20 Titles Acquired Milestone"), 
                    (30, 5000000, "30 Titles Acquired Milestone"), 
                    (40, 10000000, "40 Titles Acquired Milestone"), 
                    (50, 50000000, "50 Titles Acquired Milestone"), 
                    (60, 100000000, "60 Titles Acquired Milestone"), 
                    (70, 500000000, "70 Titles Acquired Milestone"), 
                    (80, 1000000000, "80 Titles Acquired Milestone"), 
                    (90, 5000000000, "90 Titles Acquired Milestone"), 
                    (100, 10000000000, "100 Titles Acquired Milestone"), 
                    (200, 50000000000, "200 Titles Acquired Milestone"), 
                    (300, 100000000000, "300 Titles Acquired Milestone"), 
                    (400, 500000000000, "400 Titles Acquired Milestone"), 
                    (500, 1000000000000, "500 Titles Acquired Milestone"), 
                    (1000, 5000000000000, "1000 Titles Acquired Milestone"), 
                    (5000, 10000000000000, "5000 Titles Acquired Milestone"), 
                    (10000, 50000000000000, "10000 Titles Acquired Milestone")
                ]
            },
            {
                "TYPE": "ARMS_OWNED",
                "milestones": [
                    (5, 50000, "5 Arms Acquired Milestone"), 
                    (10, 100000, "10 Arms Acquired Milestone"), 
                    (25, 500000, "25 Arms Acquired Milestone"), 
                    (50, 1000000, "50 Arms Acquired Milestone"), 
                    (100, 5000000, "100 Arms Acquired Milestone"), 
                    (150, 10000000, "150 Arms Acquired Milestone"), 
                    (300, 50000000, "300 Arms Acquired Milestone"), 
                    (450, 100000000, "450 Arms Acquired Milestone"), 
                    (1000, 5000000000, "1000 Arms Acquired Milestone"), 
                    (10000, 9000000000, "10000 Arms Acquired Milestone"), 
                    (50000, 90000000000, "50000 Arms Acquired Milestone")
                ]
            },
            {
                "TYPE": "TALISMANS_OWNED",
                "milestones": [
                    (5, 50000, "5 Talismans Acquired Milestone"), 
                    (10, 100000, "10 Talismans Acquired Milestone"), 
                    (25, 500000, "25 Talismans Acquired Milestone"), 
                    (50, 1000000, "50 Talismans Acquired Milestone"), 
                    (100, 5000000, "100 Talismans Acquired Milestone"), 
                    (150, 10000000, "150 Talismans Acquired Milestone"), 
                    (300, 50000000, "300 Talismans Acquired Milestone"), 
                    (450, 100000000, "450 Talismans Acquired Milestone"), 
                    (1000, 5000000000, "1000 Talismans Acquired Milestone"), 
                    (10000, 9000000000, "10000 Talismans Acquired Milestone"), 
                    (50000, 90000000000, "50000 Talismans Acquired Milestone")
                ]
            },
            {
                "TYPE": "SUMMONS_OWNED",
                "milestones": [
                    (5, 50000, "5 Summons Acquired Milestone"), 
                    (10, 100000, "10 Summons Acquired Milestone"), 
                    (25, 500000, "25 Summons Acquired Milestone"), 
                    (50, 1000000, "50 Summons Acquired Milestone"), 
                    (100, 5000000, "100 Summons Acquired Milestone"), 
                    (150, 10000000, "150 Summons Acquired Milestone"), 
                    (300, 50000000, "300 Summons Acquired Milestone"), 
                    (450, 100000000, "450 Summons Acquired Milestone"), 
                    (1000, 5000000000, "1000 Summons Acquired Milestone"), 
                    (10000, 9000000000, "10000 Summons Acquired Milestone"), 
                    (50000, 90000000000, "50000 Summons Acquired Milestone")
                ]
            },
            {
                "TYPE": "TUTORIAL",
                "milestones": [
                    (1, 50000, "Tutorial Milestone Completed"), 
                    (2, 100000, "Tutorial Student Milestone Completed"), 
                    (3, 500000, "Tutorial Graduate Milestone Completed"), 
                    (4, 1000000, "Tutorial Expert Milestone Completed"), 
                    (5, 5000000, "Tutorial Master Milestone Completed"), 
                    (10, "Kakashi Hatake", "Secret Tutorial God Milestone Completed")
                ]
            },
            {
                "TYPE": "BLACKSMITH",
                "milestones": [
                    (5, 5000000, "Blacksmith Mastery Milestone Completed"), 
                    (15, 10000000, "Blacksmith Expert Milestone Completed"), 
                    (50, 50000000, "Blacksmith Master Milestone Completed"), 
                    (100, 100000000, "Blacksmith God Milestone Completed")
                ]
            },
            {
                "TYPE": "ROLL",
                "milestones": [
                    (5, 5000000, "5 Rolls Completed Milestone"), 
                    (10, 5000000, "10 Rolls Completed Milestone"), 
                    (25, 5000000, "25 Rolls Completed Milestone"), 
                    (50, 5000000, "50 Rolls Completed Milestone"), 
                    (80, 5000000, "80 Rolls Completed Milestone"), 
                    (100, 10000000, "100 Rolls Completed Milestone"), 
                    (150, 10000000, "150 Rolls Completed Milestone"), 
                    (180, 10000000, "180 Rolls Completed Milestone"), 
                    (200, 10000000, "200 Rolls Completed Milestone"), 
                    (250, 10000000, "250 Rolls Completed Milestone"), 
                    (300, 30000000, "300 Rolls Completed Milestone"), 
                    (500, 50000000, "500 Rolls Completed Milestone"), 
                    (750, 100000000, "750 Rolls Completed Milestone"), 
                    (1000, 500000000, "1000 Rolls Completed Milestone"), 
                    (1500, 1000000000, "1500 Rolls Completed Milestone"), 
                    (2000, 5000000000, "2000 Rolls Completed Milestone"), 
                    (5000, 10000000000, "5000 Rolls Completed Milestone"), 
                    (10000, 50000000000, "10000 Rolls Completed Milestone"), 
                    (50000, 100000000000, "50000 Rolls Completed Milestone"), 
                    (100000, 500000000000, "100000 Rolls Completed Milestone"), 
                    (500000, 1000000000000, "500000 Rolls Completed Milestone"), 
                    (1000000, 5000000000000, "1000000 Rolls Completed Milestone"), 
                    (5000000, 10000000000000, "5000000 Rolls Completed Milestone")
                ]
            },
            {
                "TYPE": "DAILY",
                "milestones": [
                    (1, 1000000, "Daily Milestone Completed"), 
                    (2, 1000000, "Daily Double Milestone Completed"), 
                    (3, 5000000, "Daily Triple Milestone Completed"), 
                    (5, 1000000, "Daily Consistency Milestone Completed"), 
                    (10, 1000000, "Daily Boom Milestone Completed"), 
                    (15, 1000000, "Daily Boom Boom Milestone Completed"), 
                    (20, 1000000, "Daily Boom Boom Boom Milestone Completed"), 
                    (30, 20000000, "Daily Execution Milestone Completed"), 
                    (40, 10000000, "Daily Executioner Milestone Completed"), 
                    (50, 50000000, "Daily Executioner 2 Milestone Completed"), 
                    (60, 1000000, "Daily Executioner 3 Milestone Completed"), 
                    (70, 1000000, "Daily Executioner 4 Milestone Completed"), 
                    (80, 1000000, "Daily Executioner 5 Milestone Completed"), 
                    (100, 100000000, "Master of Daily Milestones Completed"), 
                    (130, 100000000, "Master of Daily Milestones 2 Completed"), 
                    (150, 300000000, "Master of Daily Milestones 3 Completed"), 
                    (200, 500000000, "Master of Daily Milestones 4 Completed"), 
                    (250, 1000000000, "Master of Daily Milestones 5 Completed"), 
                    (300, 5000000000, "Master of Daily Milestones 6 Completed"), 
                    (380, 10000000000, "Master of Daily Milestones 7 Completed"), 
                    (400, 50000000000, "Master of Daily Milestones 8 Completed"), 
                    (500, 100000000000, "Master of Daily Milestones 9 Completed"), 
                    (600, 500000000000, "Master of Daily Milestones 10 Completed"), 
                    (700, 1000000000000, "Master of Daily Milestones 11 Completed"), 
                    (1000, 5000000000000, "God of Daily Milestones Completed")
                ]
            },
            {
                "TYPE": "DONATION",
                "milestones": [
                    (100000, 10000000, "Guild Investor Milestone Completed"), 
                    (500000, 50000000, "Guild Investor 2 Milestone Completed"), 
                    (10000000, 10000000, "Guild Investor 3 Milestone Completed"), 
                    (50000000, 10000000, "Guild Investor 4 Milestone Completed"), 
                    (100000000, 100000000, "The Guild Comes First! Milestone Completed"), 
                    (500000000, 100000000, "The Guild Comes First! 2 Milestone Completed"), 
                    (1000000000, 500000000, "The Guild Comes First! 3 Milestone Completed"), 
                    (10000000000, 1500000000, "The Guild Comes First! 4 Milestone Completed"), 
                    (50000000000, 5000000000, "Through The Wire! Milestone Completed"), 
                    (100000000000, 10000000000, "Through The Wire! 2 Milestone Completed"), 
                    (500000000000, 50000000000, "Through The Wire! 3 Milestone Completed"), 
                    (1000000000000, 100000000000, "Through The Wire! 4 Milestone Completed"), 
                    (5000000000000, 500000000000, "Guild God! Milestone Completed"), 
                    (10000000000000, 1000000000000, "Guild God 2! Milestone Completed"), 
                    (50000000000000, 5000000000000, "Guild God 3! Milestone Completed"), 
                    (100000000000000, 10000000000000, "Guild God 4! Milestone Completed"), 
                    (500000000000000, 50000000000000, "Guild God 5! Milestone Completed")
                ]
            }
        ]

        for template in milestone_templates:
            for amount, reward, name in template["milestones"]:
                milestone = {
                    "TYPE": template["TYPE"],
                    "AMOUNT": 0,
                    "COMPLETE": amount,
                    "REWARD": reward,
                    "COMPLETED": False,
                    "NAME": name
                }
                milestone_field["MISC_MILESTONES"].append(milestone)

        await asyncio.to_thread(db.updateUserNoFilter,{"DID": player_class.did}, {"$push": {"QUESTS": milestone_field}})


def milestone_universe_exist(player_class, universe_title):
    for quest in player_class.quests:
        universes = quest.get("UNIVERSES", [])
        for universe in universes:
            if universe.get("UNIVERSE") == universe_title:
                return True
    return False
    
            




def setup(bot):
    Quests(bot)