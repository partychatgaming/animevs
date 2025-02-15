import db
import time
from logger import loggy
from decouple import config
import unique_traits as ut
now = time.asctime()
from interactions import listen, slash_command, SlashCommandOption, OptionType, SlashCommandChoice, cooldown, Buckets, Embed, Extension
import crown_utilities

class Options(Extension):
    def __init__(self,bot):
        self.bot = bot

        @listen()
        async def on_ready(self):
            # self.bot.logger.info(f"Help cog loaded at {now}")
            loggy.info('Options Cog is ready')
        
        async def cog_check(self, ctx):
            return await self.bot.validate_user(ctx)
        
        @slash_command(name="autosave", description="Toggles Autosave on Battle Start.", scopes=crown_utilities.guild_ids)
        async def autosave(ctx):
            try:
                player = db.queryUser({"DID": str(ctx.author.id)})
                autosave_on = player.get("AUTOSAVE", False)

                if not autosave_on:
                    db.updateUserNoFilter({"DID": str(ctx.author.id)}, {"$set": {"AUTOSAVE": True}})
                    embed = Embed(title="Autosave Activated", description="You can still save your progress with the save button in battle.")
                    await ctx.send(embed=embed)
                else:
                    db.updateUserNoFilter({"DID": str(ctx.author.id)}, {"$set": {"AUTOSAVE": False}})
                    embed = Embed(title="Autosave Deactivated", description="You can still save your progress with the save button in battle.")
                    await ctx.send(embed=embed)
            except Exception as ex:
                loggy.error(f"Error in Autosave command: {ex}")
                # trace = []
                # tb = ex.__traceback__
                # while tb is not None:
                #       trace.append({
                #          "filename": tb.tb_frame.f_code.co_filename,
                #          "name": tb.tb_frame.f_code.co_name,
                #          "lineno": tb.tb_lineno
                #       })
                #       tb = tb.tb_next
                # print(str({
                #       'type': type(ex).__name__,
                #       'message': str(ex),
                #       'trace': trace
                # }))
                await ctx.send("There's an issue with your Autosave. Seek support in the Anime 🆚+ support server", ephemeral=True)
        
        @slash_command(name="battleview", description="Toggles Opponent Stats in Battle", scopes=crown_utilities.guild_ids)
        async def battleview(ctx):
            try:
                player = db.queryUser({"DID": str(ctx.author.id)})
                opponent_info = player.get("RIFT", 0)

                if not opponent_info:
                    db.updateUserNoFilter({"DID": str(ctx.author.id)}, {"$set": {"RIFT": 1}})
                    embed = Embed(title="Battle View Deactivated", description="You can still view your opponent stats on the Card")
                    await ctx.send(embed=embed)
                else:
                    db.updateUserNoFilter({"DID": str(ctx.author.id)}, {"$set": {"RIFT": 0}})
                    embed = Embed(title="Battle View Activated", description="You can now see extra details in the battle header.")
                    await ctx.send(embed=embed)
            except Exception as ex:
                loggy.error(f"Error in Battle View command: {ex}")
                # trace = []
                # tb = ex.__traceback__
                # while tb is not None:
                #       trace.append({
                #          "filename": tb.tb_frame.f_code.co_filename,
                #          "name": tb.tb_frame.f_code.co_name,
                #          "lineno": tb.tb_lineno
                #       })
                #       tb = tb.tb_next
                # print(str({
                #       'type': type(ex).__name__,
                #       'message': str(ex),
                #       'trace': trace
                # }))
                await ctx.send("There's an issue with your Battle View . Seek support in the Anime 🆚+ support server", ephemeral=True)



        @slash_command(name="difficulty", description="Change the difficulty setting of Anime VS+",
                            options=[
                                SlashCommandOption(
                                    name="mode",
                                    description="Difficulty Level",
                                    type=OptionType.STRING,
                                    required=True,
                                    choices=[
                                        SlashCommandChoice(
                                            name="⚙️ Normal",
                                            value="NORMAL"
                                        ),
                                        SlashCommandChoice(
                                            name="⚙️ Easy",
                                            value="EASY"
                                        ),
                                        SlashCommandChoice(
                                            name="⚙️ Hard",
                                            value="HARD"
                                        )
                                    ]
                                )
                            ]
                ,scopes=crown_utilities.guild_ids)
        @cooldown(Buckets.USER, 1, 10)
        async def difficulty(ctx, mode):
            try:
                query = {'DID': str(ctx.author.id)}
                player = db.queryUser(query)
                update_query = {'$set': {'DIFFICULTY': mode}}
                response = db.updateUserNoFilter(query, update_query)
                if response:
                    embed = Embed(title="Difficulty Updated", description=f"{ctx.author.mention} has been updated to ⚙️ **{mode.lower()}** mode.", color=0x00ff00)
                    await ctx.send(embed=embed)
            except Exception as ex:
                loggy.error(f"Error in difficulty command: {ex}")
                # trace = []
                # tb = ex.__traceback__
                # while tb is not None:
                #       trace.append({
                #          "filename": tb.tb_frame.f_code.co_filename,
                #          "name": tb.tb_frame.f_code.co_name,
                #          "lineno": tb.tb_lineno
                #       })
                #       tb = tb.tb_next
                # print(str({
                #       'type': type(ex).__name__,
                #       'message': str(ex),
                #       'trace': trace
                # }))
                embed = Embed(title="Difficulty Update Failed", description=f"{ctx.author.mention} has failed to update to ⚙️ **{mode.lower()}** mode.", color=0xff0000)
                await ctx.send(embed=embed)
        
        
        @slash_command(name="battlehistory", description="How much battle history do you want to see during battle? 2 - 6", options=[
        SlashCommandOption(name="history", 
                            description="How much battle history do you want to see during battle? 2 - 6", 
                            type=OptionType.INTEGER, 
                            required=True,
                            choices=[
                                SlashCommandChoice(name="2 Messages", value=2),
                                SlashCommandChoice(name="3 Messages", value=3),
                                SlashCommandChoice(name="4 Messages", value=4),
                                SlashCommandChoice(name="5 Messages", value=5),
                                SlashCommandChoice(name="6 Messages", value=6)
                            ]
        )], scopes=crown_utilities.guild_ids)
        @cooldown(Buckets.USER, 1, 10)
        async def battlehistory(ctx, history: int):
            try:
                user_query = {"DID": str(ctx.author.id)}
                update_query = {"$set": {"BATTLE_HISTORY": history}}
                response = db.updateUserNoFilter(user_query, update_query)
                await ctx.send(f":bookmark_tabs:  | You will now see up to {str(history)} history messages during battle.")
            except Exception as e:
                await ctx.send(e)
            
