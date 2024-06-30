from decouple import config
from openai import OpenAI
import asyncio

# Set up your OpenAI API key
# openai.api_key = config('OPENAI_API')
client = OpenAI(
    api_key=config('OPENAI_API')
)

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
    response = client.chat.completions.create(
        model="gpt-4o",
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
    response = client.chat.completions.create(
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
    response = client.chat.completions.create(
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
    prompt = f"You are {your_card_name} from the {your_card_universe} universe and you are fighting against {opponent_card} from the {opponent_card_universe} universe. You have strenghend yoru conviction and resolve to win. Write a 1 sentence message to {opponent_card} to show how serious you are about your victory. Do not include quotes. Be as raw and true to your character's nature as possible. "
    
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
