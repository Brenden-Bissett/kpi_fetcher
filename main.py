import json
import os
from datetime import date, datetime, timedelta
from pprint import pprint
from dotenv import load_dotenv
import logging

import requests
import humanize
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

# Gets or creates a logger
logger = logging.getLogger(__name__)  

# set log level
logger.setLevel(logging.INFO)

# define file handler and set formatter
file_handler = logging.FileHandler('logfile.log')
formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)

ORG_URL = "https://dev.azure.com/henryscheinone/Development/_apis"
API_VERSION = "?api-version=6.1-preview.1"
PIPELINE_ID_EXACT_CI = 139

load_dotenv()

SESSION = requests.Session()
SESSION.auth = HTTPBasicAuth("", os.environ.get("AZURE_DEVOPS_PAT"))
SESSION.headers.update({"content-type": "application/json"})

def main(event, context):
    counts = {}
    pipeline_list = SESSION.get(
        f"{ORG_URL}/pipelines/{PIPELINE_ID_EXACT_CI}/runs{API_VERSION}"
    ).json()["value"]

    # Filter this list down so we don't make too many calls out
    pipeline_list = [x for x in pipeline_list if x["state"] == "completed"]
    pipeline_list = [x for x in pipeline_list if x["result"] != "canceled"]
    pipeline_list = [x for x in pipeline_list if is_recent(x)]
    counts["all_runs_last_two_weeks"] = len(pipeline_list)

    print(f"Found {len(pipeline_list)} pipeline runs...")

    print("Fetching details")
    # Now fetch some details for each, and stash them onto the same dict
    for run in tqdm(pipeline_list):
        run.update(
            SESSION.get(
                f"{ORG_URL}/pipelines/{PIPELINE_ID_EXACT_CI}/runs/{run['id']}{API_VERSION}"
            ).json()
        )
        process_run(run)

    # Further filtering using the extra data available
    pipeline_list = [x for x in pipeline_list if is_master(x)]
    counts["master_runs_last_two_weeks"] = len(pipeline_list)

    # Segment in interesting ways
    segments = {}
    segments["ten_most_recent"] = pipeline_list[:10]
    segments["last_two_weeks"] = pipeline_list
    segments["last_two_weeks_passing"] = [
        x for x in pipeline_list if x["result"] == "succeeded"
    ]
    segments["last_two_weeks_failing"] = [
        x for x in pipeline_list if x["result"] == "failed"
    ]
    segments["ten_most_recent_passing"] = segments["last_two_weeks_passing"][:10]
    segments["ten_most_recent_failing"] = segments["last_two_weeks_failing"][:10]
    counts["master_passing_runs_last_two_weeks"] = len(
        segments["last_two_weeks_passing"]
    )
    counts["master_failing_runs_last_two_weeks"] = len(
        segments["last_two_weeks_failing"]
    )
    # Cheeky var cause I don't want this in the counts or segments reports
    ten_most_recent_pass_rate = (
        len([x for x in segments["ten_most_recent"] if x["result"] == "succeeded"]) / 10
    )

    segmented_durations = {}
    for k, v in segments.items():
        # print(f"{k=}, {len(v)=}")
        segmented_durations[k] = humanize.precisedelta(
            get_average_duration(v),
            minimum_unit="minutes",
            format="%0.0f",
        )
    passing_rates = {
        "ten_most_recent": "{:.0f}%".format(ten_most_recent_pass_rate * 100),
        "last_two_weeks": "{:.0f}%".format(
            counts["master_passing_runs_last_two_weeks"]
            / counts["master_runs_last_two_weeks"]
            * 100
        ),
    }
    return json.dumps(
        {
            "description": (
                "A collection of average durations from Exact's CI pipeline for runs "
                "on master over the last 2 weeks. These are segmented by passing/"
                "failing, as well as a summary of the 10 most recent in each category."
            ),
            "data as of": datetime.now().isoformat(),
            "data from": (datetime.now() - timedelta(weeks=2)).isoformat(),
            "average durations": segmented_durations,
            "pipeline counts": counts,
            "passing rates": passing_rates,
        },
        indent=4,
        sort_keys=False,
    ) + (
        f"\n\n---\n\nPasses/runs\n{counts['master_passing_runs_last_two_weeks']}/"
        f"{counts['master_runs_last_two_weeks']} -> {passing_rates['last_two_weeks']}"
        f"\n\nTwo weeks pipeline duration\n{segmented_durations['last_two_weeks']}"
    )


def process_run(run):
    """
    Mutating
    """
    run["createdDate"] = datetime.fromisoformat(run["createdDate"][:16])
    run["finishedDate"] = datetime.fromisoformat(run["finishedDate"][:16])
    run["duration"] = run["finishedDate"] - run["createdDate"]


def get_average_duration(run_list):
    return sum([x["duration"] for x in run_list], timedelta(0)) / len(run_list)


def is_master(run_detail):

    try:

        if (
            run_detail["resources"]["repositories"]["self"]["refName"]
            == "refs/heads/master"
        ):
            return True
        return False

    except Exception as e:
        logger.info(run_detail)
        logger.error(f'{e}')
    
    return False

def is_recent(run):
    age = datetime.now() - datetime.fromisoformat(run["createdDate"][:16])
    if age <= timedelta(weeks=2):
        return True
    return False


if __name__ == "__main__":
    pprint(main(None, None))
