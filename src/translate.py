import openai
import os
from logger import logger

OPENAI_KEY = os.getenv('OPENAI_KEY')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4')

SYSTEM_PROMPT = ("You are a helpful assistant that translates {reference} to "
                "{target}. Only return the translated string with no additional comments. "
                "Use the context if provided to generate the best possible translation. "
                "Be careful to not add additional punctuation.")

USER_PROMPT =  "Text to translate is: '{string}'. Context: '{context}'."


openai.api_key = OPENAI_KEY

def translate(reference_language, target_language, string, context=None):
    try:
        response = openai.ChatCompletion.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT.format(reference=reference_language, target=target_language),
                },
                {
                    "role": "user",
                    "content": USER_PROMPT.format(string = string, context = context),
                },
            ],
        )
        return response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        logger.error(f"Failed to translate string '{string}'. Error: {str(e)}")
        return string