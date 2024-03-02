import os
from openai import OpenAI
from logger import logger

# Initialize the API client with your OpenAI API key
OPENAI_KEY = os.getenv('OPENAI_KEY')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4')

# Define the system and user prompts
SYSTEM_PROMPT = ("You are a helpful assistant that translates {reference} to "
                "{target}. Only return the translated string with no additional comments. "
                "Use the context if provided to generate the best possible translation. "
                "Be careful to not add additional punctuation.")

USER_PROMPT =  "Text to translate is: '{string}'. Context: '{context}'."

# Instantiate the OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

def translate(reference_language, target_language, string, context=None):
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT.format(reference=reference_language, target=target_language),
                },
                {
                    "role": "user",
                    "content": USER_PROMPT.format(string=string, context=context),
                },
            ],
        )
        return response.choices[0].message['content']
    except Exception as e:
        # Update the exception handling as per the new library's structure
        logger.error(f"Failed to translate string '{string}'. Error: {str(e)}")
        return string

# Example usage
if __name__ == "__main__":
    result = translate("English", "Spanish", "Hello, world!", "Greeting")
    print(result)
