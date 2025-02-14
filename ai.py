import os
from decouple import config
import openai
import asyncio

# Set up your OpenAI API key
# openai.api_key = config('OPENAI_API')


# client = OpenAI(
#     api_key=config('OPENAI_API')
# )

openai.api_key = config('OPENAI_API')

async def summarize_last_moves(messages):
    await asyncio.sleep(1)
    # Check if messages is not a list
    if not isinstance(messages, list):
        return "The match has started."
    
    if not messages:
        return " "

    # Extract the last four messages
    last_four_messages = messages[-4:]

    # Prepare the input for ChatGPT
    input_text = "\n".join(last_four_messages)
    
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"Summarize the last 4 moves completed in this anime card game based on the information given in this list:\n\n{input_text}\n\nNever summarize or create information that is not in the list given. Always follow the format of '(Turn Number) - Summary'. Please be short, concise, and to the point. Do not explain that you are a bot, simply respond with the summary. If there is only one move in the list, summarize that move. If there are no moves in the list, respond with 'The match has started.'"
    
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    summary = response.choices[0].message.content
    return summary


async def suggested_title_scenario(universe_title, characters):
    await asyncio.sleep(1)
    # Check if messages is not a list
    if not isinstance(characters, list):
        return False
    
    if not characters:
        return " "

    # Prepare the input for ChatGPT
    character_names = ", ".join(characters)
    
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"I created an anime battle in which I have to defeat {character_names} from the {universe_title} universe. What is a good, short title for that battle? Only respond with the name of the title. Never add quotes around the title. Be creative and concise."
    
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    title = response.choices[0].message.content
    return title


async def focus_message(your_card_name, your_card_universe, opponent_card, opponent_card_universe):
    await asyncio.sleep(1)
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"You are {your_card_name} from the {your_card_universe} universe and you are fighting against {opponent_card} from the {opponent_card_universe} universe. You are focusing intently on your strategy to win. Write a 1 sentence message to {opponent_card} to intimidate them and show your determination to win the match. Do not include quotes.  Be as raw and true to your character's nature as possible. "
    
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    summary = response.choices[0].message.content
    return summary


async def resolve_message(your_card_name, your_card_universe, opponent_card, opponent_card_universe):
    await asyncio.sleep(1)
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"You are {your_card_name} from the {your_card_universe} universe and you are fighting against {opponent_card} from the {opponent_card_universe} universe. You have strenghend your conviction and resolve to win. Write a 1 sentence message to {opponent_card} to show how serious you are about your victory. Do not include quotes. Be as raw and true to your character's nature as possible. "
    
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    summary = response.choices[0].message.content
    return summary


async def win_message(your_card_name, your_card_universe, opponent_card, opponent_card_universe):
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"You are {your_card_name} from the {your_card_universe} universe and you are fighting against {opponent_card} from the {opponent_card_universe} universe. You have won the battle. Write a 1 sentence message to {opponent_card} to show your victory and dominance. Do not include quotes. Be as raw and true to your character's nature as possible."
    
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    summary = response.choices[0].message.content
    return summary


async def lose_message(losing_card_name, your_card_universe, winning_card_name, opponent_card_universe):
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"You are {losing_card_name} from the {your_card_universe} universe and you are fighting against {winning_card_name} from the {opponent_card_universe} universe. You have lost the battle and are about to die. Write a 1 sentence message to {winning_card_name} to reflect your loss and your final words. Do not include quotes. Be as raw and true to your character's nature as possible."
    
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    summary = response.choices[0].message.content
    return summary


async def match_start_message(your_card_name, your_card_universe, opponent_card, opponent_card_universe):
    await asyncio.sleep(1)
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"You are {your_card_name} from the {your_card_universe} universe and you are fighting against {opponent_card} from the {opponent_card_universe} universe. The match has started. Write a 1 to 2 sentence message to {opponent_card} to show your readiness and determination to win. Never include quotation marks. Be as raw and true to your character's nature as possible."
    
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    summary = response.choices[0].message.content
    return summary


async def starting_battle_ai_message(your_card_name, your_card_universe, opponent_card, opponent_card_universe):
    await asyncio.sleep(1)
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"You are {your_card_name} from the {your_card_universe} universe and you are fighting against {opponent_card} from the {opponent_card_universe} universe fighting in a location in the {opponent_card_universe} universe. In 1 sentence, describe the location of the fight. Do not include quotes."
    
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    summary = response.choices[0].message.content
    return summary


async def rpg_encounter_message(your_card_name, your_card_universe, opponent_card, location):
    await asyncio.sleep(1)
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"You are {your_card_name} from the {your_card_universe} universe and you are meeting {opponent_card} from the {your_card_universe} universe in the area of a {location}. Based on lore if the characters are familiar with each other treat the greeting as so, otherwise Introduce yourself and either threaten, ask a favor or be friendly based on your characters goals. Do this in 3 sentences 35 characters each. Seperate each sentence with a newline character. Do not include quotes. And do not use back to back newlines."
    
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    summary = response.choices[0].message.content
    return summary


