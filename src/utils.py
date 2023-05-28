import os
import re
from logger import logger

KEY_VALUE_CONTEXT_RE = re.compile(r'\s*"(.*)"\s*=\s*"(.*)";\s*(?:/\*\s*Context:\s*(.*\S)\s*\*/)?')

def write_strings(strings, lang_file_path):

    directory = os.path.dirname(lang_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    try:
        with open(lang_file_path, 'w') as f:
            for key, value in strings.items():
                f.write(f'"{key}" = "{value}";\n')

    except Exception as e:
        logger.error(f"Error occurred while writing translations: {str(e)}")
        raise e

def read_strings(file_path):
    try:
        strings = {}
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file_content:
                for line in file_content:
                    match = KEY_VALUE_CONTEXT_RE.match(line.strip())
                    if match:
                        existing_key = match.group(1)
                        existing_value = match.group(2)
                        strings[existing_key] = existing_value
        return strings
    except Exception as e:
        logger.error(f"Error occurred while reading strings: {str(e)}")
        return {}

def sort_by_key(strings, ordered_keys):
    return { key: strings[key] for key in ordered_keys if key in strings }

def extract_strings_with_context(file_content):
    try:
        strings = {}
        for line in file_content:
            match = KEY_VALUE_CONTEXT_RE.match(line)
            if match:
                key, value = match.group(1), match.group(2)
                context = match.group(3) if match.group(3) else None
                strings[key] = {'value': value, 'context': context}
        return strings
    except Exception as e:
        logger.error(f"Error occurred while extracting strings from lines: {str(e)}")
        return {}
    
def delete_file(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f'Successfully deleted file {file_path}')
        except Exception as e:
            logger.error(f'Error occurred while deleting file {file_path}: {str(e)}')
            raise e