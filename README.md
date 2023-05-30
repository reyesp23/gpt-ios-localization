# GPT iOS String Localization

This GitHub action translates your base language .strings files into multiple languages using the OpenAI API and opens a Pull Request with the translations. Include a context comment on each string to improve the translation quality.

### ⚠️**Warnings**
- The OpenAI API is currently not available for free. You need an API Key issued with a `paid account` to use this workflow.
- This action works reliably using gpt-4, however this model is currently only available through a waitlist. You can still test this Action with gpt-3.5-turbo, however it is not recommended since it ocasionally includes additional characters or format errors that can break your .strings file. 


This is a GitHub Action that uses GPT-4 to translate .strings files into multiple languages.
Add context to your translations by appending a comment for each string:

```"sign_in_email_field" = "Sign In"; /* Context: Label used in email field on sign in page */```

The localization updates will be posted on a Pull Request. 


## Setup

### Repository Settings

#### 1. Settings > Actions > General

- Select `Read and write permissions`
- Toggle `Allow GitHub Actions to create and approve pull requests`
  
<img width="893" alt="Screenshot 2023-05-29 at 23 00 45" src="https://github.com/reyesp23/gpt-ios-localization/assets/22821919/cd7de4b0-26c6-4199-8641-af9a3d6aa737">

#### 2. Settings > Secrets and variables > Actions

<img width="1230" alt="Screenshot 2023-05-29 at 23 03 10" src="https://github.com/reyesp23/gpt-ios-localization/assets/22821919/7727d95a-62d3-4bf9-a99e-ce62dadc67bd">


### GitHub Actions Workflow Settings

#### Required
- Set trigger, for example: Pull Request Opened, Pull Request Merged, Banch created, Manual dispatch, etc
- OPENAI_KEY 
- GITHUB_TOKEN
- BASE_LANGUAGE: Provide base language for your translations
- TARGET_LANGUAGES: Provide desired target languages separated by comma.
- PR_BASE_BRANCH: Provide base brach for the auto generated translations PR
- HEAD_REF: Provide the reference (SHA or branch name) of the commit that contains the changes in the base language file.
- SOURCE_REF: Provide the reference (SHA or branch name) of the commit that will serve as base for the diff comparison. 
- 

#### Optional
- PR_TTLE
- PR_BODY
- PR_LABELS
- LLM_MODEL

#### On PR Opened
- Branch with Feature A opens a PR trying to merge into main
- Localize Feature A base language string changes
- Opens a new PR based on Feature A branch with the translations
- Review and Merge translations PR into Feature A branch
- Merge Feature A into main

```yaml
name: Localize - Opened PR
on:
  pull_request:
    types:
      - opened
    branches:
      - main

jobs:
  localize:
    runs-on: ubuntu-latest
    steps:
      - name: Run Localize Action
        uses: reyesp23/gpt-ios-localization@main
        with:
          HEAD_REF: ${{ github.event.pull_request.head.sha }}
          SOURCE_REF: ${{ github.event.pull_request.base.sha }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_KEY: ${{ secrets.OPENAI_KEY }}
          BASE_LANGUAGE: 'en'
          TARGET_LANGUAGES: 'it, es'
          PR_BASE_BRANCH: ${{ github.event.pull_request.head.ref }}
```

## 🌐 Languages
- English - en
- Spanish - es
- Italian - it
- 
## 📃 License
MIT License