async def rpg_start_encounter_message(your_card_name, your_card_universe, opponent_card, location):
    await asyncio.sleep(1)
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"You are {your_card_name} from the {your_card_universe} universe and you are meeting {opponent_card} from the {your_card_universe} universe in the area of a {location}. Describe the setting of the encounter and the two chracters meeting in 1 sentences 30 characters. Do not include quotes. Do not refer to the encounter."
    
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    summary = response.choices[0].message.content
    return summary


async def rpg_movement_ai_message(your_card_name, your_card_universe,location,  move, stand, up, down, left, right, last_thought = None, train_of_thought = None):
    await asyncio.sleep(1)
    if up is None:
        up = "Clear View"
    if down is None:
        down = "Clear View"
    if left is None:
        left = "Clear View"
    if right is None:
        right = "Clear View"
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"You are {your_card_name} from the {your_card_universe} universe and you navigating a {location} moving {move}. The following emojis represent potential points of interest. You are standing on {stand} and you see a {up} a {down} a {left} and a {right}. Speak as though you are a conversational inner monologue. Describe the scene as if you were there standing in the scene. Describe it in 3 complete sentences or less. Stay true to the chracters tone and voice. Use no more than 40 characters in total. Take the Universe in consideration when describiing the scene and the tone of the scene. Do not include quotes."
    if last_thought:
        prompt += f" You last thought was {last_thought}. View these thoughts as a continuation of your experience walking in this world. Place yourself in this headspace and respond accordingly. Ensure your response is unique from your last thought.Try not to repeat Adjectives or Adverbs"
    if train_of_thought:
        prompt += f" You have a train of thought that is {train_of_thought}. Use this as a foundation for your response. Ensure your response is unique from your last thought.If you last three thoughts are serious tell a situation joke or pun. Try not to repeat Adjectives or Adverbs"
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    summary = response.choices[0].message.content
    return summary


async def rpg_action_ai_message(your_card_name, your_card_universe,location,  move, up, down, left, right, thoughts):
    await asyncio.sleep(1)
    if up is None:
        up = "Clear View"
    if down is None:
        down = "Clear View"
    if left is None:
        left = "Clear View"
    if right is None:
        right = "Clear View"
    # Define the prompt to indicate the context of the anime card game assistant
    prompt = f"You are {your_card_name} from the {your_card_universe} universe and you navigating a {location}, you think this about this area :{thoughts} and decide to move {move}. The following emojis represent potential points of interest. You see a {up} a {down} a {left} and a {right}. Create a complete scene from these emojis and describe how the character is feeling with their thoughts as a foundatation for the tone. Describe it in 2 sentences or less. Use no more than 70 characters in total. Do not include quotes.Do not use the characters name. Be witty and creative."
    
    # Call the OpenAI API to summarize messages using the GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the summary from the response
    summary = response.choices[0].message.content
    return summary


async def rpg_story(your_card_name, universe_name, list_of_combatants, location_in_universe):
    prompt = f"""
    Generate a humorous, suspenseful, mysterious, or horror storyline for {your_card_name} in the {universe_name} universe at {location_in_universe}. Include interactions with multiple characters from this list: {list_of_combatants}. The story should have dialogue options to fight or not fight, culminating in a boss showdown where both options lead to a fight. Only use characters from the provided list. Use aggressive dialogue for fight scenarios. The "dialogue" field must have a maximum of 3 sentences and 350 characters per character. The "narrative" for each character should be no more than one sentence. Create a detailed and engaging storyline following this exact structure:

    ```json
    {{
        "title": "Story Title",
        "storyline": [
            {{
                "character": "Character Name",
                "dialogue": "Character's dialogue (3 sentences max, 350 characters max)",
                "FIGHT": true,
                "options": {{
                    "option_1": {{
                        "text": "Aggressive/Non-aggressive response (3 sentences max, 350 characters max)",
                        "result": "fight/not_fight",
                        "narrative": "Outcome of the choice (1 sentence max)"
                    }},
                    "option_2": {{
                        "text": "Alternative response (3 sentences max, 350 characters max)",
                        "result": "fight/not_fight",
                        "narrative": "Outcome of the choice (1 sentence max)"
                    }}
                }}
            }},
            {{
                "character": "Next Character Name",
                "dialogue": "Next character's dialogue",
                "FIGHT": false,
                "options": {{
                    "option_1": {{
                        "text": "Response option 1",
                        "result": "fight/not_fight",
                        "narrative": "Outcome of option 1"
                    }},
                    "option_2": {{
                        "text": "Response option 2",
                        "result": "fight/not_fight",
                        "narrative": "Outcome of option 2"
                    }}
                }}
            }}
        ],
        "BOSS": {{
            "character": "Boss Character Name",
            "dialogue": "Boss's dialogue (3 sentences max, 350 characters max)",
            "FIGHT": true,
            "options": {{
                "option_1": {{
                    "text": "Response to boss (3 sentences max, 350 characters max)",
                    "result": "fight",
                    "narrative": "Outcome of the choice (1 sentence max)"
                }},
                "option_2": {{
                    "text": "Alternative response to boss (3 sentences max, 350 characters max)",
                    "result": "fight",
                    "narrative": "Outcome of the choice (1 sentence max)"
                }}
            }}
        }}
    }}
    ```

    Ensure the output strictly adheres to this JSON structure, including all fields and formatting.
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a creative storyteller who always returns stories in the exact JSON format specified, without any additional text."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

