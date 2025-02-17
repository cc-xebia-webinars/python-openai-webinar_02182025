# To run this script, use the command from the root folder of the repo:
# python -m demos.i_call_cmd_funcs


import json
from typing import TypedDict, cast

from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)

from ..utils.openai_utils import openai_service


class Model(TypedDict):
    id: str
    name: str
    input: float
    output: float


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

tools: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "toggle_tokens",
            "description": (
                "Toggle the display of token usage information for "
                "the last chat."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "token_stats",
            "description": (
                "Get stats on the selected model, number of total tokens, "
                "and the expense of the tokens in dollars."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]


def get_price(
    model_id: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    for model_info in models:
        if model_info["id"] == model_id:
            input_price = model_info["input"]
            output_price = model_info["output"]
            break
    else:
        raise ValueError("Model not found")

    return (input_price * prompt_tokens) + (output_price * completion_tokens)


def call_function(name: str, args: dict) -> str:
    if name == "toggle_tokens":
        global show_tokens
        show_tokens = not show_tokens
        return f"Show tokens: {show_tokens}"
    elif name == "token_stats":
        return (
            f"Model: {model_id}\n"
            f"Total Tokens: {total_tokens} "
            "Total Expense: "
            f"(${get_price(model_id, prompt_tokens, completion_tokens):.8f})"
        )
    return ""


show_tokens = False
completion_tokens = 0
prompt_tokens = 0
total_tokens = 0

print("\n\n\nWelcome to the French Culture Tutor!\n")

print("Available models:")
for model_index, model_info in enumerate(models):
    print(f"{model_index + 1} {model_info['name']} ({model_info['id']})")

model_number = int(input("\nWhich model would you like to use? "))
model_index = model_number - 1
if model_index > len(models) - 1 or model_index < 0:
    raise ValueError("Invalid model number.")

model_id = models[model_index]["id"]

while True:
    next_user_message = input(
        "\nWhat can I help you with? (type `q` to exit)\n\n> "
    )

    if next_user_message.lower() in ["exit", "quit", "q"]:
        print("Goodbye!")
        break

    messages.append(
        {
            "role": "user",
            "content": next_user_message,
        }
    )

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
                    "appropriate. If the user asks to toggle tokens use the "
                    "toggle_tokens tool function. Of, if the user asks for "
                    "stats on the session such as the selected model the "
                    "number of tokens used, or the cost/expense of the "
                    "tokens use the token_stats tool function."
                ),
            },
        ],
        tools=tools,
        tool_choice="auto",
    )

    next_assistant_message = completion.choices[0].message
    messages.append(cast(ChatCompletionMessageParam, next_assistant_message))

    if completion.choices[0].message.tool_calls:
        tool_calls = completion.choices[0].message.tool_calls
        for tool_call in tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            result = call_function(name, args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

        completion = openai_service.chat.completions.create(
            model=model_id,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

    next_assistant_message = completion.choices[0].message
    print(f"\n{next_assistant_message.content}")

    if completion.usage:
        completion_tokens += completion.usage.completion_tokens
        prompt_tokens += completion.usage.prompt_tokens
        total_tokens += completion.usage.total_tokens

    if show_tokens:
        if completion.usage:
            print(
                f"\n\nCompletion Tokens: {completion.usage.completion_tokens}"
                f"\nPrompt Tokens: {completion.usage.prompt_tokens}"
                f"\nTotal Tokens: {completion.usage.total_tokens}"
            )
        else:
            print("No usage information available.")

    messages.append(cast(ChatCompletionMessageParam, next_assistant_message))
