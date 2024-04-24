# GPT iOS String Localization

This GitHub action translates your base language ```.strings``` files into multiple languages using Open AI ```GPT-4``` API and opens a Pull Request with the translations. 

### Contextual translations
Add context to improve the translations by simply including a comment after each string:

```
"sign_in_email_field" = "Sign In"; /* Context: Label used in email field on sign in page */
```

### ⚠️**Warning**⚠️
- The OpenAI API is currently not available for free. To use this action you'll need to sign-up for a paid account and generate an API Key.
- This action works reliably using ```gpt-4```, you can still test this Action with ```gpt-3.5-turbo```, however it is not recommended since it ocasionally includes additional characters or format errors that can break your .strings file. 




## Configure Repository

### Enable permissions
#### 1. Settings > Actions > General > Workflow permissions

- Select `Read and write permissions`
- Toggle on `Allow GitHub Actions to create and approve pull requests`
  
<img width="893" alt="Screenshot 2023-05-29 at 23 00 45" src="https://github.com/reyesp23/gpt-ios-localization/assets/22821919/cd7de4b0-26c6-4199-8641-af9a3d6aa737">

### Set your OpenAI API key as secret

#### 2. Settings > Secrets and variables > Actions > Repository secrets > New repository secret

<img width="1230" alt="Screenshot 2023-05-29 at 23 03 10" src="https://github.com/reyesp23/gpt-ios-localization/assets/22821919/7727d95a-62d3-4bf9-a99e-ce62dadc67bd">




## Configure Actions

#### Actions > set up a workflow yourself
<img width="1130" alt="Screenshot 2024-03-01 at 7 59 20 PM" src="https://github.com/reyesp23/gpt-ios-localization/assets/22821919/2048b41f-6ce0-483d-9f2f-d7d254e5a47c">

#### Inputs

| Name             | Description   | Required |
| -------------    |-------------  | -------- |
| OPENAI_KEY       | Key to access OpenAI API | Yes |
| GITHUB_TOKEN     | Github Token to access Github API | Yes |
| HEAD_REF         | Reference (SHA or branch name) of the commit that contains the changes in .strings file | Yes |
| SOURCE_REF       | Reference (SHA or branch name) of the commit that will serve as base for the diff comparison | Yes |
| BASE_LANGUAGE    | Base language code for your translations | Yes |
| TARGET_LANGUAGES | Target language codes separated by comma | Yes |
| LLM_MODEL        | LLM model used for the translation. 'gpt-4' (Default), 'gpt-3.5-turbo' | No |
| PR_BASE_BRANCH   | Base branch for the auto-generated translations PR | Yes |
| PR_TTLE          | Title for the autogenerated translations PR | No |
| PR_BODY          | Body for the autogenerated translations PR | No |
| PR_LABELS        | Labels for the autogenerated translations PR | No |


## Workflow Examples

#### On PR Opened
1. `Feature A` branch opens a PR with `main` as base.
2. String changes in `Feature A` are extracted and localized.
3. A translations PR with `Feature A`as base is auto-generated.

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

#### On PR Merged
1. `Feature A` PR is merged into `main`.
2. String changes in `Feature A` merge commit are extracted and localized.
3. A translations PR with `main`as base is auto-generated.

```yaml
name: Localize - Merged PR
on:
  pull_request:
    types:
      - closed
    branches:
      - main

jobs:
  localize:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: Run Localize Action
        uses: reyesp23/gpt-ios-localization@main
        with:
          HEAD_REF: ${{ github.event.pull_request.merge_commit_sha }}
          SOURCE_REF: ${{ github.event.pull_request.base.sha }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_KEY: ${{ secrets.OPENAI_KEY }}
          BASE_LANGUAGE: 'en'
          TARGET_LANGUAGES: 'it, es'
          PR_BASE_BRANCH: ${{ github.event.pull_request.base.ref }}
```

#### On new Release/ branch
1. A new `Release/` branch is created
2. Strings in the new branch are compared against `main`
3. String changes are extracted and localized.
3. A translations PR with `main`as base is auto-generated.

```yaml
name: Localize - New Release
on:
  create:
    branches:
      - 'release/*'

jobs:
  localize:
    runs-on: ubuntu-latest
    steps:
  
      - name: Run Localize Action
        uses: reyesp23/gpt-ios-localization@main
        with:
          HEAD_REF: ${{ github.sha }}
          SOURCE_REF: 'refs/remotes/origin/main'
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_KEY: ${{ secrets.OPENAI_KEY }}
          BASE_LANGUAGE: 'en'
          TARGET_LANGUAGES: 'it, es'
          PR_BASE_BRANCH: 'main'
```

#### On manual dispatch
1. A manual event is triggered from the Actions menu
2. Strings in 'develop' are compared against `main`
3. String changes are extracted and localized.
3. A translations PR with `main`as base is auto-generated.

```yaml
name: Localize - Manual Run
on:
  workflow_dispatch:
  
jobs:
  localize:
    runs-on: ubuntu-latest
    steps:  
      - name: Run Localize Action
        uses: reyesp23/gpt-ios-localization@main
        with:
          HEAD_REF: 'develop'
          SOURCE_REF: ${{ github.sha }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_KEY: ${{ secrets.OPENAI_KEY }}
          BASE_LANGUAGE: 'en'
          TARGET_LANGUAGES: 'it, es, fr'
          PR_BASE_BRANCH: ${{ github.ref }}
```

## To Do
- Batched translations
- Auto resolving conflicts when having the same translations branch

## 🌐 Languages
- English - en
- Spanish - es
- Italian - it
- French - fr
- German - de
- Dutch - nl
- Russian - ru
- Portuguese - pt
- Chinese Simplified - zh
- Chinese Traditional - zh-Hant
- Japanese - ja
- Korean - ko
- Turkish - tr

## 📃 License
MIT License
