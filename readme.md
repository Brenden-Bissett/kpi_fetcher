*This repo is very specific to a project at my last job, and not generalised at all*

# Exact pipeline KPI Tool

This is a cheeky little tool that fetches some metrics from an Azure Devops pipeline (The [Exact YAML one](https://dev.azure.com/henryscheinone/Development/_build?definitionId=139)) for reporting on that.

This is meant to be a supplement to the analytics and reporting that natively come out of Azure Devops, and one day will likely be made obsolete by improvements in their platform (huge fucking 🤞 on that one)

## Example output
```bash

>py main.py

('{\n'
 '    "description": "A collection of average durations from Exact\'s CI '
 'pipeline for runs on master over the last 2 weeks. These are segmented by '
 'passing/failing, as well as a summary of the 10 most recent in each '
 'category.",\n'
 '    "data as of": "2021-09-20T13:45:40.590897",\n'
 '    "data from": "2021-09-06T13:45:40.590897",\n'
 '    "average durations": {\n'
 '        "ten_most_recent": "1 hour and 60 minutes",\n'
 '        "last_two_weeks": "2 hours and 2 minutes",\n'
 '        "last_two_weeks_passing": "2 hours and 17 minutes",\n'
 '        "last_two_weeks_failing": "1 hour and 48 minutes",\n'
 '        "ten_most_recent_passing": "2 hours and 15 minutes",\n'
 '        "ten_most_recent_failing": "1 hour and 54 minutes"\n'
 '    },\n'
 '    "pipeline counts": {\n'
 '        "all_runs_last_two_weeks": 193,\n'
 '        "master_runs_last_two_weeks": 27,\n'
 '        "master_passing_runs_last_two_weeks": 13,\n'
 '        "master_failing_runs_last_two_weeks": 14\n'
 '    },\n'
 '    "passing rates": {\n'
 '        "ten_most_recent": "40%",\n'
 '        "last_two_weeks": "48%"\n'
 '    }\n'
 '}\n'
 '\n'
 '---\n'
 '\n'
 'Passes/runs\n'
 '13/27 -> 48%\n'
 '\n'
 'Two weeks pipeline duration\n'
 '2 hours and 2 minutes')
```

## Why is it cheeky?

* It doesn't even return proper json, just a blob of text that contains json
* It's janky as hell
* Hardcoded config
* Uses someones personal access token XP


## Requirements

* Create ".env" file, with "AZURE_DEVOPS_PAT" property containing API Token. (As set up in Azure Devops)

## Where does it run?

In AWS Lambda, inside the account `soei-sandbox` in the ap-southeast-2 region. [here is a link](https://ap-southeast-2.console.aws.amazon.com/lambda/home?region=ap-southeast-2#/functions/cam_exact_pipeline_duration_kpi).

🔑 - In order to run it needs a *personal access token*. This is provided to the tool via an environment variable named `AZURE_DEVOPS_PAT`, this can be configured in the AWS lambda config page [here](https://ap-southeast-2.console.aws.amazon.com/lambda/home?region=ap-southeast-2#/functions/cam_exact_pipeline_duration_kpi?tab=configure), which any inheritors of this project will need to do, as my tokens will be revoked before 2021-10-01.

🔧 - Configuration is currently managed by a bunch of global variables at the top of [main.py](main.py).

💡 - Ideas for extension could be:
* query parameters to override some options
* path based routing to query different pipelines
* or using environment variables and hosting separate lambdas
* pulling in to an Azure Function app instead of AWS lambda 🤢

---
Good luck, have fun
