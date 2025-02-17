# To run this script, use the command from the root folder of the repo:
# python -m demos.e_guardrails_chat


from openai.types.chat import ChatCompletionMessageParam

from ..utils.openai_utils import openai_service

model = "gpt-4o-mini"
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

    next_assistant_message = str(completion.choices[0].message.content)

    print(f"\n{next_assistant_message}")

    messages.append(
        {
            "role": "assistant",
            "content": next_assistant_message,
        }
    )
