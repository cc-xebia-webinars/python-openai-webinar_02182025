# To run this script, use the command from the root folder of the repo:
# python -m demos.j_structured_output

# Import necessary modules and classes
from pydantic import BaseModel

from ..utils.openai_utils import openai_service


# Define a class to represent each step in the math reasoning
class Step(BaseModel):
    explanation: str
    output: str


# Define a class to represent the overall math reasoning, including steps and final answer
class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str

    # Pretty print the math reasoning steps and final answer
    def pretty_print(self) -> None:
        for i, step in enumerate(self.steps, start=1):
            print(f"Step {i}:")
            print(f"  Explanation: {step.explanation}")
            print(f"  Output: {step.output}")
            print()
        print(f"Final Answer: {self.final_answer}")


# Request a completion from the OpenAI service with a specific model
# and messages
completion = openai_service.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a helpful math tutor. Guide the user through the "
                "solution step by step."
            ),
        },
        {
            "role": "user",
            "content": (
                "how can I derive the first derivative function of "
                "x^2 + 3x + 5?"
            ),
        },
    ],
    response_format=MathReasoning,
)

# Parse the response and pretty print the math reasoning if available
math_reasoning = completion.choices[0].message

if math_reasoning.refusal:
    print("Refusal: ", math_reasoning.refusal)
else:
    if math_reasoning.parsed:
        math_reasoning.parsed.pretty_print()
    else:
        print("No math reasoning provided.")
