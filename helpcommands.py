'''
Help functions

'''


# @help.command()
# async def test(ctx):
#    em = Embed(title = "test", description = "test", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#test <test>")

#    await ctx.send(embed = em)

# @help.command()
# async def Exhibitions(ctx):
#    em = Embed(title = "Exhibitions", description = "Exhibitions are 1v1 Bounty matches between players organized by Admins, winner gets tournament wins", color = ctx.author.color)

#    em.add_field(name = "**Commands**\n*use #help <command>*", value = "e,einvite")

#    await ctx.send(embed = em)

# @help.command()
# async def e(ctx):
#    em = Embed(title = "e", description = "ADMIN: opens up an exhibition lobby", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#e")

#    await ctx.send(embed = em)

# @help.command()
# async def einvite(ctx):
#    em = Embed(title = "einvite", description = "invites users to join exhibition", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#einvite <user>")

#    await ctx.send(embed = em)

# @help.command()
# async def KingsGambit(ctx):
#    em = Embed(title = "Kings Gambit", description = "Kings Gambit's are king of the hill style matches where the king decides the rules organized by Admins, winner gets tournament wins", color = ctx.author.color)

#    em.add_field(name = "**Commands**\n*use #help <command>*", value = "jkg,kg,skg")

#    await ctx.send(embed = em)

# @help.command()
# async def jkg(ctx):
#    em = Embed(title = "jkg", description = "Joins Open Kings Gambit Lobby", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#jkg <user>")

#    await ctx.send(embed = em)

# @help.command()
# async def kg(ctx):
#    em = Embed(title = "kg", description = "ADMIN: Opens Kings Gambit Lobby", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#kg")

#    await ctx.send(embed = em)

# @help.command()
# async def skg(ctx):
#    em = Embed(title = "skg", description = "Scores Kings Gambit and rotates the hill", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#skg <user>")

#    await ctx.send(embed = em)

# @help.command()
# async def GodsOfCod(ctx):
#    em = Embed(title = "Gods Of COD", description = "Gods Of COD are cash prize tournaments where teams compete over a series of matches organized by Admins, winner gets tournament wins", color = ctx.author.color)

#    em.add_field(name = "**Commands**\n*use #help <command>*", value = "cgoc,dgoc,egoc,goc,gocarchive,goci,sgoc,goclk,gocrules,rgoc")

#    await ctx.send(embed = em)

# @help.command()
# async def cgoc(ctx):
#    em = Embed(title = "cgoc", description = "ADMIN: Create open Gods of Cod Session", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#cgoc")

#    await ctx.send(embed = em)

# @help.command()
# async def dgoc(ctx):
#    em = Embed(title = "dgoc", description = "ADMIN: Deletes GOC tournament from database", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#dgoc")

#    await ctx.send(embed = em)

# @help.command()
# async def egoc(ctx):
#    em = Embed(title = "egoc", description = "ADMIN: Ends Gods Of COD tournament", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#egoc")

#    await ctx.send(embed = em)

# @help.command()
# async def goc(ctx):
#    em = Embed(title = "goc", description = "Create Gods of Cod Tournament", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#goc <title> <gametype> <gametypeFLAG> <reward> <ImageUrl>")

#    await ctx.send(embed = em)

# @help.command()
# async def goci(ctx):
#    em = Embed(title = "goci", description = "Invite # of users to Gods of Cod Session", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#goci <user>...")

#    await ctx.send(embed = em)

# @help.command()
# async def sgoc(ctx):
#    em = Embed(title = "sgoc", description = "End Registration and Start Gods Of Cod Tournament", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#sgoc")

#    await ctx.send(embed = em)

# @help.command()
# async def gocarchive(ctx):
#    em = Embed(title = "gocarchive", description = "Lookup past Gods Of Cod Tournaments", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#gocarchive <title>")

#    await ctx.send(embed = em)

# @help.command()
# async def goclk(ctx):
#    em = Embed(title = "goclk", description = "Lookup Current  Gods Of Cod Tournament Information", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#goclk")

#    await ctx.send(embed = em)

