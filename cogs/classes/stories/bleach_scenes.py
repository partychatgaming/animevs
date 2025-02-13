scene_1 = {
    "title": "The Arrival of the Substitute Shinigami",
    "map_dict": "map_scene_1",
    "storyline": [
        {
            "character": "Rukia Kuchiki",
            "dialogue": "You need to become a Shinigami to protect those you care about.",
            "boss": False,
            "options": {
                "option_1": {
                    "text": "I don’t believe in this Shinigami stuff.",
                    "result": "not_fight",
                    "narrative": "Rukia looks frustrated but continues to explain."
                },
                "option_2": {
                    "text": "Fine, I’ll do it. Just tell me how.",
                    "result": "not_fight",
                    "narrative": "Rukia looks relieved and hands you the Shinigami badge."
                }
            }
        },
        {
            "character": "Ichigo Kurosaki",
            "dialogue": "Who are you? Why are you in my house?",
            "boss": False,
            "options": {
                "option_1": {
                    "text": "I’m here to protect my family from the Hollows.",
                    "result": "not_fight",
                    "narrative": "Ichigo looks surprised but calms down."
                },
                "option_2": {
                    "text": "Get out of my way or I’ll make you move.",
                    "result": "fight",
                    "narrative": "Ichigo prepares for a fight, tension rising in the air."
                }
            }
        },
        {
            "character": "Renji Abarai",
            "dialogue": "Rukia, you know this is forbidden. You shouldn't be here.",
            "boss": True,
            "options": {
                "option_1": {
                    "text": "We need her help! Don’t get in our way!",
                    "result": "fight",
                    "narrative": "Renji draws his sword, ready to battle $$$."
                },
                "option_2": {
                    "text": "Please, let her stay and help us.",
                    "result": "not_fight",
                    "narrative": "Renji hesitates but decides to listen."
                }
            }
        }
    ]
}

scene_2 = {
    "title": "Meeting with Kisuke Urahara",
    "map_dict": "map_scene_2",
    "storyline": [
        {
            "character": "Kisuke Urahara",
            "dialogue": "Welcome to my shop. I hear you need some help with those pesky Hollows.",
            "boss": False,
            "options": {
                "option_1": {
                    "text": "Yes, I need to learn how to fight them.",
                    "result": "not_fight",
                    "narrative": "Kisuke nods, offering his assistance."
                },
                "option_2": {
                    "text": "I don't need your help, old man.",
                    "result": "not_fight",
                    "narrative": "Kisuke smiles knowingly, but doesn't push further."
                }
            }
        },
        {
            "character": "Orihime Inoue",
            "dialogue": "I can sense the Hollows getting stronger. We need to act quickly.",
            "boss": False,
            "options": {
                "option_1": {
                    "text": "Let's go together and face them.",
                    "result": "not_fight",
                    "narrative": "Orihime agrees, ready to assist $$$."
                },
                "option_2": {
                    "text": "Stay here and let me handle this.",
                    "result": "not_fight",
                    "narrative": "Orihime looks worried but trusts your decision."
                }
            }
        },
        {
            "character": "Ichigo Kurosaki",
            "dialogue": "You again? Are you sure you're ready for this?",
            "boss": False,
            "options": {
                "option_1": {
                    "text": "Of course, I'm ready.",
                    "result": "not_fight",
                    "narrative": "Ichigo nods approvingly."
                },
                "option_2": {
                    "text": "I don't need your approval.",
                    "result": "fight",
                    "narrative": "Ichigo frowns, ready to test your resolve."
                }
            }
        }
    ]
}

scene_3 = {
    "title": "Encounter with Renji Abarai",
    "map_dict": "map_scene_3",
    "storyline": [
        {
            "character": "Renji Abarai",
            "dialogue": "You're not supposed to be here. State your business!",
            "boss": False,
            "options": {
                "option_1": {
                    "text": "I'm here to help with the Hollow problem.",
                    "result": "not_fight",
                    "narrative": "Renji narrows his eyes but decides to hear you out."
                },
                "option_2": {
                    "text": "That's none of your concern.",
                    "result": "fight",
                    "narrative": "Renji draws his sword, ready to challenge you."
                }
            }
        },
        {
            "character": "Orihime Inoue",
            "dialogue": "Renji, we need to work together. The Hollows are growing stronger.",
            "boss": False,
            "options": {
                "option_1": {
                    "text": "She's right, we should team up.",
                    "result": "not_fight",
                    "narrative": "Renji grudgingly agrees to a temporary alliance."
                },
                "option_2": {
                    "text": "Stay out of this, Orihime.",
                    "result": "not_fight",
                    "narrative": "Orihime steps back, but remains concerned."
                }
            }
        },
        {
            "character": "Kisuke Urahara",
            "dialogue": "Ah, Renji, always so quick to fight. Let's solve this peacefully, shall we?",
            "boss": False,
            "options": {
                "option_1": {
                    "text": "Listen to Urahara, Renji.",
                    "result": "not_fight",
                    "narrative": "Renji calms down slightly, considering Urahara's words."
                },
                "option_2": {
                    "text": "I don't need his help.",
                    "result": "fight",
                    "narrative": "Renji's grip on his sword tightens, ready for battle."
                }
            }
        }
    ]
}






