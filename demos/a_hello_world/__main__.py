# To run this script, use the command from the root folder of the repo:
# python -m demos.a_hello_world

import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# Initialize OpenAI client
openai_service = OpenAI(api_key=OPENAI_API_KEY)

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
