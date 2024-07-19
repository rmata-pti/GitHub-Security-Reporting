import requests
import pandas as pd
import time
from datetime import datetime
import openpyxl  # Ensure openpyxl is imported
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# GitHub API URL
GITHUB_API_URL = "https://api.github.com"

# Replace with your Org & Token settings
ORGANIZATION_NAME = "my-GitHub-organization"
ACCESS_TOKEN = "your-github-personal-access-token"

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

# Prompt user for organization name with a default value
default_org = ORGANIZATION_NAME
org_input = input(f"Enter your organization name (default: {default_org}): ")
ORGANIZATION_NAME = org_input.strip() or default_org

# Get all teams in the organization
print(f"Fetching teams for organization: {ORGANIZATION_NAME}...")
teams = get_teams(ORGANIZATION_NAME)
team_slugs = [team['slug'] for team in teams]

if not teams:
    print("No teams found or access denied. Please check your token permissions.")
else:
    # Prompt user to select a specific team or all teams
    print("\nTeams in your organization:")
    for i, team in enumerate(teams):
        print(f"{i + 1}. {team['name']}")

    print(f"{len(teams) + 1}. All Teams")

    team_choice = int(input("\nEnter the number of the team you want to process (or 'All Teams' option): "))

    if team_choice == len(teams) + 1:
        selected_team_slugs = team_slugs
        report_suffix = "all_teams"
        print("You chose to process all teams.")
    else:
        selected_team_slugs = [team_slugs[team_choice - 1]]
        report_suffix = teams[team_choice - 1]['slug']
        print(f"You chose to process team: {teams[team_choice - 1]['name']}")

    # Get all repositories for the selected teams
    all_repos = []
    for team_slug in selected_team_slugs:
        print(f"\nFetching repositories for team: {team_slug}...")
        team_repos = get_team_repos(ORGANIZATION_NAME, team_slug)
        all_repos.extend(team_repos)

    # Remove duplicate repositories
    all_repos = {repo['full_name']: repo for repo in all_repos}.values()
    total_repos = len(all_repos)
    print(f"\nTotal unique repositories found: {total_repos}")

    # Prepare the report data
    report_data = []

    for index, repo in enumerate(all_repos, start=1):
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
    report_filename = f"alerts_report_{report_suffix}_{current_time}.xlsx"

    # Save to an Excel file with the team name as a suffix
    df.to_excel(report_filename, index=False)

    print(f"\nReport generated and saved as {report_filename}")
