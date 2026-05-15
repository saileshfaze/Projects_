import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


def very_important_function(
    template: str,
    *variables,
    file: os.PathLike,
    engine: str,
    header: bool = True,
    debug: bool = False,
):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, "w") as _f:
        ...


response = client.responses.create(
    model="gpt-5.5", input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)
