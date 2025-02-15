import db
import crown_utilities
import textwrap
from interactions import Embed, AutocompleteContext


class Family:
    def __init__(self, head, partner, kids, bank, house, estates, transactions, summon, universe, timestamp, HDID):
        self.head = head
        self.partner = partner
        self.kids = kids
        self.bank = bank
        self.house = house
        self.estates = estates
        self.transactions = transactions
        self.summon = summon
        self.universe = universe
        self.timestamp = timestamp
        self.HDID = HDID

        self.members = []
        self.members.extend([self.head, self.partner, self.kids])
        self.family_name = self.head

        self.transactions_embed = ""

        self.is_head = False
        self.is_partner = False
        self.is_kid = False

        self.summon_data = db.querySummon({'summon': self.summon})
        self.summon_name = self.summon_data['name']
        self.summon
        self.stars = ""
        self.rank = ""
        self.gem_investment_percentage = ""

        self.guild_buff_on_status_emoji = "🔴" if not self.guild_buff_on else "🟢"

        self.guild_mission_message = "Guild Mission is not active."
        self.guild_war_message = "Guild War is not active."
        self.embed_list = []

        self._populate_names_and_format()
        self._format_transactions()
        self._calculate_rank()

    def _populate_names_and_format(self):
        user_data = {user['DID']: user['DISNAME'] for user in db.queryUsers({'DID': {'$in': self.members + self.officers + self.captains + [self.owner]}})}
        
        for index, member_id in enumerate(self.members):
            member_name = user_data[member_id]
            
            if member_id in self.officers:
                formatted_name = f"🅾️ [{index}] **{member_name}**"
                self.formatted_list_of_officers.append(formatted_name)
                self.officer_names.append(member_name)
            elif member_id in self.captains:
                formatted_name = f"🇨 [{index}] **{member_name}**"
                self.formatted_list_of_captains.append(formatted_name)
                self.captain_names.append(member_name)
            elif member_id == self.owner:
                formatted_name = f"👑 [{index}] **{member_name}**"
                self.formatted_owner = formatted_name
                self.owner_name = member_name
            else:
                formatted_name = f"\n🔰 [{index}] **{member_name}**"
                self.formatted_list_of_members.append(formatted_name)
                self.member_names.append(member_name)

        self.members_list_joined = "".join(self.formatted_list_of_members)
        self.captains_list_joined = ", ".join(self.formatted_list_of_captains)
        self.officers_list_joined = ", ".join(self.formatted_list_of_officers)


    def _format_transactions(self):
        if self.transactions:
            transactions_len = len(self.transactions)
            if transactions_len >= 10:
                self.transactions = self.transactions[-10:]
            self.transactions_embed = "\n".join(self.transactions)


    def get_user_role(self, user_disname):
        if user_disname == self.owner_name:
            self.is_owner = True
        elif user_disname in self.officer_names:
            self.is_officer = True
        elif user_disname in self.captain_names:
            self.is_captain = True
        elif user_disname in self.member_names:
            self.is_member = True
        else:
            return None


    def _calculate_rank(self):
        balance = self.bank  # Assuming the bank attribute represents the guild's balance

        if balance >= 100000000000:
            self.stars = "✨✨✨✨✨"
            self.rank = "S Rank Guild"
            self.gem_investment_percentage = "10%"
        elif balance >= 1000000000:
            self.stars = "⭐⭐⭐⭐"
            self.rank = "A Rank Guild"
            self.gem_investment_percentage = "6%"
        elif balance >= 100000000:
            self.stars = "⭐⭐⭐"
            self.rank = "B Rank Guild"
            self.gem_investment_percentage = "6%"
        elif balance >= 1000000:
            self.stars = "⭐⭐"
            self.rank = "C Rank Guild"
            self.gem_investment_percentage = "4%"
        else:
            self.stars = "⭐"
            self.rank = "D Rank Guild"
            self.gem_investment_percentage = "2%"


    def generate_embed(self, embed_type):
            if embed_type == "first_page":
                return self._generate_first_page()
            elif embed_type == "membership":
                return self._generate_membership_page()
            elif embed_type == "guild_mission":
                return self._generate_guild_mission_embed()
            elif embed_type == "war":
                return self._generate_war_embed()
            elif embed_type == "activity":
                return self._generate_activity_page()
            elif embed_type == "explanations":
                return self._generate_guild_explanations()
            else:
                raise ValueError("Invalid embed type")

    def _generate_first_page(self):
        return Embed(title=f"{self.guild_display_name}", description=textwrap.dedent(f"""
        {self.stars}
        **{self.rank}**
        
        👑 **Owner** 
        {self.formatted_owner}
        
        🅾️ **Officers**
        {self.officers_list_joined}
        
        🇨 **Captains**
        {self.captains_list_joined}
        
        **Guild Membership Count** 
        {self.member_count}
                        
        **Guild Buff**
        {self._get_guild_buff_message()}
        
        **Active Buff**
        {self._get_active_guild_buff_message()}
        
        **Bank** 
        {self._get_icon()} {'{:,}'.format(self.bank)}

        **Gem Investment**
        As a {self.stars} {self.rank}, members investing into this guild using the /donate command will yield a {self.gem_investment_percentage} return on your investment in the form of 💎 gems across all universes they've explored.
        """), color=0x7289da)

    def _generate_membership_page(self):
        return Embed(title=f"Members", description=textwrap.dedent(f"""
        🔰 **Members**\n{self.members_list_joined}
        """), color=0x7289da)

    def _generate_guild_mission_embed(self):
        return Embed(title=f"Guild Missions", description=textwrap.dedent(f"""
        **Guild Mission** *Coming Soon*
        {self._get_guild_mission_message()}
        **Completed Guild Missions**
        {str(self.completed_missions)}
        """), color=0x7289da)

    def _generate_war_embed(self):
        return Embed(title=f"Guild War", description=textwrap.dedent(f"""
        **War** *Coming Soon*
        {self._get_war_message()}
        **Wars Won**
        {str(self.wins)}
        """), color=0x7289da)

    def _generate_activity_page(self):
        return Embed(title="Recent Guild Activity", description=textwrap.dedent(f"""
        {self.transactions_embed}
        """), color=0x7289da)

    def _generate_guild_explanations(self):
        return Embed(title=f"Information", description=textwrap.dedent(f"""
        **Buff Explanations**
        - **Quest Buff**: Start Quest from the required fight in the Tale, not for dungeons
        - **Level Buff**: Each fight will grant you a level up
        - **Stat Buff**: Add 50 ATK & DEF, 30 AP, and 100 HLT
        - **Rift Buff**: Rifts will always be available
        - **Rematch Buff**: Unlimited Rematches
        
        **Guild Position Explanations**
        - **Owner**:  All operations */guildoperations*
        - **Officer**:  Can Add members, Delete members, Pay members, Buy, Swap, and Toggle Buffs
        - **Captain**:  Can Toggly Buffs, Pay members
        - **Member**:  No operations
        """), color=0x7289da)

    def _get_guild_buff_message(self):
        # Implement logic to get guild buff message
        return "Guild buff message"

    def _get_active_guild_buff_message(self):
        if not self.guild_buff_available:
            return "No Active Guild Buff"
        
        if not self.active_guild_buff:
            return "No Active Guild Buff"

        for buff in self.guild_buffs:
            if buff['TYPE'] == self.active_guild_buff:
                active_guild_buff_use_cases = str(buff['USES'])
                gbon_status = "🟢" if self.guild_buff_on else "🔴"
                return f"{gbon_status} {self.active_guild_buff} Buff: {active_guild_buff_use_cases} uses left!"

        return "No Active Guild Buff"  # Fallback if no matching buff is found
    
    def _get_icon(self):
        # Implement logic to get icon
        return "🏆"

    def _get_guild_mission_message(self):
        # Implement logic to get guild mission message
        return "Guild mission message"

    def _get_war_message(self):
        # Implement logic to get war message
        return "War message"

    async def send_guild_info(self):
        embed_types = ["first_page", "membership", "guild_mission", "war", "activity", "explanations"]
        
        for embed_type in embed_types:
            embed = self.generate_embed(embed_type)
            self.embed_list.append(embed)
        
        return self.embed_list


    def get_user_buttons(self, user_id):
        if user_id == self.owner or user_id in self.officers:
            return ["Buff Toggle", "Buff Swap", "Buff Shop"]
        elif user_id in self.captains:
            return ["Buff Toggle"]
        else:
            return []


