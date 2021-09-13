*This repo is very specific to a project at my last job, and not generalised at all*

# Exact pipeline KPI Tool

This is a cheeky little tool that fetches some metrics from an Azure Devops pipeline (The [Exact YAML one](https://dev.azure.com/henryscheinone/Development/_build?definitionId=139)) for reporting on that.

This is meant to be a supplement to the analytics and reporting that natively come out of Azure Devops, and one day will likely be made obsolete by improvements in their platform (huge fucking 🤞 on that one)

## Why is it cheeky?

* It doesn't even return proper json, just a blob of text that contains json
* It's janky as hell
* Hardcoded config
* Uses someones personal access token XP


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
