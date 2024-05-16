from decouple import config
from openai import OpenAI

# Set up your OpenAI API key
# openai.api_key = config('OPENAI_API')
client = OpenAI(
    api_key=config('OPENAI_API')
)

def summarize_last_moves(messages):
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