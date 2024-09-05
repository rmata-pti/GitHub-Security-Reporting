import requests
import pandas as pd
import time
from datetime import datetime
import openpyxl  # Ensure openpyxl is imported
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

# GitHub API URL
GITHUB_API_URL = "https://api.github.com"

# Organization name
ORGANIZATION_NAME = "provenancetech"

# GitHub Token from environment variable (GitHub Actions secret)
ACCESS_TOKEN = os.getenv('GH_TOKEN')

if ACCESS_TOKEN is None:
    raise ValueError("GitHub token (GH_TOKEN) is not set in the environment variables.")

# Headers for authentication
headers = {
    "Authorization": f"token {ACCESS_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Configure retries and backoff strategy
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# Function to check rate limit status
def check_rate_limit():
    response = http.get(f"{GITHUB_API_URL}/rate_limit", headers=headers)
    
    # Check if the response was successful
    if response.status_code != 200:
        print(f"Error checking rate limit: {response.status_code} {response.text}")
        return None
    
    try:
        rate_limit = response.json()
        return rate_limit
    except ValueError:
        print(f"Failed to parse rate limit response: {response.text}")
        return None

# Function to handle rate limit exceeded
def handle_rate_limit():
    rate_limit = check_rate_limit()
    
    if rate_limit and 'rate' in rate_limit:
        remaining_requests = rate_limit['rate']['remaining']
        reset_time = rate_limit['rate']['reset']
        if remaining_requests == 0:
            reset_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reset_time))
            print(f"Rate limit exceeded. Pausing until {reset_timestamp}.")
            time_to_wait = max(0, reset_time - time.time() + 1)  # Add 1 second buffer
            time.sleep(time_to_wait)
    else:
        print("Unable to check rate limit; proceeding without rate limit check.")

# Function to get the list of teams in the organization
def get_teams(org_name):
    teams = []
    page = 1
    while True:
        handle_rate_limit()
        try:
            response = http.get(f"{GITHUB_API_URL}/orgs/{org_name}/teams?page={page}&per_page=100", headers=headers, timeout=30)
            response.raise_for_status()
            response_data = response.json()
            if not response_data:
                break
            teams.extend(response_data)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching teams: {e}")
            break
    return teams

# Remaining code for fetching repositories, alerts, etc. (unchanged)

# Main script logic
if __name__ == "__main__":
    print(f"Fetching teams for organization: {ORGANIZATION_NAME}...")
    
    teams = get_teams(ORGANIZATION_NAME)
    
    if not teams:
        print("No teams found or access denied. Please check your token permissions.")
    else:
        for team_slug in [team['slug'] for team in teams]:
            print(f"\nProcessing team: {team_slug}")
            # Process the team's repositories and generate reports (as per original code)
