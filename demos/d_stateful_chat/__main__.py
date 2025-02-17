# To run this script, use the command from the root folder of the repo:
# python -m demos.d_stateful_chat


from openai.types.chat import ChatCompletionMessageParam

from ..utils.openai_utils import openai_service

model = "gpt-4o-mini"
messages: list[ChatCompletionMessageParam] = [
    {
        "role": "system",
        "content": ("You are a helpful tutor on French culture."),
    },
]

print("\n\n\nWelcome to the French Culture Tutor!\n")

while True:
    next_user_message = input(
        "\nWhat can I help you with? (type `q` to exit)\n\n"
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
        model=model,
        messages=messages,
    )

    next_assistant_message = str(completion.choices[0].message.content)

    print(f"\n{next_assistant_message}")

    messages.append(
        {
            "role": "assistant",
            "content": next_assistant_message,
        }
    )
