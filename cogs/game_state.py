import db
import custom_logging
import crown_utilities
import asyncio
import textwrap
from cogs.reward_drops import reward_drop, scenario_drop
from cogs.quests import Quests
import time
from interactions import Client, ActionRow, Button, File, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension


class GameState(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('GameState Cog is ready!')

    # async def save_spot(self, player, universe_title, mode, currentopponent):
    #     """
    #     Update this with the bot.py function that updates save_spot as well as to not store duplicate save spots
    #     """
    #     try:
    #         player.make_available()
    #         for save_spot in player.save_spot:
    #             if save_spot['UNIVERSE'] == universe_title and save_spot['MODE'] == mode:
    #                 query = {"DID": player.did}
    #                 new_value = {"$pull": {"SAVE_SPOT": {"UNIVERSE": universe_title, "MODE": str(mode)}}}
    #                 db.updateUserNoFilter(query, new_value)

    #         user = {"DID": str(player.did)}
    #         query = {"$addToSet": {"SAVE_SPOT": {"UNIVERSE": universe_title, "MODE": str(mode), "CURRENTOPPONENT": currentopponent}}}
    #         response = db.updateUserNoFilter(user, query)
    #         return
    #     except Exception as ex:
    #         custom_logging.debug(ex)

    async def save_spot(self, player, universe_title, mode, currentopponent):
        """
        Update this with the bot.py function that updates save_spot as well as to not store duplicate save spots
        """
        try:
            player.make_available()

            # Remove existing save spot if it exists
            query = {
                "DID": player.did,
                "SAVE_SPOT.UNIVERSE": universe_title,
                "SAVE_SPOT.MODE": mode
            }
            update = {
                "$pull": {
                    "SAVE_SPOT": {
                        "UNIVERSE": universe_title,
                        "MODE": mode
                    }
                }
            }
            db.updateUserNoFilter(query, update)

            # Add new save spot
            query = {"DID": player.did}
            update = {
                "$addToSet": {
                    "SAVE_SPOT": {
                        "UNIVERSE": universe_title,
                        "MODE": mode,
                        "CURRENTOPPONENT": currentopponent
                    }
                }
            }
            db.updateUserNoFilter(query, update)
            
        except Exception as ex:
            custom_logging.debug(ex)


    async def delete_save_spot(self, player, universe_title, mode, currentopponent):
        """
        Update this with the bot.py function that updates save_spot as well as to not store duplicate save spots
        """
        try:
            for save_spot in player.save_spot:
                if save_spot['UNIVERSE'] == universe_title and save_spot['MODE'] == mode:
                    query = {"DID": player.did}
                    new_value = {"$pull": {"SAVE_SPOT": {"UNIVERSE": universe_title, "MODE": str(mode)}}}
                    db.updateUserNoFilter(query, new_value)

            return
        except Exception as ex:
            custom_logging.debug(ex)


    async def pvp_end_game(self, battle_config, private_channel, battle_msg):
        try:
            if battle_config.is_pvp_game_mode:
                total_complete = False
                battle_config.player1_card.stats_handler(battle_config, battle_config.player1, total_complete)
                battle_config.player2_card.stats_handler(battle_config, battle_config.player2, total_complete)
                battle_config.player1.make_available()
                talisman_response = crown_utilities.decrease_talisman_count(battle_config.player1.did, battle_config.player1.equipped_talisman)
                arm_durability_message = crown_utilities.update_arm_durability(battle_config.player1, battle_config.player1_arm, battle_config.player1_card)
                
                battle_config.continue_fighting = False

                if arm_durability_message != False:
                    await private_channel.send(f"{arm_durability_message}")

                if battle_config.player1_wins:
                    pvp_response = await battle_config.pvp_victory_embed(battle_config.player1, battle_config.player1_card, battle_config.player1_arm, battle_config.player1_title, battle_config.player2, battle_config.player2_card)
                else:
                    if battle_config.is_tutorial_game_mode:
                        pvp_response = await battle_config.you_lose_embed(battle_config.player1_card, battle_config.player2_card, companion_card = None)
                    else:
                        pvp_response = await battle_config.pvp_victory_embed(battle_config.player2, battle_config.player2_card, battle_config.player2_arm, battle_config.player2_title, battle_config.player1, battle_config.player1_card)

                if not battle_config.is_tutorial_game_mode and battle_config.is_co_op_mode:
                    co_op_talisman_response = crown_utilities.decrease_talisman_count(battle_config.player2.did, battle_config.player2.equipped_talisman)
                    co_op_arm_durability_message = crown_utilities.update_arm_durability(battle_config.player2, battle_config.player2_arm, battle_config.player2_card)
                    if co_op_arm_durability_message != False:
                        await private_channel.send(f"{co_op_arm_durability_message}")

                await battle_msg.delete(delay=2)
                await asyncio.sleep(2)
                battle_msg = await private_channel.send(embed=pvp_response)
                
                return
            else:
                return False
        except Exception as ex:
            custom_logging.debug(ex)
            return False


    async def you_lose_non_pvp(self, battle_config, private_channel, battle_msg, user1, user2=None):
        if battle_config.player2_wins:
            total_complete = False
            battle_config.player1_card.stats_handler(battle_config, battle_config.player1, total_complete)
            battle_config.player1.make_available()
            battle_config.rematch_buff = False

            play_again_buttons = [
                Button(
                    style=ButtonStyle.BLUE,
                    label="Start Over",
                    custom_id=f"{battle_config._uuid}|play_again_yes"
                ),
                Button(
                    style=ButtonStyle.RED,
                    label="End",
                    custom_id=f"{battle_config._uuid}|play_again_no"
                )
            ]
            
            if battle_config.player1.guild != 'PCG':
                team_info = db.queryTeam({'TEAM_NAME': str(battle_config.player1.guild.lower())})
                guild_buff_info = team_info['ACTIVE_GUILD_BUFF']
                if guild_buff_info == 'Rematch':
                    battle_config.rematch_buff =True
            
            if battle_config.rematch_buff:
                play_again_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=f"Guild Rematches Available!",
                        custom_id=f"{battle_config._uuid}|guild_rematch"
                    )
                )
            
            elif battle_config.player1.retries >= 1:
                play_again_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=f"{battle_config.player1.retries} Rematches Available!",
                        custom_id=f"{battle_config._uuid}|player_rematch"
                    )
                )
            else:
                battle_config.rematch_buff = False

            play_again_buttons_action_row = ActionRow(*play_again_buttons)

            talisman_response = crown_utilities.decrease_talisman_count(battle_config.player1.did, battle_config.player1.equipped_talisman)
            arm_durability_message = crown_utilities.update_arm_durability(battle_config.player1, battle_config.player1_arm, battle_config.player1_card)
            if arm_durability_message != False:
                await private_channel.send(f"{arm_durability_message}")
            if battle_config.is_duo_mode or battle_config.is_co_op_mode:
                if battle_config.is_co_op_mode and not battle_config.is_duo_mode:
                    co_op_talisman_response = crown_utilities.decrease_talisman_count(battle_config.player3.did, battle_config.player3.equipped_talisman)
                    co_op_arm_durability_message = crown_utilities.update_arm_durability(battle_config.player3, battle_config.player3_arm, battle_config.player3_card)
                    if co_op_arm_durability_message != False:
                        await private_channel.send(f"{co_op_arm_durability_message}")
                loss_response = await battle_config.you_lose_embed(battle_config.player1_card, battle_config.player2_card, battle_config.player3_card)
            else:
                loss_response = await battle_config.you_lose_embed(battle_config.player1_card, battle_config.player2_card, None)
            
            # await battle_msg.delete()
            await asyncio.sleep(1)
            end_msg = await private_channel.send(embed=loss_response, components=[play_again_buttons_action_row])

            def check(component: Button) -> bool:
                return component.ctx.author == user1

            try:
                button_ctx  = await self.bot.wait_for_component(components=play_again_buttons_action_row, timeout=300, check=check)

                if button_ctx.ctx.custom_id == f"{battle_config._uuid}|play_again_no":
                    if battle_config.is_duo_mode or battle_config.is_co_op_mode:
                        loss_response = await battle_config.you_lose_embed(battle_config.player1_card, battle_config.player2_card, battle_config.player3_card)
                    else:
                        loss_response = await battle_config.you_lose_embed(battle_config.player1_card, battle_config.player2_card, None)
                    # await battle_msg.delete()
                    await end_msg.edit(embed=loss_response, components=[])
                    
                    
                    if battle_config.player1.autosave and battle_config.match_can_be_saved:
                        await end_msg.edit(embed = battle_config.saved_game_embed(battle_config.player1_card, battle_config.player2_card))
                        
                    else:
                        await end_msg.edit(embed = battle_config.close_pve_embed(battle_config.player1_card, battle_config.player2_card))
                    battle_config.continue_fighting = False
                    return

                if button_ctx.ctx.custom_id == f"{battle_config._uuid}|play_again_yes":
                    battle_config.current_opponent_number = 0
                    battle_config.reset_game()
                    # print(f"CURRENT OPPONENT {battle_config.current_opponent_number}")
                    battle_config.continue_fighting = True
                    
                if button_ctx.ctx.custom_id == f"{battle_config._uuid}|player_rematch":
                    new_info = await crown_utilities.updateRetry(battle_config.player1.did, "U","DEC")
                    battle_config.player1.retries = battle_config.player1.retries - 1
                    battle_config.reset_game()
                    battle_config.continue_fighting = True
                    battle_config.player1_card.used_focus = False
                    battle_config.player1_card.used_resolve = False
                    battle_config.player1_card.resolved = False
                    battle_config.player1_card.focused = False
                    battle_config.player2_card.resolved = False
                    battle_config.player2_card.focused = False
                    battle_config.player2_card.used_focus = False
                    battle_config.player2_card.used_resolve = False
                    if battle_config.is_co_op_mode or battle_config.is_duo_mode:
                        battle_config.player3.used_focus = False
                        battle_config.player3.used_resolve = False
                
                if button_ctx.ctx.custom_id == f"{battle_config._uuid}|guild_rematch":
                    battle_config.reset_game()
                    new_info = await crown_utilities.guild_buff_update_function(str(battle_config.player1.guild.lower()))
                    update_team_response = db.updateTeam(new_info['QUERY'], new_info['UPDATE_QUERY'])
                    battle_config.continue_fighting = True
                    battle_config.player1_card.used_focus = False
                    battle_config.player1_card.used_resolve = False
                    battle_config.player1_card.resolved = False
                    battle_config.player1_card.focused = False
                    battle_config.player2_card.resolved = False
                    battle_config.player2_card.focused = False
                    battle_config.player2_card.used_focus = False
                    battle_config.player2_card.used_resolve = False
                    if battle_config.is_co_op_mode or battle_config.is_duo_mode:
                        battle_config.player3.used_focus = False
                        battle_config.player3.used_resolve = False
            
            
            except Exception as ex:
                custom_logging.debug(ex)
                return
        else:
            return False 


    async def you_win_non_pvp(self, battle_config, private_channel, battle_msg, gameClock, user1, user2=None):
        total_complete = False
        # Finish This Tomorrow
        if battle_config.player1_wins and not battle_config.is_pvp_game_mode:

            if any((battle_config.is_tales_game_mode, battle_config.is_dungeon_game_mode, battle_config.is_boss_game_mode)):
                reward_msg = await reward_drop(self, battle_config, battle_config.player1)

                p1_win_rewards = await battle_config.get_non_drop_rewards(battle_config.player1)
                # questlogger = await quest(user1, battle_config.player2_card, battle_config.mode)
                petlogger = await crown_utilities.summonlevel(battle_config.player1, battle_config.player1_card)
                cardlogger = await crown_utilities.cardlevel(user1, battle_config.mode)

                if not battle_config.is_easy_difficulty:
                    petlogger = await crown_utilities.summonlevel(battle_config.player1, battle_config.player1_card)
                    cardlogger = await crown_utilities.cardlevel(user1, battle_config.mode)
                    talisman_response = crown_utilities.decrease_talisman_count(battle_config.player1.did, battle_config.player1.equipped_talisman)
                    arm_durability_message = crown_utilities.update_arm_durability(battle_config.player1, battle_config.player1_arm, battle_config.player1_card)
                    if arm_durability_message != False:
                        await private_channel.send(f"{arm_durability_message}")
        

                if battle_config.is_co_op_mode and not battle_config.is_duo_mode:
                    co_op_reward_msg = await reward_drop(self, battle_config, battle_config.player3)
                    co_op_talisman_response = crown_utilities.decrease_talisman_count(battle_config.player3.did, battle_config.player3.equipped_talisman)
                    co_op_arm_durability_message = crown_utilities.update_arm_durability(battle_config.player3, battle_config.player3_arm, battle_config.player3_card)
                    if co_op_arm_durability_message != False:
                        await private_channel.send(f"{co_op_arm_durability_message}")
                        
                    co_op_bonuses = battle_config.get_co_op_bonuses(battle_config.player1, battle_config.player3)
                    p3_win_rewards = await battle_config.get_non_drop_rewards(battle_config.player3)
                    # p3_questlogger = await quest(user2, battle_config.player2_card, battle_config.mode)
                    p3_petlogger = await crown_utilities.summonlevel(battle_config.player3, battle_config.player3_card)
                    p3_cardlogger = await crown_utilities.cardlevel(user2, battle_config.mode)
                    p3_co_op_bonuses = battle_config.get_co_op_bonuses(battle_config.player3, battle_config.player1)


                if battle_config.current_opponent_number != (battle_config.total_number_of_opponents):
                    if battle_config.is_dungeon_game_mode:
                        quest_response = await Quests.quest_check(battle_config.player1, "DUNGEONS")
                        milestone_reponse = await Quests.milestone_check(battle_config.player1, "DUNGEONS_RUN", 1)
                    else:
                        quest_response = await Quests.quest_check(battle_config.player1, "TALES")
                        milestone_reponse = await Quests.milestone_check(battle_config.player1, "TALES_RUN", 1)
                    battle_config.player1_card.stats_handler(battle_config, battle_config.player1, total_complete)
                    
                    if not battle_config.is_co_op_mode:
                        embedVar = Embed(title=f"🎊 VICTORY\nThe game lasted {battle_config.turn_total} rounds.",color=0x1abc9c)
                        embedVar.add_field(name=f"Rewards", value=f"{reward_msg}\nEarned {p1_win_rewards['ESSENCE']} {p1_win_rewards['RANDOM_ELEMENT']} Essence")
                        embedVar.set_footer(text=f"{battle_config.get_previous_moves_embed()}")
                        if quest_response:
                            embedVar.add_field(name="**Quest Complete**",
                                value=f"{quest_response}")

                        # Define a list of milestones to check
                        milestones = [
                            (battle_config.player1, battle_config.battle_mode, 1, battle_config.selected_universe),
                            (battle_config.player1, battle_config.player1_card.move1_element, battle_config.player1_card.move1_damage_dealt, battle_config.selected_universe),
                            (battle_config.player1, battle_config.player1_card.move2_element, battle_config.player1_card.move2_damage_dealt, battle_config.selected_universe),
                            (battle_config.player1, battle_config.player1_card.move3_element, battle_config.player1_card.move3_damage_dealt, battle_config.selected_universe),
                        ]

                        # Check milestones and add messages to the embed
                        for milestone in milestones:
                            milestone_messages = await Quests.milestone_check(*milestone)
                            if milestone_messages:
                                for message in milestone_messages:
                                    embedVar.add_field(name="🏆 Milestone", value=message)



                        f_message = battle_config.get_most_focused(battle_config.player1_card, battle_config.player2_card)
                        embedVar.add_field(name=f"🌀 | Focus Count",
                                        value=f"**{battle_config.player2_card.name}**: {battle_config.player2_card.focus_count}\n**{battle_config.player1_card.name}**: {battle_config.player1_card.focus_count}")
                        #Most Damage Dealth
                        d_message = battle_config.get_most_damage_dealt(battle_config.player1_card, battle_config.player2_card)
                        embedVar.add_field(name=f"💥 | Damage Dealt",
                                        value=f"**{battle_config.player2_card.name}**: {battle_config.player2_card.damage_dealt}\n**{battle_config.player1_card.name}**: {battle_config.player1_card.damage_dealt}")
                        #Most Healed
                        h_message = battle_config.get_most_damage_healed(battle_config.player1_card, battle_config.player2_card)
                        embedVar.add_field(name=f"❤️‍🩹 | Healing",
                                        value=f"**{battle_config.player2_card.name}**: {battle_config.player2_card.damage_healed}\n**{battle_config.player1_card.name}**: {battle_config.player1_card.damage_healed}")

                    elif battle_config.is_co_op_mode and not battle_config.is_duo_mode:
                        if battle_config.is_co_op_mode:
                            battle_config.player3_card.stats_handler(battle_config, battle_config.player3, total_complete)
                        embedVar = Embed(title=f"👥 CO-OP VICTORY\nThe game lasted {battle_config.turn_total} rounds.\n\n👤**{battle_config.player1.disname}:** {drop_response}\nEarned {p1_win_rewards['ESSENCE']} {p1_win_rewards['RANDOM_ELEMENT']} Essence\n👥**{battle_config.player3.disname}:** {cdrop_response}\nEarned {p3_win_rewards['ESSENCE']} {p3_win_rewards['RANDOM_ELEMENT']} Essence",description=textwrap.dedent(f"""
                        {battle_config.get_previous_moves_embed()}
                        
                        """),color=0x1abc9c)
                        embedVar.add_field(name="**Co-Op Bonus**",
                                value=f"{co_op_bonuses}")
                        # if questlogger:
                        #     embedVar.add_field(name="**Quest Progress**",
                        #         value=f"{questlogger}")

                    elif battle_config.is_duo_mode:
                        embedVar = Embed(title=f"🎊 DUO VICTORY\nThe game lasted {battle_config.turn_total} rounds.\n\n{reward_drop}",description=textwrap.dedent(f"""
                        {battle_config.get_previous_moves_embed()}
                        
                        """),color=0x1abc9c)
                        
                    if battle_config.is_co_op_mode:
                        battle_config.player3_card.damage_dealt = round(battle_config.player3_card.damage_dealt)
                        battle_config.player3_card.damage_healed = round(battle_config.player3_card.damage_healed)
                        f_message = battle_config.get_most_focused(battle_config.player1_card, battle_config.player2_card, battle_config.player3_card)
                        embedVar.add_field(name=f"🌀 | Focus Count",
                                        value=f"**{battle_config.player2_card.name}**: {battle_config.player2_card.focus_count}\n**{battle_config.player1_card.name}**: {battle_config.player1_card.focus_count}\n**{battle_config.player3_card.name}**: {battle_config.player3_card.focus_count}")
                        #Most Damage Dealth
                        d_message = battle_config.get_most_damage_dealt(battle_config.player1_card, battle_config.player2_card, battle_config.player3_card)
                        embedVar.add_field(name=f"🗯️ | Damage Dealt",
                                        value=f"**{battle_config.player2_card.name}**: {battle_config.player2_card.damage_dealt}\n**{battle_config.player1_card.name}**: {battle_config.player1_card.damage_dealt}\n**{battle_config.player3_card.name}**: {battle_config.player3_card.damage_dealt}")
                        #Most Healed
                        h_message = battle_config.get_most_damage_healed(battle_config.player1_card, battle_config.player2_card, battle_config.player3_card)
                        embedVar.add_field(name=f"❤️‍🩹 | Healing",
                                        value=f"**{battle_config.player2_card.name}**: {battle_config.player2_card.damage_healed}\n**{battle_config.player1_card.name}**: {battle_config.player1_card.damage_healed}\n**{battle_config.player3_card.name}**: {battle_config.player3_card.damage_healed}")

                    if battle_config.is_dungeon_game_mode:
                        if battle_config.crestsearch:
                            await crown_utilities.blessguild(10000, battle_config.player1.association)
                            embedVar.add_field(name=f"**{battle_config.selected_universe} Crest Search!**",
                                            value=f":flags:**{battle_config.player1.association}** earned **100,000** 🪙")
                    
                    embedVar.set_author(name=f"{battle_config.player2_card.name} lost!")
                    
                    await battle_msg.delete(delay=2)
                    await asyncio.sleep(2)
                    battle_msg = await private_channel.send(embed=embedVar)
                    battle_config.reset_game()
                    battle_config.current_opponent_number = battle_config.current_opponent_number + 1
                    battle_config.continue_fighting = True


                if battle_config.current_opponent_number == (battle_config.total_number_of_opponents):
                    battle_config.continue_fighting = False
                    if battle_config.is_dungeon_game_mode:
                        quest_response = await Quests.quest_check(battle_config.player1, "FULL DUNGEONS")
                    else:
                        quest_response = await Quests.quest_check(battle_config.player1, "FULL TALES")
                    total_complete = True
                    battle_config.player1_card.stats_handler(battle_config, battle_config.player1, total_complete)
                    if battle_config.is_co_op_mode:
                        battle_config.player3_card.stats_handler(battle_config, battle_config.player3, total_complete)

                    # if battle_config.player1.autosave == True:
                    #     await self.save_spot(battle_config.player1, battle_config.selected_universe, battle_config.mode, 0)
                    if battle_config.is_dungeon_game_mode:
                        embedVar = Embed(title=f"🔥 DUNGEON CONQUERED",description=f"**{battle_config.selected_universe} Dungeon** has been conquered\n\n{reward_drop}",
                                                color=0xe91e63)
                        
                        if quest_response:
                            embedVar.add_field(name="**Quest Complete**",
                                value=f"{quest_response}")
                        
                        # Define a list of milestones to check
                        milestones = [
                            (battle_config.player1, "DUNGEONS_COMPLETED", 1),
                            (battle_config.player1, battle_config.battle_mode, 1, battle_config.selected_universe),
                            (battle_config.player1, battle_config.player1_card.move1_element, battle_config.player1_card.move1_damage_dealt, battle_config.selected_universe),
                            (battle_config.player1, battle_config.player1_card.move2_element, battle_config.player1_card.move2_damage_dealt, battle_config.selected_universe),
                            (battle_config.player1, battle_config.player1_card.move3_element, battle_config.player1_card.move3_damage_dealt, battle_config.selected_universe),
                        ]

                        # Check milestones and add messages to the embed
                        for milestone in milestones:
                            milestone_messages = await Quests.milestone_check(*milestone)
                            if milestone_messages:
                                for message in milestone_messages:
                                    embedVar.add_field(name="🏆 Milestone", value=message)
                        
                        if battle_config.crestsearch:
                            await crown_utilities.blessguild(100000, battle_config.player1.association)
                            teambank = await crown_utilities.blessteam(100000, battle_config.player1.guild)
                            await movecrest(battle_config.selected_universe, battle_config.player1.association)
                            embedVar.add_field(name=f"**{battle_config.selected_universe}** CREST CLAIMED!",
                                            value=f"**{battle_config.player1.association}** earned the {battle_config.selected_universe} **Crest**")

                        if not battle_config.is_easy_difficulty:
                            upload_query = {'DID': str(battle_config.player1.did)}
                            new_upload_query = {'$addToSet': {'DUNGEONS': battle_config.selected_universe},
                                                '$set': {'BOSS_FOUGHT' : False}}
                            r = db.updateUserNoFilter(upload_query, new_upload_query)
                        
                        if battle_config.selected_universe in battle_config.player1.completed_dungeons:
                            await crown_utilities.bless(50000000, battle_config.player1.did)
                            await battle_msg.delete(delay=2)
                            await asyncio.sleep(2)
                            embedVar.add_field(name="Minor Reward",
                                        value=f"You were awarded 🪙 50,000,000 for completing the {battle_config.selected_universe} Dungeon again!")
                            embedVar.add_field(name="Boss Key Aquired!",
                                        value=f"The Boss Arena has been Unlocked!")
                        else:
                            await crown_utilities.bless(500000000, battle_config.player1.did)
                            await battle_msg.delete(delay=2)
                            await asyncio.sleep(2)
                            embedVar.add_field(name="Dungeon Reward",
                                        value=f"You were awarded 🪙 500,000,000 for completing the {battle_config.selected_universe} Dungeon!")
                        if battle_config.is_co_op_mode and not battle_config.is_duo_mode:
                            await crown_utilities.bless(500000, battle_config.player3.did)
                            await asyncio.sleep(2)
                            
                            await private_channel.send(
                                f"{user2.mention} You were awarded 🪙 500,000 for  assisting in the {battle_config.selected_universe} Dungeon!")
                        battle_msg = await private_channel.send(embed=embedVar)
                        battle_config.continue_fighting = False

                        await self.delete_save_spot(battle_config.player1, battle_config.selected_universe, battle_config.mode, 0)
                        return
                    
                    if battle_config.is_tales_game_mode:
                        embedVar = Embed(title=f"🎊 UNIVERSE CONQUERED",
                                                description=f"**{battle_config.selected_universe}** has been conquered\n\n{reward_drop}",
                                                color=0xe91e63)
                        if quest_response:
                            embedVar.add_field(name="**Quest Complete**",
                                value=f"{quest_response}")
                        
                        # Define a list of milestones to check
                        milestones = [
                            (battle_config.player1, "TALES_COMPLETED", 1),
                            (battle_config.player1, battle_config.battle_mode, 1, battle_config.selected_universe),
                            (battle_config.player1, battle_config.player1_card.move1_element, battle_config.player1_card.move1_damage_dealt, battle_config.selected_universe),
                            (battle_config.player1, battle_config.player1_card.move2_element, battle_config.player1_card.move2_damage_dealt, battle_config.selected_universe),
                            (battle_config.player1, battle_config.player1_card.move3_element, battle_config.player1_card.move3_damage_dealt, battle_config.selected_universe),
                        ]

                        # Check milestones and add messages to the embed
                        for milestone in milestones:
                            milestone_messages = await Quests.milestone_check(*milestone)
                            if milestone_messages:
                                for message in milestone_messages:
                                    embedVar.add_field(name="🏆 Milestone", value=message)
                        
                        if not battle_config.is_easy_difficulty:
                            embedVar.set_author(name=f"{battle_config.selected_universe} Dungeon has been unlocked!")
                            upload_query = {'DID': str(battle_config.player1.did)}
                            new_upload_query = {'$addToSet': {'CROWN_TALES': battle_config.selected_universe}}
                            await asyncio.to_thread(db.updateUserNoFilter, upload_query, new_upload_query)
                        if battle_config.selected_universe in battle_config.player1.completed_tales:
                            await crown_utilities.bless(2500000, battle_config.player1.did)
                            await battle_msg.delete(delay=2)
                            await asyncio.sleep(2)
                            embedVar.add_field(name="Minor Reward",
                                        value=f"You were awarded 🪙 2,500,000 for completing the {battle_config.selected_universe} Tale again!")
                        else:
                            await crown_utilities.bless(100000000, battle_config.player1.did)
                            # await ctx.send(embed=embedVar)
                            await battle_msg.delete(delay=2)
                            await asyncio.sleep(2)
                            
                            embedVar.add_field(name="Conquerors Reward",
                                        value=f"You were awarded 🪙 100,000,000 for completing the {battle_config.selected_universe} Tale!")
                            # battle_msg = await private_channel.send(embed=embedVar)
                        if battle_config.is_co_op_mode and not battle_config.is_duo_mode:
            
                            await crown_utilities.bless(250000, battle_config.player3.did)
                            # await crown_utilities.bless(125, user2)
                            # await ctx.send(embed=embedVar)
                            await asyncio.sleep(2)
                            embedVar.add_field(name="Companion Reward",
                                        value=f"{user2.mention} You were awarded 🪙 250,000 for assisting in the {battle_config.selected_universe} Tale!")
                            
                        battle_msg = await private_channel.send(embed=embedVar)
                        battle_config.continue_fighting = False
                        
                        await self.delete_save_spot(battle_config.player1, battle_config.selected_universe, battle_config.mode, 0)
                        return

                if battle_config.is_boss_game_mode:
                    battle_config.player1_card.stats_handler(battle_config, battle_config.player1, total_complete)
                    if battle_config.is_co_op_mode:
                        battle_config.player3_card.stats_handler(battle_config, battle_config.player3, total_complete)
                        embedVar = Embed(title=f"⚡ **{battle_config.player1_card.name}** and **{battle_config.player3_card}** defeated the {battle_config.selected_universe} Boss {battle_config.player2_card.name}!\nMatch concluded in {battle_config.turn_total} turns!\n\n{drop_response} + 🪙 15,000!\n\n{battle_config.player3_card.name} got 🪙 10,000!", color=0x1abc9c)
                        embedVar.set_author(name=f"**{battle_config.player2_card.name}** Says: {battle_config._concede_boss_description}")
                        embedVar.add_field(name="**Co-Op Bonus**",
                                    value=f"{p3_co_op_bonuses}")
                    else:
                        embedVar = Embed(title=f"⚡ **{battle_config.player1_card.name}** defeated the {battle_config.selected_universe} Boss {battle_config.player2_card.name}!\nMatch concluded in {battle_config.turn_total} turns!\n\n{drop_response} + 🪙 25,000!",color=0x1abc9c)
                    await crown_utilities.bless(25000, str(battle_config.player1.did))
                    embedVar.set_footer(text=f"{battle_config.get_previous_moves_embed()}")

                    if battle_config.crestsearch:
                        await crown_utilities.blessguild(25000, battle_config.player1.association)
                        teambank = await crown_utilities.blessteam(5000, battle_config.player1.guild)
                        await movecrest(battle_config.selected_universe, battle_config.player1.association)
                        embedVar.add_field(name=f"**{battle_config.selected_universe} Crest Claimed**!",
                                        value=f":flags:**{battle_config.player1.association}** earned the {battle_config.selected_universe} **Crest**")
                    embedVar.set_author(name=f"{battle_config.player2_card.name} lost",
                                        icon_url="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620236432/PCG%20LOGOS%20AND%20RESOURCES/PCGBot_1.png")
                    # await ctx.send(embed=embedVar)
                    # await battle_msg.delete(delay=2)
                    # await asyncio.sleep(2)
                    # battle_msg = await private_channel.send(embed=embedVar)


                    await battle_config.set_boss_win(battle_config.player1, battle_config.player2_card)
                    if battle_config.is_co_op_mode:
                        await battle_config.set_boss_win(battle_config.player1, battle_config.player2_card, battle_config.player3)
                    battle_config.continue_fighting = False
                
            if battle_config.is_explore_game_mode:
                total_complete = True
                battle_config.player1_card.stats_handler(battle_config, battle_config.player1, total_complete)
                await explore_win(battle_config, battle_msg, private_channel, user1)

            if battle_config.is_raid_game_mode:
                total_complete = True
                battle_config.player1_card.stats_handler(battle_config, battle_config.player1, total_complete)
                await raid_win(battle_config, battle_msg, private_channel, user1)

            if battle_config.is_scenario_game_mode:
                await scenario_win(battle_config, battle_msg, private_channel, user1)
                return

            if battle_config.is_abyss_game_mode:
                await abyss_win(battle_config, battle_msg, private_channel, user1)
        else:
            return


