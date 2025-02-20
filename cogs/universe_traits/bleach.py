import crown_utilities
import random


character_type = [
    {"NAME": "Sajin Komamura", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Sosuke Aizen", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Grimmjow Jaegerjaquez", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Orihime Inoue", "FIRST_RELEASE": "FULLBRING ACTIVATION", "SECOND_RELEASE": "FULLBRING COMPLETION"},
    {"NAME": "Renji Abarai", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Yoruichi Shihoin", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Yhwach Bach", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Shunsui Kyoraku", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Retsu Unohana", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Jushiro Ukitake", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Rukia Kuchiki", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Genryusai Yamamoto", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Mugetsu", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Kenpachi Zaraki", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Mayuri Kurotsuchi", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Royal Ichigo Kurosaki", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Toshiro Hitsugaya", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Byakuya Kuchiki", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Kaname Tosen", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Ichibe Hyosube", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Kisuke Urahara", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Maki Ichinose", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Uryu Ishida", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Giriko Kutsuzawa", "FIRST_RELEASE": "FULLBRING ACTIVATION", "SECOND_RELEASE": "FULLBRING COMPLETION"},
    {"NAME": "Ulquiorra Cifer", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Shinji Hirako", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Starrk Coyote", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Barragan Louisenbairn", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Yammy Llargo", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Soifon", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Hollow Ichigo", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Gin Ichimaru", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Rangiku Matsumoto", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Kugo Ginjo", "FIRST_RELEASE": "FULLBRING ACTIVATION", "SECOND_RELEASE": "FULLBRING COMPLETION"},
    {"NAME": "Riruka Dokugamine", "FIRST_RELEASE": "FULLBRING ACTIVATION", "SECOND_RELEASE": "FULLBRING COMPLETION"},
    {"NAME": "Grand Fisher", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Yukio Hans Vorarlberna", "FIRST_RELEASE": "FULLBRING ACTIVATION", "SECOND_RELEASE": "FULLBRING COMPLETION"},
    {"NAME": "Nnoitra Gilga", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Ikkaku Madarame", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Yasutora Sado", "FIRST_RELEASE": "FULLBRING ACTIVATION", "SECOND_RELEASE": "FULLBRING COMPLETION"},
    {"NAME": "Isshin Kurosaki", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Vasto Lordes Ichigo", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Moe Shishigawara", "FIRST_RELEASE": "FULLBRING ACTIVATION", "SECOND_RELEASE": "FULLBRING COMPLETION"},
    {"NAME": "Izuru Kira", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Shuhei Hisagi", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Luppi Antenor", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Tier Harribel", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Aaroniero Arruruerie", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Jin Kariya", "FIRST_RELEASE": "FULLBRING ACTIVATION", "SECOND_RELEASE": "FULLBRING COMPLETION"},
    {"NAME": "Szayelaporro Granz", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Shukuro Tsukishima", "FIRST_RELEASE": "FULLBRING ACTIVATION", "SECOND_RELEASE": "FULLBRING COMPLETION"},
    {"NAME": "Neliel Tu Odelschwanck", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Momo Hinamori", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Ichigo Kurosaki", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "White", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Imprisoned Aizen", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Senjumaru Shutara", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Jugram Haschwalth", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "As Nodt", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Liltotto Lamperd", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Cang Du", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Gremmy Thoumeaux", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Hiyori Sarugaki", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Dordonii Alessandro Del Socaccio", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Rudbornn Chelute", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Wonderweiss Margela", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "Royal Byakuya Kuchiki", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Royal Renji Abarai", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Hogyoku Aizen", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Fullbringer Ichigo", "FIRST_RELEASE": "FULLBRING ACTIVATION", "SECOND_RELEASE": "FULLBRING COMPLETION"},
    {"NAME": "Askin Nakk Le Vaar", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Quilge Opie", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "PePe Waccabrada", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Driscoll Berci", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Berenice Gabrielli", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Mask De Masculine", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Giselle Gewelle", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Yumichika Ayasegawa", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Tessai Tsukabishi", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Royal Rukia Kuchiki", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Adult Toshiro Hitsugaya", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Kirio Hikifune", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Oetsu Nimaiya", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Tenjiro Kirinji", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Bambietta Basterbine", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Bazz-B", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Meninas McAllon", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Jerome Guizbatt", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Candice Catnipp", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Nianzol Weizol", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Love Aikawa", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Hanataro Yamada", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Ganju Shiba", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Yachiru Kusajishi", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Zommari Rureaux", "FIRST_RELEASE": "RESURRECCION", "SECOND_RELEASE": "SEGUNDA ETAPA"},
    {"NAME": "First Kenpachi Retsu Unohana", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Almighty Yhwach Bach", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Successor Uryu Ishida", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Ryuken Ishida", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Unleashed Kenpachi Zaraki", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Hybrid Sajin Komamura", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Pernida Parnkgjas", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "BG9", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Gerard Valkyrie", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Robert Accutrone", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "NaNaNa Najahkoop", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Hachigen Ushoda", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Lisa Yadomaru", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Mashiro Kuna", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Rose Otoribashi", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Marechiyo Omaeda", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Tetsuzaemon Iba", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Lille Barro", "FIRST_RELEASE": "VOLLSTANDIG", "SECOND_RELEASE": "SHRIFT"},
    {"NAME": "Kensei Muguruma", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Jackie Tristan", "FIRST_RELEASE": "FULLBRING ACTIVATION", "SECOND_RELEASE": "FULLBRING COMPLETION"},
    {"NAME": "Nanao Ise", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
    {"NAME": "Isane Kotetsu", "FIRST_RELEASE": "SHIKAI", "SECOND_RELEASE": "BANKAI"},
]

def first_release(player_card, battle_config, player_title):
    if player_card.universe == "Bleach":  # Bleach Trait
        # fortitude or luck is based on health
        fortitude = 0.0
        low = player_card.health - (player_card.health * .75)
        high = player_card.health - (player_card.health * .66)
        fortitude = round(random.randint(int(low), int(high)))
        # Resolve Scaling
        resolve_health = round(fortitude + (.5 * player_card.resolve_value))
        resolve_attack_value = round(
            (.30 * player_card.defense) * (player_card.resolve_value / (.50 * player_card.defense)))
        resolve_defense_value = round(
            (.30 * player_card.defense) * (player_card.resolve_value / (.50 * player_card.defense)))

        title_message = ""
        message = ""
        if player_title.singularity_effect:
            resolve_health, resolve_attack_value, resolve_defense_value, title_message = player_title.singularity_handler(resolve_health, resolve_attack_value, resolve_defense_value)

        for release in character_type:
            if release["NAME"] == player_card.name:
                if release["FIRST_RELEASE"] == "SHIKAI":
                    player_card.bleach_first_release_shikai = True
                    player_card.bleach_second_release_bankai = True
                if release["FIRST_RELEASE"] == "RESURRECCION":
                    player_card.bleach_first_release_resurreccion = True
                    player_card.bleach_second_release_segunda_etapa = True
                if release["FIRST_RELEASE"] == "FULLBRING ACTIVATION":
                    player_card.bleach_first_release_fullbring_activation = True
                    player_card.bleach_second_release_fullbring_completion = True
                if release["FIRST_RELEASE"] == "VOLLSTANDIG":
                    player_card.bleach_first_release_vollstandig = True
                    player_card.bleach_second_release_schrift = True
        

        player_card.stamina = player_card.stamina + player_card.resolve_value
        player_card.health = player_card.health + resolve_health

        if player_card.bleach_first_release_shikai:
            if player_card.blitz_count < 1:
                player_card.blitz_count = 1
            player_card.damage_healed = player_card.damage_healed + resolve_health
            player_card.attack = round((player_card.attack + (player_card.blitz_count * resolve_attack_value)) * player_card.blitz_count)
            player_card.defense = round((player_card.defense + (player_card.blitz_count * resolve_defense_value)) * player_card.blitz_count)
            message = f"♾️ {player_card.name} resolved with their shikai to increase attack and defense {title_message}"

        if player_card.bleach_first_release_resurreccion:
            player_card.bleach_hollow_ap_buff = player_card.bleach_hollow_ap_buff + player_card.card_lvl
            player_card.attack = player_card.attack + player_card.card_lvl
            player_card.defense = player_card.defense + player_card.card_lvl
            message = f"♾️ {player_card.name} resolved with their resurreccion to increase ability power, attack, and defense by {player_card.card_lvl:,} {title_message}"

        if player_card.bleach_first_release_fullbring_activation:
            player_card.stamina_focus_recovery_amount = 200
            message = f"♾️ {player_card.name} resolved with their fullbring activation extend focus buffs and increase stamina {title_message}"
            player_card.stamina += 200

        if player_card.bleach_first_release_vollstandig:
            player_card.defense = round(player_card.defense * .25)    
            if player_card.blitz_count > 0:
                player_card.bleach_quincy_ap_buff = player_card.move3ap
            else:
                player_card.bleach_quincy_ap_buff = round(player_card.move3ap * .5)
            message = f"♾️ {player_card.name} resolved with their vollstandig to increase their ultimate attack ability power by {player_card.bleach_quincy_ap_buff:,}, lowering their defense by 25% {title_message}"
                    

        player_card.used_resolve = True
        player_card.usedsummon = False
        battle_config.add_to_battle_log(message)
        player_card.bleach_first_release_used = True
        battle_config.turn_total = battle_config.turn_total + 1
        if player_card.bleach_first_release_fullbring_activation:
            battle_config.repeat_turn()
        else:
            battle_config.next_turn()
        return True


async def second_release(player_card, opponent_card, battle_config):
    if player_card.universe == "Bleach":
        player_card.bleach_second_release_used = True
        if player_card.bleach_second_release_bankai:
            damage = round(battle_config.turn_total * player_card.blitz_count * player_card.tier * player_card.focus_count)
            opponent_card.health = opponent_card.health - damage
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} unleashed bankai dealing {damage:,} damage to {opponent_card.name}")
            battle_config.next_turn()

        if player_card.bleach_second_release_segunda_etapa:
            player_card.bleach_second_release_segunda_etapa_activated = True
            # With this being true, when health is above 50% of max health all attacks will be critical strikes
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} transformed into their segunda etapa form. All attacks will be critical strikes while above 50% health")
            battle_config.next_turn()

        if player_card.bleach_second_release_fullbring_completion:
            buff = round(player_card.stamina * player_card.tier)
            player_card.bleach_fullbring_ap_buff += buff
            player_card.attack += buff
            player_card.defense += buff
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} activated their fullbring increase attack, defense, and ability power by {buff:,}")
            battle_config.next_turn()

        if player_card.bleach_second_release_schrift:
            player_card.health = player_card.max_health
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} activated their schrift, reverting all damage taken. Let the real battle begin.")
            battle_config.next_turn()
    return True

def spiritual_pressure(player_card, battle_config, opponent_card):
    if player_card.universe == "Bleach":
        dmg = player_card.damage_cal("Bleach", battle_config, opponent_card)
        dmg['SUMMON_USED'] = False
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} attacked with their spiritual pressure")
        player_card.activate_element_check(battle_config, dmg, opponent_card)

soul_reaper = "**Soul Reaper:**\n*Shikai*: On Resolve: Gain +ATK/DEF × Blitz Count\n*Bankai*: Execute: (Turn × Blitz × Tier) true dmg"
quincy = " **Quincy:**\n*Vollständig*: On Resolve: If player Blitzed during battle gain, 2×Ult AP; else +50% AP. -25% DEF\n*Schrift*: Execute: Full heal"
hollow = "**Hollow:**\n*Resurrección*: On Resolve: Gain AP, ATK, DEF by LVL\n*Segunda Etapa*: Execute: Critical Strikes >50% HP"
fullbringer = "**Fullbringer:**\n*Fullbring Activation*: On Resolve: Gain +200 Stamina, Extend Focus Buffs\n*Fullbring Completion*: Execute: +ATK/DEF by Stamina × Tier"