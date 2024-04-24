import os
import git
import utils
from languages import LANGUAGES
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
                    handle_added_base_file(changed_file)
                elif change_type == 'M':
                    logger.info(f'Modified base file')
                    handle_modified_base_file(changed_file)
                elif change_type == 'D':
                    logger.info(f'Deleted base file')
                    handle_deleted_base_file(changed_file)
    logger.info('Finished processing diff')

def handle_added_base_file(base_file):
    target_commit_content = base_file.b_blob.data_stream.read().decode('utf-8').splitlines()
    target_commit_strings = utils.extract_strings_with_context(target_commit_content)
    process_strings(base_file, target_commit_strings)

def handle_modified_base_file(base_file):
    source_commit_content = base_file.a_blob.data_stream.read().decode('utf-8').splitlines()
    target_commit_content = base_file.b_blob.data_stream.read().decode('utf-8').splitlines()
    
    source_commit_strings = utils.extract_strings_with_context(source_commit_content)
    target_commit_strings = utils.extract_strings_with_context(target_commit_content)
    diff_strings = {k: v for k, v in target_commit_strings.items() if k in source_commit_strings and v != source_commit_strings[k]}
    process_strings(base_file, target_commit_strings, diff_strings)

def handle_deleted_base_file(base_file):
    base_file_path = base_file.a_path
    for language in TARGET_LANGUAGES:
        lang_file_path = base_file_path.replace(f"{BASE_LANGUAGE}.lproj", f"{language}.lproj")
        utils.delete_file(lang_file_path)

def process_strings(base_file, base_language_strings, diff_strings = {}):
    for target_language in TARGET_LANGUAGES:
        if target_language == BASE_LANGUAGE:
            logger.info('Target language is the same as base language')
            continue
        logger.info(f'Translate {LANGUAGES.get(BASE_LANGUAGE)} -> {LANGUAGES.get(target_language)}')

        #Read strings file for base language
        base_language_keys = base_language_strings.keys()

        #Read strings file for target language
        lang_file_path = base_file.a_path.replace(f"{BASE_LANGUAGE}.lproj", f"{target_language}.lproj")
        target_language_strings = utils.read_strings(lang_file_path)
        target_language_keys = target_language_strings.keys()

        # Find keys present in the base language file but not in the target language file
        added_strings_keys = base_language_keys - target_language_keys
        logger.info(f'{len(added_strings_keys)} Added: {list(added_strings_keys)}')

        # Keys that were modified in the base language file
        diff_strings_keys = diff_strings.keys()
        logger.info(f'{len(diff_strings_keys)} Modified: {list(diff_strings_keys)}')

        # Keys present in target language file but not in the base language file
        keys_to_delete = set(target_language_keys - base_language_keys)
        logger.info(f'{len(keys_to_delete)} Deleted: {list(keys_to_delete)}')

        #All keys that need translation (Added + Modified)
        keys_to_write = set(added_strings_keys).union(set(diff_strings_keys))

        logger.info(f'----------------------')
        for key in keys_to_write:
            base_language_string = base_language_strings[key]
            value, context = base_language_string['value'], base_language_string['context']
            translated_value = translate(LANGUAGES[BASE_LANGUAGE], LANGUAGES[target_language], value, context)
            target_language_strings[key] = translated_value
            logger.info(f' + {translated_value}')

        for key in keys_to_delete:
            logger.info(f' - {target_language_strings[key]}')
            del target_language_strings[key]
            
        logger.info(f'----------------------')

        # Sort strings in the same order as the base language
        translated_strings_sorted = utils.sort_by_key(target_language_strings, base_language_keys)
        utils.write_strings(translated_strings_sorted, lang_file_path)

def main():
    logger.info('Starting...')
    logger.info(TARGET_LANGUAGES)

    if BASE_LANGUAGE not in LANGUAGES:
        logger.error(f'Base language {BASE_LANGUAGE} not supported')
        exit(1)
    
    for language in TARGET_LANGUAGES:
        if language not in LANGUAGES:
            logger.error(f'Target language {language} not supported')
            exit(1)

    source_commit = REPO.commit(SOURCE_COMMIT_SHA)
    target_commit = REPO.commit(TARGET_COMMIT_SHA)
    diff = source_commit.diff(target_commit)

    if not diff:
        logger.info('No changes found in base file')
        exit(0)

    process_diff(diff)

if __name__ == "__main__":
    main()