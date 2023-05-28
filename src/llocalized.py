import os
import git
import utils
from languages import LANGUAGE_NAMES
from logger import logger
from translate import translate

ROOT_DIR = os.environ['GITHUB_WORKSPACE']
SOURCE_COMMIT_SHA = os.environ['SOURCE_COMMIT_SHA']
TARGET_COMMIT_SHA = os.environ['TARGET_COMMIT_SHA']
BASE_LANGUAGE = os.getenv('BASE_LANGUAGE', 'en')
TARGET_LANGUAGES = set(language.strip() for language in os.environ['TARGET_LANGUAGES'].split(','))
REPO = git.Repo(ROOT_DIR)

def process_diff(diff):
    for change_type in ['A', 'M', 'D']:
        for changed_file in diff.iter_change_type(change_type):
            file_path = changed_file.a_path
            if file_path.endswith(f"{BASE_LANGUAGE}.lproj/Localizable.strings"):
                if change_type == 'A':
                    logger.info(f'Added base file')
                    handle_added_file(changed_file)
                elif change_type == 'M':
                    logger.info(f'Modified base file')
                    handle_modified_file(changed_file)
                elif change_type == 'D':
                    logger.info(f'Deleted base file')
                    handle_deleted_file(changed_file)
    logger.info('Finished processing diff')

def handle_added_file(file):
    b_file_content = file.b_blob.data_stream.read().decode('utf-8').splitlines()
    b_strings = utils.extract_strings_with_context(b_file_content)
    process_strings(file, b_strings)

def handle_modified_file(file):
    a_file_content = file.a_blob.data_stream.read().decode('utf-8').splitlines()
    a_strings = utils.extract_strings_with_context(a_file_content)

    b_file_content = file.b_blob.data_stream.read().decode('utf-8').splitlines()
    b_strings = utils.extract_strings_with_context(b_file_content)

    modified_strings = {k: v for k, v in b_strings.items() if k in a_strings and v != a_strings[k]}
    process_strings(file, b_strings, modified_strings)

def handle_deleted_file(file):
    file_path = file.a_path
    for language in TARGET_LANGUAGES:
        lang_file_path = file_path.replace(f"{BASE_LANGUAGE}.lproj", f"{language}.lproj")
        utils.delete_file(lang_file_path)

def process_strings(changed_file, base_language_strings, modified_strings = {}):
    for target_language in TARGET_LANGUAGES:
        logger.info(f'Translate {LANGUAGE_NAMES.get(BASE_LANGUAGE)} -> {LANGUAGE_NAMES.get(target_language)}')
        if target_language == BASE_LANGUAGE:
            logger.info('Target language is the same as base language')
            continue
        
        lang_file_path = changed_file.a_path.replace(f"{BASE_LANGUAGE}.lproj", f"{target_language}.lproj")

        base_language_keys = base_language_strings.keys()

        #Read current translations file
        translated_strings = utils.read_strings(lang_file_path)
        translated_keys = translated_strings.keys()

        # Keys present in the base file but not in the other language files
        added_strings_keys = base_language_keys - translated_keys
        logger.info(f'{len(added_strings_keys)} Added: {list(added_strings_keys)}')

        # Keys that were modified in the base file with respect to the base branch
        modified_strings_keys = modified_strings.keys()
        logger.info(f'{len(modified_strings_keys)} Modified: {list(modified_strings_keys)}')

        #All keys that need translation
        keys_to_write = set(added_strings_keys).union(set(modified_strings_keys))

        # Keys present in the other language files but not in the English file
        keys_to_delete = set(translated_keys - base_language_keys)
        logger.info(f'{len(keys_to_delete)} Deleted: {list(keys_to_delete)}')

        logger.info(f'----------------------')
        for key in keys_to_write:
            string = base_language_strings[key]
            value, context = string['value'], string['context']
            translated_value = translate(LANGUAGE_NAMES[BASE_LANGUAGE], LANGUAGE_NAMES[target_language], value, context)
            translated_strings[key] = translated_value
            logger.info(f' + {translated_value}')

        for key in keys_to_delete:
            logger.info(f' - {translated_strings[key]}')
            del translated_strings[key]
            
        logger.info(f'----------------------')
        # Sort strings in the same order as the base language
        translated_strings_sorted = utils.sort_by_key(translated_strings, base_language_keys)
        utils.write_strings(translated_strings_sorted, lang_file_path)

def main():
    logger.info('Starting...')
    logger.info(TARGET_LANGUAGES)

    source_commit = REPO.commit(SOURCE_COMMIT_SHA)
    target_commit = REPO.commit(TARGET_COMMIT_SHA)
    diff = source_commit.diff(target_commit)

    if not diff:
        logger.info('No changes found')
        exit()

    process_diff(diff)

if __name__ == "__main__":
    main()