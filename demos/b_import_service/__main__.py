# To run this script, use the command from the root folder of the repo:
# python -m demos.b_import_service

# import an instantiate OpenAI client object
from ..utils.openai_utils import openai_service

# Example usage: Generate a haiku about recursion in programming
completion = openai_service.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming.",
        },
    ],
)

print(completion.choices[0].message.content)
