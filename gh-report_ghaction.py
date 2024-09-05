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
    rate_limit = response.json()
    return rate_limit

# Function to handle rate limit exceeded
def handle_rate_limit():
    rate_limit = check_rate_limit()
    remaining_requests = rate_limit['rate']['remaining']
    reset_time = rate_limit['rate']['reset']
    if remaining_requests == 0:
        reset_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reset_time))
        print(f"Rate limit exceeded. Pausing until {reset_timestamp}.")
        time_to_wait = max(0, reset_time - time.time() + 1)  # Add 1 second buffer
        time.sleep(time_to_wait)

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

# Function to get repositories for a specific team
def get_team_repos(org_name, team_slug):
    repos = []
    page = 1
    while True:
        handle_rate_limit()
        try:
            response = http.get(f"{GITHUB_API_URL}/orgs/{org_name}/teams/{team_slug}/repos?page={page}&per_page=100", headers=headers, timeout=30)
            response.raise_for_status()
            response_data = response.json()
            if not response_data:
                break
            repos.extend(response_data)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repositories for team {team_slug}: {e}")
            break
    return repos

# Function to get code scanning alerts for a repository
def get_code_scanning_alerts(repo_full_name):
    alerts = []
    page = 1
    while True:
        handle_rate_limit()
        try:
            response = http.get(f"{GITHUB_API_URL}/repos/{repo_full_name}/code-scanning/alerts?page={page}&per_page=100", headers=headers, timeout=30)
            response.raise_for_status()
            response_data = response.json()
            if not response_data:
                break
            alerts.extend(response_data)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching code scanning alerts for {repo_full_name}: {e}")
            break
    return alerts

# Function to get dependabot alerts for a repository
def get_dependabot_alerts(repo_full_name):
    alerts = []
    page = 1
    while True:
        handle_rate_limit()
        try:
            response = http.get(f"{GITHUB_API_URL}/repos/{repo_full_name}/dependabot/alerts?page={page}&per_page=100", headers=headers, timeout=30)
            response.raise_for_status()
            response_data = response.json()
            if not response_data:
                break
            alerts.extend(response_data)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching dependabot alerts for {repo_full_name}: {e}")
            break
    return alerts

# Function to get secret scanning alerts for a repository
def get_secret_scanning_alerts(repo_full_name):
    alerts = []
    page = 1
    while True:
        handle_rate_limit()
        try:
            response = http.get(f"{GITHUB_API_URL}/repos/{repo_full_name}/secret-scanning/alerts?page={page}&per_page=100", headers=headers, timeout=30)
            response.raise_for_status()
            response_data = response.json()
            if not response_data:
                break
            alerts.extend(response_data)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching secret scanning alerts for {repo_full_name}: {e}")
            break
    return alerts

# Get all teams in the organization
print(f"Fetching teams for organization: {ORGANIZATION_NAME}...")
teams = get_teams(ORGANIZATION_NAME)
team_slugs = [team['slug'] for team in teams]

if not teams:
    print("No teams found or access denied. Please check your token permissions.")
else:
    for team_slug in team_slugs:
        print(f"\nProcessing team: {team_slug}")
        
        # Get repositories for the current team
        team_repos = get_team_repos(ORGANIZATION_NAME, team_slug)
        total_repos = len(team_repos)
        print(f"Total repositories for team {team_slug}: {total_repos}")

        # Prepare the report data
        report_data = []

        for index, repo in enumerate(team_repos, start=1):
            repo_name = repo['name']
            full_repo_name = repo['full_name']
            print(f"Processing {index}/{total_repos}: {full_repo_name}")
            code_scanning_alerts = get_code_scanning_alerts(full_repo_name)
            dependabot_alerts = get_dependabot_alerts(full_repo_name)
            secret_scanning_alerts = get_secret_scanning_alerts(full_repo_name)
            for alert in code_scanning_alerts:
                report_data.append({
                    "Repository": repo_name,
                    "Alert Type": "Code Scanning",
                    "Alert Number": alert["number"],
                    "Description": alert["rule"]["description"],
                    "Severity": alert["rule"]["severity"],
                    "State": alert["state"],
                    "Created At": alert["created_at"],
                    "Updated At": alert["updated_at"],
                    "URL": alert["html_url"]
                })
            for alert in dependabot_alerts:
                report_data.append({
                    "Repository": repo_name,
                    "Alert Type": "Dependabot",
                    "Alert Number": alert["number"],
                    "Description": alert["security_advisory"]["description"] if "description" in alert["security_advisory"] else "N/A",
                    "Severity": alert["security_advisory"]["severity"],
                    "Package Name": alert["security_advisory"]["package"]["name"] if "package" in alert["security_advisory"] else "N/A",
                    "Vulnerable Version Range": alert["vulnerable_version_range"] if "vulnerable_version_range" in alert else "N/A",
                    "Patched Version": alert["security_advisory"]["patched_versions"] if "patched_versions" in alert["security_advisory"] else "N/A",
                    "State": alert["state"],
                    "Created At": alert["created_at"],
                    "Updated At": alert["updated_at"],
                    "URL": alert["html_url"]
                })
            for alert in secret_scanning_alerts:
                report_data.append({
                    "Repository": repo_name,
                    "Alert Type": "Secret Scanning",
                    "Alert Number": alert["number"],
                    "Description": alert["secret_type_display_name"],
                    "Severity": "N/A",  # Secret Scanning alerts do not have severity information
                    "State": alert["state"],
                    "Created At": alert["created_at"],
                    "Updated At": alert["updated_at"],
                    "URL": alert["html_url"]
                })
            time.sleep(0.5)  # Adjusting the delay to avoid hitting the API rate limit

        # Convert to a DataFrame
        df = pd.DataFrame(report_data)

        # Add date and time to the report filename
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"alerts_report_{team_slug}_{current_time}.xlsx"

        # Save to an Excel file with the team slug as a suffix
        df.to_excel(report_filename, index=False)

        print(f"Report generated and saved as {report_filename}")

