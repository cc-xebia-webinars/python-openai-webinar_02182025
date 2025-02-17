# To run this script, use the command from the root folder of the repo:
# python -m demos.c_console_chat

# Import necessary modules and classes
from openai.types.chat import ChatCompletionMessageParam

from ..utils.openai_utils import openai_service

# Define the model to be used
model = "gpt-4o-mini"

# Initialize the conversation with a system message
# A system message is a special type of message that sets
# the behavior of the assistant
messages: list[ChatCompletionMessageParam] = [
    {
        "role": "system",
        "content": "You are a helpful tutor on French culture.",
    },
]

# Print a welcome message to the user
print("\n\n\nWelcome to the French Culture Tutor!\n")

# Start an infinite loop to interact with the user
while True:
    # Prompt the user for input
    next_message = input("\nWhat can I help you with? (type `q` to exit)\n\n")

    # Check if the user wants to exit
    if next_message.lower() in ["exit", "quit", "q"]:
        print("Goodbye!")
        break

    # Create a completion request to the OpenAI service
    completion = openai_service.chat.completions.create(
        model=model,
        messages=[
            *messages,
            {
                "role": "user",
                "content": next_message,
            },
        ],
    )

    # Print the response from the OpenAI service
    print(f"\n{completion.choices[0].message.content}")

    # Observe the response is NOT added to the messages list