# @help.command()
# async def gocrules(ctx):
#    em = Embed(title = "gorules", description = "Lookup Current Gods Of Cod Tournament Rules", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#gorules")

#    await ctx.send(embed = em)

# @help.command()
# async def rgoc(ctx):
#    em = Embed(title = "rgoc", description = "Register Player and Player Team for Gods Of Cod Tournament", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#goclk")

#    await ctx.send(embed = em)

# @help.command()
# async def att(ctx):
#    em = Embed(title = "att", description = "Add Teammate by username", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#att <teamname> <user>")

#    await ctx.send(embed = em)

# @help.command()
# async def cteam(ctx):
#    em = Embed(title = "cteam", description = "Create a team ", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#cteam <game> <teamname>")

#    await ctx.send(embed = em)

# @help.command()
# async def dt(ctx):
#    em = Embed(title = "dt", description = "TEAMOWNER: delete team from database", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#dt <teamname>")

#    await ctx.send(embed = em)

# @help.command()
# async def dtm(ctx):
#    em = Embed(title = "dtm", description = "TEAMOWNER: delete teammate from team", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#dtm <user>")

#    await ctx.send(embed = em)

# @help.command()
# async def lteam(ctx):
#    em = Embed(title = "lteam", description = "Leave current team", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#lteam")

#    await ctx.send(embed = em)


# @help.command()
# async def bc(ctx):
#    em = Embed(title = "bc", description = "Buys Card from Flex Shop:tm:", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#bc <cardname>")

#    await ctx.send(embed = em)


# @help.command()
# async def bt(ctx):
#    em = Embed(title = "bt", description = "Buys Title from Flex Shop :tm:", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#bt <titlename>")

#    await ctx.send(embed = em)


# @help.command()
# async def shop(ctx):
#    em = Embed(title = "shop", description = "Opens up Flex Shop:tm:", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#shop")

#    await ctx.send(embed = em)

# @help.command()
# async def vc(ctx):
#    em = Embed(title = "vc", description = "View any card by cardname", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#vc <cardname>")

#    await ctx.send(embed = em)

# @help.command()
# async def cl(ctx):
#    em = Embed(title = "cl", description = "Check if a User is playing in a session", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#cl <user>")

#    await ctx.send(embed = em)


# @help.command()
# async def c1v1(ctx):
#    em = Embed(title = "c1v1", description = "Create a 1v1 Lobby ", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#c1v1 <ranktype>")

#    await ctx.send(embed = em)


# @help.command()
# async def c2v2(ctx):
#    em = Embed(title = "c2v2", description = "Create a 2v2 Duo or Team Scrimm Lobby ", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#c2v2 <ranktype> <user1>")

#    await ctx.send(embed = em)


# @help.command()
# async def c3v3(ctx):
#    em = Embed(title = "c3v3", description = "Create a 3v3 Team Scrimm Lobby ", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#c3v3 <ranktype> <user1> <user2>")

#    await ctx.send(embed = em)


# @help.command()
# async def c4v4(ctx):
#    em = Embed(title = "c4v4", description = "Create a 4v4 Team Scrimm Lobby ", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#c4v4 <ranktype> <user1> <user2> <user3>")

#    await ctx.send(embed = em)


# @help.command()
# async def c5v5(ctx):
#    em = Embed(title = "c5v5", description = "Create a 5v5 Team Scrimm Lobby ", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#c5v5 <ranktype> <user1> <user2> <user3> <user4>")

#    await ctx.send(embed = em)


# @help.command()
# async def el(ctx):
#    em = Embed(title = "el", description = "Saves then ends the owned lobby", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#el")

#    await ctx.send(embed = em)


# @help.command()
# async def dal(ctx):
#    em = Embed(title = "dal", description = "ADMIN:Delete All Lobbies from database", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#dal")

#    await ctx.send(embed = em)


# @help.command()
# async def dl(ctx):
#    em = Embed(title = "dl", description = "Delete Lobby without recording data\n*Useful if you make an error", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#dl")

#    await ctx.send(embed = em)


# @help.command()
# async def jl(ctx):
#    em = Embed(title = "jl", description = "Join Lobby /Join Scrimm\nJoin an open lobby with up to 4 teammates", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#jl <user> ...")

