# This script is an entry point to interact with the French weather and fashion expert.
# Run using: python -m demos.h_call_functions

# Import standard libraries and type helpers.
import json  # For parsing JSON responses.
from typing import TypedDict, cast

# Import OpenAI chat message and tool parameter types.
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)

# Import custom utilities for interacting with OpenAI and OpenWeather.
from ..utils.openai_utils import openai_service
from ..utils.openweather_utils import format_weather_data, get_current_weather


# Define the Model type and a list of available models with their cost parameters.
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

# Set up initial system messages that guide the AI's behavior.
messages: list[ChatCompletionMessageParam] = [
    {
        "role": "system",
        "content": (
            "You are a helpful French weather and fashion expert. When a "
            "user asks about the weather or what clothing and accessories to "
            "wear in a specific location in France, retrieve the current "
            "weather for the specified location and provide recommendations "
            "accordingly. Respond in the language the user uses for their "
            "request."
        ),
    },
]

# Define available tools (functions) that the AI can call. In this case, a tool to get current weather data.
tools: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country e.g. Bogotá, Colombia",
                    },
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]

# Welcome the user and prompt for input.
print("\n\n\nWelcome to the French Weather and Fashion Expert!\n")

question = input(
    "Ask what kind of clothing to wear in any French city today > "
)

# Append user query and additional system instructions to the messages.
messages.extend(
    [
        {
            "role": "user",
            "content": question,
        },
        {
            "role": "system",
            "content": (
                "Please only answer questions about French weather and "
                "fashion. For all other requests, politiely decline to "
                "answer and suggest a random French city to visit. All "
                "answers should be appropriate for a 16-year-old high "
                "school student using a school computer. Respond in the "
                "language the user uses for their request. Default to "
                "English if you are unsure which language the user is using."
            ),
        },
    ]
)

# Call the OpenAI chat API with the current message context and tool configuration.
completion = openai_service.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)


# Function to process tool calls (here, the weather retrieval).
def call_function(name: str, args: dict) -> str:
    # If the tool is to get current weather, format the weather data.
    if name == "get_current_weather":
        return format_weather_data(get_current_weather(**args))
    return ""


# Append the initial AI response message.
messages.append(
    cast(ChatCompletionMessageParam, completion.choices[0].message)
)

# Process any tool calls returned from the AI response.
while completion.choices[0].message.tool_calls:
    tool_calls = completion.choices[0].message.tool_calls
    for tool_call in tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        # Execute the corresponding function for the tool call.
        result = call_function(name, args)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
        )

    # Make subsequent API calls with updated message context including tool responses.
    completion = openai_service.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

# Print the final AI response.
print(f"\n\n{completion.choices[0].message.content}\n")