async def explore_win(battle_config, battle_msg, private_channel, user1):
    if battle_config.is_explore_game_mode:
        explore_response =  await battle_config.explore_embed(user1, battle_config.player1, battle_config.player1_card, battle_config.player2_card)
        await battle_msg.delete(delay=2)
        await asyncio.sleep(2)
        battle_msg = await private_channel.send(embed=explore_response)
        return True
    else:
        return False


async def raid_win(battle_config, battle_msg, private_channel, user1):
    if battle_config.is_raid_game_mode:
        shield_response = battle_config.raid_victory()
        raid_response = await battle_config.pvp_victory_embed(battle_config.player1, battle_config.player1_card, battle_config.player1_arm, battle_config.player1_title, battle_config.player2, battle_config.player2_card)
        await battle_msg.delete(delay=2)
        await asyncio.sleep(2)
        battle_msg = await private_channel.send(embed=raid_response)
        return True
    else:
        return False


async def scenario_win(battle_config, battle_msg, private_channel, user1):
    try:
        if battle_config.is_raid_scenario:
            quest_response = await Quests.quest_check(battle_config.player1, "RAIDS")
        else:
            quest_response = await Quests.quest_check(battle_config.player1, "SCENARIOS")
        if battle_config.is_scenario_game_mode:
            total_complete = False
            if battle_config.current_opponent_number != (battle_config.total_number_of_opponents):
                battle_config.player1_card.stats_handler(battle_config, battle_config.player1, total_complete)
                cardlogger = await crown_utilities.cardlevel(user1, "Tales")

                embedVar = Embed(title=f"VICTORY\nThe game lasted {battle_config.turn_total} rounds.", color=0x1abc9c)
                embedVar.set_footer(text=f"{battle_config.get_previous_moves_embed()}")
                if quest_response:
                    embedVar.add_field(name="**Quest Complete**",
                        value=f"{quest_response}")
                    
                milestone_response = await Quests.milestone_check(battle_config.player1, "SCENARIOS_RUN", 1)

                # Potentially bring this back if you notice milestones not loading properly
                # if milestone_response:
                #     embedVar.add_field(name="🏆 **Milestone**",
                #         value=f"{milestone_response}")

                # Define a list of milestones to check
                milestones = [
                    (battle_config.player1, battle_config.battle_mode, 1, battle_config.selected_universe),
                    (battle_config.player1, battle_config.player1_card.move1_element, battle_config.player1_card.move1_damage_dealt, battle_config.selected_universe),
                    (battle_config.player1, battle_config.player1_card.move2_element, battle_config.player1_card.move2_damage_dealt, battle_config.selected_universe),
                    (battle_config.player1, battle_config.player1_card.move3_element, battle_config.player1_card.move3_damage_dealt, battle_config.selected_universe),
                ]

                # Check milestones and add messages to the embed
                for milestone in milestones:
                    milestone_messages = await Quests.milestone_check(*milestone)
                    if milestone_messages:
                        for message in milestone_messages:
                            embedVar.add_field(name="🏆 Milestone", value=message)
                

                await battle_msg.delete(delay=2)
                await asyncio.sleep(2)
                battle_msg = await private_channel.send(embed=embedVar)
                battle_config.current_opponent_number = battle_config.current_opponent_number + 1
                battle_config.reset_game()
                battle_config.continue_fighting = True
            
            if battle_config.current_opponent_number == (battle_config.total_number_of_opponents):
                battle_config.continue_fighting = False
                battle_config.player1.make_available()
                total_complete = True
                battle_config.player1_card.stats_handler(battle_config, battle_config.player1, total_complete)

                response = await scenario_drop(battle_config.player1, battle_config.scenario_data, battle_config.difficulty)

                save_scen = battle_config.player1.save_scenario(battle_config.scenario_data['TITLE'])
                unlock_message = battle_config.get_unlocked_scenario_text()
                embedVar = Embed(title=f"Scenario Cleared!\nThe game lasted {battle_config.turn_total} rounds.",description=textwrap.dedent(f"""
                Good luck on your next adventure!

                {save_scen}
                {unlock_message}
                """),color=0xe91e63)
                embedVar.set_footer(text=f"{battle_config.get_previous_moves_embed()}")
                exp = (len(battle_config.list_of_opponents_by_name) * 100) * battle_config._ai_opponent_card_lvl
                await crown_utilities.cardlevel(user1, "Scenario", exp)

                # milestone_response = await Quests.milestone_check(battle_config.player1, "SCENARIOS_COMPLETED", 1)
                # Define a list of milestones to check
                milestones = [
                    (battle_config.player1, battle_config.battle_mode, 1, battle_config.selected_universe),
                    (battle_config.player1, battle_config.player1_card.move1_element, battle_config.player1_card.move1_damage_dealt, battle_config.selected_universe),
                    (battle_config.player1, battle_config.player1_card.move2_element, battle_config.player1_card.move2_damage_dealt, battle_config.selected_universe),
                    (battle_config.player1, battle_config.player1_card.move3_element, battle_config.player1_card.move3_damage_dealt, battle_config.selected_universe),
                    (battle_config.player1, "SCENARIOS_COMPLETED", 1, battle_config.selected_universe)
                ]

                # Check milestones and add messages to the embed
                for milestone in milestones:
                    milestone_messages = await Quests.milestone_check(*milestone)
                    if milestone_messages:
                        for message in milestone_messages:
                            embedVar.add_field(name="🏆 Milestone", value=message)

                if quest_response:
                    embedVar.add_field(name="**Quest Complete**",
                        value=f"{quest_response}")

                embedVar.set_author(name=f"{battle_config.player2_card.name} lost!")

                embedVar.add_field(
                name=f"Scenario Reward",
                value=f"{response}")

                await private_channel.send(embed=embedVar)

            return True
        else:
            return False
    except Exception as ex:
        custom_logging.debug(ex)
        return