#    await ctx.send(embed = em)


# @help.command()
# async def score(ctx):
#    em = Embed(title = "score", description = "Score a team during any lobby", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#score <user>")

#    await ctx.send(embed = em)


# @help.command()
# async def lg(ctx):
#    em = Embed(title = "lg", description = "ADMIN: pulls teams up to 5 into a lobby", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#sg <user> ...")

#    await ctx.send(embed = em)


# @help.command()
# async def lo(ctx):
#    em = Embed(title = "lo", description = "Checks if user is a Lobby Owner", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#lo <user>")

#    await ctx.send(embed = em)

# @help.command()
# async def ag(ctx):
#    em = Embed(title = "ag", description = "Add game to list", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#ag <gamename>")

#    await ctx.send(embed = em)


# @help.command()
# async def flex(ctx):
#    em = Embed(title = "flex", description = "Display Custom Player Card", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#flex")

#    await ctx.send(embed = em)

# @help.command()
# async def lk(ctx):
#    em = Embed(title = "lk", description = "Lookup Player Data", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#lk <username>")

#    await ctx.send(embed = em)

# @help.command()
# async def lkg(ctx):
#    em = Embed(title = "lkg", description = "Lookup Games supported by bot", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#lkg")

#    await ctx.send(embed = em)

# @help.command()
# async def lkt(ctx):
#    em = Embed(title = "lkt", description = "Lookup Team Page by Teamname", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#lkt <teamname>")

#    await ctx.send(embed = em)

# @help.command()
# async def uc(ctx):
#    em = Embed(title = "uc", description = "Update Player Card", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#uc <cardname>")

#    await ctx.send(embed = em)

# @help.command()
# async def uign(ctx):
#    em = Embed(title = "uign", description = "Update Player In Game Name for game", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#uign <game> <newIGN>")

#    await ctx.send(embed = em)

# @help.command()
# async def ut(ctx):
#    em = Embed(title = "ut", description = "Update Player Title", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#ut <titlename>")

#    await ctx.send(embed = em)

# @help.command()
# async def vault(ctx):
#    em = Embed(title = "vault", description = "Opens Player Vault", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#vault")

#    await ctx.send(embed = em)


# @help.command()
# async def challenge(ctx):
#    em = Embed(title = "challenge", description = "Challenge User To 1v1 Lobby", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#challenge <user>")

#    await ctx.send(embed = em)


# @help.command()
# async def d(ctx):
#    em = Embed(title = "d", description = "Delete All User and Vault Data", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#d <user> IWANTTODELETEMYACCOUNT")

#    await ctx.send(embed = em)


# @help.command()
# async def r(ctx):
#    em = Embed(title = "r", description = "Register for access to Bot", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#r")

#    await ctx.send(embed = em)


# @help.command()
# async def iby(ctx):
#    em = Embed(title = "iby", description = "Shows how many matches you've won against another user", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#iby <user>")

#    await ctx.send(embed = em)

# @help.command()
# async def ml(ctx):
#    em = Embed(title = "ml", description = "Shows the current lobbby YOU are in", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#ml")

#    await ctx.send(embed = em)

# @help.command()
# async def senpai(ctx):
#    em = Embed(title = "senpai", description = "Opens Senpai:tm: Says Tutorial.", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#senpai")

#    await ctx.send(embed = em)

# @help.command()
# async def bootcamp(ctx):
#    em = Embed(title = "bootcamp", description = "Opens up Senpai:tm: Bootcamp Tutorial.", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#bootcamp")

#    await ctx.send(embed = em)


# @help.command()
# async def franchise(ctx):
#    em = Embed(title = "franchise", description = "Open up Senpai:tm: Franchise Tutorial.", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#franchise")

#    await ctx.send(embed = em)


# @help.command()
# async def legend(ctx):
#    em = Embed(title = "legend", description = "Open up Senpai:tm: Legend Tutorial.", color = ctx.author.color)

#    em.add_field(name = "**Syntax**", value = "#legend")

#    await ctx.send(embed = em)

