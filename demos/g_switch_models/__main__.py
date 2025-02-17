# This module implements a command-line French Culture Tutor using OpenAI's chat API.
# It allows the user to select a model and interact using a conversational interface.

from typing import TypedDict

from openai.types.chat import ChatCompletionMessageParam

from ..utils.openai_utils import openai_service


# Define a TypedDict to store model information: id, name, and per-token pricing.
class Model(TypedDict):
    id: str
    name: str
    input: float
    output: float


# List of available models with their associated pricing per input/output token.
models: list[Model] = [
    {
        "id": "gpt-4o-mini",
        "name": "GPT-4o Mini",
        "input": 0.15 / 1000000,
        "output": 0.60 / 1000000,
    },
    {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "input": 2.50 / 1000000,
        "output": 10.00 / 1000000,
    },
]


# Pre-configured conversation starting with system instructions to ensure responses are centered on French culture.
messages: list[ChatCompletionMessageParam] = [
    {
        "role": "system",
        "content": (
            "You are a helpful tutor on French culture. All questions should "
            "be answered with respect to French culture and history. It is "
            "important to provide accurate and detailed information. When "
            "appropriate, include references to famous French cultural "
            "figures, use French words/phrases, and discuss the significance "
            "of events in French history. Your goal is to help the user "
            "learn about French culture in an engaging and informative way. "
            "If the user asks about a specific topic, provide a brief "
            "overview and suggest further reading or resources. If the user "
            "asks for a summary of a specific event, provide a concise "
            "summary and highlight its importance in French culture. If the "
            "user asks for a comparison between French culture and another "
            "culture, provide a thoughtful analysis that respects both "
            "cultures. The bulk of any answer should be in the language of "
            "the user which defaults to English."
        ),
    },
]


# Function to compute the total price based on prompt and completion token usage.
def get_price(
    model_id: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    # Loop through available models to find matching pricing details.
    for model_info in models:
        if model_info["id"] == model_id:
            input_price = model_info["input"]
            output_price = model_info["output"]
            break
    else:
        raise ValueError("Model not found")

    # Calculate and return the total cost.
    return (input_price * prompt_tokens) + (output_price * completion_tokens)


# Initialize token tracking and a flag to control token usage display.
show_tokens = False
completion_tokens = 0
prompt_tokens = 0
total_tokens = 0

print("\n\n\nWelcome to the French Culture Tutor!\n")

# List each available model for user selection.
print("Available models:")
for model_index, model_info in enumerate(models):
    print(f"{model_index + 1} {model_info['name']} ({model_info['id']})")

model_number = int(input("\nWhich model would you like to use? "))
model_index = model_number - 1
if model_index > len(models) - 1 or model_index < 0:
    raise ValueError("Invalid model number.")

model_id = models[model_index]["id"]

# Main interactive loop for processing user input and generating OpenAI responses.
while True:
    # Read the next message from the user.
    next_user_message = input(
        "\nWhat can I help you with? (type `q` to exit)\n\n> "
    )

    if next_user_message.lower() in ["toggle tokens"]:
        # Toggle token count display.
        show_tokens = not show_tokens
        print(f"Show tokens: {show_tokens}")
        continue

    if next_user_message.lower() in ["token count"]:
        # Display the current token usage and corresponding cost.
        print(
            f"Model: {model_id}\n"
            f"Total Tokens: {total_tokens} "
            f"(${get_price(model_id, prompt_tokens, completion_tokens):.8f})"
        )
        continue

    if next_user_message.lower() in ["exit", "quit", "q"]:
        print("Goodbye!")
        break

    # Add the user's message to the conversation history.
    messages.append(
        {
            "role": "user",
            "content": next_user_message,
        }
    )

    # Call the OpenAI service to generate a completion based on the current conversation.
    completion = openai_service.chat.completions.create(
        model=model_id,
        messages=[
            *messages,
            {
                "role": "system",
                "content": (
                    "Only answer questions relevant to French culture and "
                    "history. It's ok to discuss controversial topics, but "
                    "keep it respectful of all cultures involved. Assume "
                    "the user is a high school student around the age of 16 "
                    "and keep answers simple and easy to understand and "
                    "appropriate."
                ),
            },
        ],
    )

    # Store and print the assistant's response.
    next_assistant_message = str(completion.choices[0].message.content)
    print(f"\n{next_assistant_message}")

    # Update token counts if the usage information is available.
    if completion.usage:
        completion_tokens += completion.usage.completion_tokens
        prompt_tokens += completion.usage.prompt_tokens
        total_tokens += completion.usage.total_tokens

    # Optionally display detailed token count information.
    if show_tokens:
        if completion.usage:
            print(
                f"\n\nCompletion Tokens: {completion.usage.completion_tokens}"
                f"\nPrompt Tokens: {completion.usage.prompt_tokens}"
                f"\nTotal Tokens: {completion.usage.total_tokens}"
            )
        else:
            print("No usage information available.")

    # Append the assistant's response to the conversation history.
    messages.append(
        {
            "role": "assistant",
            "content": next_assistant_message,
        }
    )
