import crown_utilities
import db
import dataclasses as data
from interactions import listen, slash_command, InteractionContext, OptionType, slash_option, AutocompleteContext, Extension
from logger import loggy

class Explore(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        # print('Explore Cog is ready!')
        loggy.info('Explore Cog is ready')


    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    @slash_command(description="Toggle Explore Mode On/Off or explore a universe")
    @slash_option(
            name="universe",
            description="Type universe you want to explore, or type 'all' to explore all universes",
            opt_type=OptionType.STRING,
            required=False,
            autocomplete=True
    )
    async def explore(self, ctx: InteractionContext, universe=None):
        try:
            player = db.queryUser({"DID": str(ctx.author.id)})
            p = crown_utilities.create_player_from_data(player)
            message = None
            if p.explore == 0:
                db.updateUserNoFilter({'DID': str(p.did)}, {'$set': {'EXPLORE': True}})
                message = f"🌌 | Entering Explore Mode"
            elif p.explore == 1:
                db.updateUserNoFilter({'DID': str(p.did)}, {'$set': {'EXPLORE': False, 'EXPLORE_LOCATION': "NULL"}})
                message = "🚨 | Exiting Explore Mode"

            if universe is not None:
                message = p.set_explore(universe)

            if message is not None:
                await ctx.send(f"{message}")

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


    @slash_command(description="Set Explore Channel")
    async def setexplorechannel(self, ctx: InteractionContext):
        if ctx.author.guild_permissions.administrator:
            guild = ctx.guild
            server_channel = ctx.channel
            server_query = {'GNAME': str(guild), 'EXP_CHANNEL': str(server_channel)}
            try:
                response = db.queryServer({'GNAME': str(guild)})
                if response:
                    update_channel = db.updateServer({'GNAME': str(guild)}, {'$set': {'EXP_CHANNEL': str(server_channel)}})
                    await ctx.send(f"Explore Channel updated to **{server_channel}**")
                    return
                else:
                    update_channel = db.createServer(data.newServer(server_query))
                    await ctx.send("Explore Channel set.")
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
        else:
            await ctx.send("Admin command only.")
            return


    @slash_command(description="Create Default Server Explore Channel")
    async def createexplorechannel(self, ctx: InteractionContext):
        guild = ctx.guild
        categoryname = "Explore"
        channelname = "explore-encounters"
        try:
            if ctx.author.guild_permissions.administrator == True:
                category = discord.utils.get(guild.categories, name=categoryname)
                if category is None: #If there's no category matching with the `name`
                    category = await guild.create_category_channel(categoryname)
                    setchannel = await guild.create_text_channel(channelname, category=category)
                    await ctx.send(f"New **Explore** Category and **{channelname}** Channel Created!")
                    await setchannel.send("**Explore Channel Set**")
                    return setchannel

                else: #Else if it found the categoty
                    setchannel = discord.utils.get(guild.text_channels, name=channelname)
                    if channel is None:
                        setchannel = await guild.create_text_channel(channelname, category=category)
                        await ctx.send(f"New Explore Channel is **{channelname}**")
                        await setchannel.send("**Explore Channel Set**")
                    else:
                        await ctx.send(f"Explore Channel Already Exist **{channelname}**")
                        await setchannel.send(f"{ctx.author.mention} Explore Here")            
                
            # else:
            #     print("Not Admin")
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
    
    @explore.autocomplete("universe")
    async def play_autocomplete(self, ctx: AutocompleteContext):
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
    Explore(bot)
              