async def abyss_win(battle_config, battle_msg, private_channel, user1):
    try:
        if battle_config.is_abyss_game_mode:
            total_complete = False
            if battle_config.current_opponent_number != (battle_config.total_number_of_opponents):
                battle_config.player1_card.stats_handler(battle_config, battle_config.player1, total_complete)
                embedVar = Embed(title=f"VICTORY\nThe game lasted {battle_config.turn_total} rounds.",description=textwrap.dedent(f"""
                {battle_config.get_previous_moves_embed()}
                
                """),color=0x1abc9c)

                embedVar.set_author(name=f"{battle_config.player2_card.name} lost!")
                

                await battle_msg.delete(delay=2)
                await asyncio.sleep(2)
                battle_msg = await private_channel.send(embed=embedVar)
                battle_config.reset_game()
                battle_config.current_opponent_number = battle_config.current_opponent_number + 1
                battle_config.continue_fighting = True
            
            if battle_config.current_opponent_number == (battle_config.total_number_of_opponents):
                total_complete = True
                battle_config.player1_card.stats_handler(battle_config, battle_config.player1, total_complete)
                await battle_config.save_abyss_win(user1, battle_config.player1, battle_config.player1_card)
                abyss_message = await abyss_level_up_message(battle_config.player1.did, battle_config.abyss_floor, battle_config.player2_card.name, battle_config.player2_title.name, battle_config.player2_arm.name)
                abyss_drop_message = "\n".join(abyss_message['DROP_MESSAGE'])
                prestige = battle_config.player1.prestige
                aicon = ":new_moon:"
                if prestige == 1:
                    aicon = ":waxing_crescent_moon:"
                elif prestige == 2:
                    aicon = ":first_quarter_moon:"
                elif prestige == 3:
                    aicon = ":waxing_gibbous_moon:"
                elif prestige == 4:
                    aicon = ":full_moon:"
                elif prestige == 5:
                    aicon = ":waning_gibbous_moon:"
                elif prestige == 6:
                    aicon = ":last_quarter_moon:"
                elif prestige == 7:
                    aicon = ":waning_crescent_moon:"
                elif prestige == 8:
                    aicon = ":crescent_moon:"
                elif prestige == 9:
                    aicon = ":crown:"
                elif prestige >= 10:
                    aicon = ":japanese_ogre:"
                prestige_message = "Conquer the **Abyss** to unlock **Abyssal Rewards** and **New Game Modes.**"
                if battle_config.player1.prestige > 0:
                    prestige_message = f"{aicon} | Prestige Activated! Conquer the **Abyss** to unlock **Abyssal Rewards** and earn another **/exchange**"
                embedVar = Embed(title=f"🌑 Floor **{battle_config.abyss_floor}** Cleared\nThe game lasted {battle_config.turn_total} rounds.",description=textwrap.dedent(f"""
                {prestige_message}
                
                🎊**Abyss Floor Unlocks**
                **{max(0, (3 - (3 * battle_config.player1.prestige))) if max(0, (3 - (3 * battle_config.player1.prestige))) > 0 else "Prestige Unlocked"}** - *PvP and Guilds*
                **{max(0, (10 - (10 * battle_config.player1.prestige))) if max(0, (10 - (10 * battle_config.player1.prestige))) > 0 else "Prestige Unlocked"}** - *Trading*
                **{max(0, (15 - (15 * battle_config.player1.prestige))) if max(0, (15 - (15 * battle_config.player1.prestige))) > 0 else "Prestige Unlocked"}** - *Associations and Raids*
                **{max(0, (20 - (20 * battle_config.player1.prestige))) if max(0, (20 - (20 * battle_config.player1.prestige))) > 0 else "Prestige Unlocked"}** - *Gifting*
                **{max(0, (25 - (25 * battle_config.player1.prestige))) if max(0, (25 - (25 * battle_config.player1.prestige))) > 0 else "Prestige Unlocked"}** - *Explore Mode*
                **{max(0, (30 - (30 * battle_config.player1.prestige))) if max(0, (30 - (30 * battle_config.player1.prestige))) > 0 else "Prestige Unlocked"}** - *Marriage*
                **{max(0, (40 - (40 * battle_config.player1.prestige))) if max(0, (40 - (40 * battle_config.player1.prestige))) > 0 else "Prestige Unlocked"}** - *Dungeons*
                **{max(0, (50 - (50 * battle_config.player1.prestige))) if max(0, (50 - (50 * battle_config.player1.prestige))) > 0 else "Prestige Unlocked"}** - *Bosses*
                **{max(0, 100 - (10 * battle_config.player1.prestige)) if max(0, 100 - (10 * battle_config.player1.prestige)) > 0 else "Prestige Unlocked"}** - *Boss Soul Exchange*
                """),color=0xe91e63)

                embedVar.set_author(name=f"{battle_config.player2_card.name} lost!")
                embedVar.set_footer(text=f"Traverse 🌑 The Abyss in /solo to unlock new game modes and features!")
                floor_list = [0,2,3,6,7,8,9,10,20,25,40,60,100]
                if battle_config.abyss_floor in floor_list:
                    embedVar.add_field(
                    name=f"Abyssal Unlock",
                    value=f"{abyss_message['MESSAGE']}")
                embedVar.add_field(
                name=f"Abyssal Rewards",
                value=f"{abyss_drop_message}")

                battle_msg = await private_channel.send(embed=embedVar)
                battle_config.continue_fighting = False
            return True
        else:
            return False
    except Exception as ex:
        custom_logging.debug(ex)
        return


async def movecrest(universe, guild):
    guild_name = guild
    universe_name = universe
    guild_query = {'GNAME': guild_name}
    guild_info = db.queryGuildAlt(guild_query)
    if guild_info:
        alt_query = {'FDID': guild_info['FDID']}
        crest_list = guild_info['CREST']
        pull_query = {'$pull': {'CREST': universe_name}}
        pull = db.updateManyGuild(pull_query)
        update_query = {'$push': {'CREST': universe_name}}
        update = db.updateGuild(alt_query, update_query)
        universe_guild = db.updateUniverse({'TITLE': universe_name}, {'$set': {'GUILD': guild_name}})
    else:
        print("Association not found: Crest")


def setup(bot):
    GameState(bot)






