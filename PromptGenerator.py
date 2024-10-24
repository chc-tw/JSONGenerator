import argparse
from src.utility import generate_prompt
from langchain_core.prompts import PromptTemplate
import os

def main():
    parser = argparse.ArgumentParser(description="Generate a prompt based on input.")
    parser.add_argument('--prompt', type=str, required=True, help='Input prompt or path to a text file containing the prompt.')
    args = parser.parse_args()

    if args.prompt.endswith('.txt') and os.path.isfile(args.prompt):
        with open(args.prompt, 'r') as file:
            prompt_content = file.read()
    else:
        prompt_content = args.prompt

    result = generate_prompt(prompt_content)
    print(result)

if __name__ == "__main__":
    main()