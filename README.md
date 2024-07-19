# GitHub Security Alerts Report

This script fetches security alerts from GitHub repositories for a specified organization and generates a comprehensive report in Excel format. The report includes Code Scanning, Dependabot, and Secret Scanning alerts.

## Features

- Fetches security alerts for all repositories in a specified GitHub organization.
- Supports filtering repositories by specific teams within the organization.
- Includes Code Scanning, Dependabot, and Secret Scanning alerts.
- Combines descriptions and severities into unified columns.
- Handles rate limits and retries on request failures.
- Generates a timestamped Excel report.

## Prerequisites

- Python 3.x
- requirements.txt

## Installation

1. Clone this repository:
```sh
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```
2. Create & Activate Python Virtual Env:
```
python -m venv gh-report```
[Mac] source gh-report/bin/activate
[Windows] gh-report\Scripts\activate
```

3. Install required packages: 
```
pip install -r requirements.txt
```

## Usage

1. Update Org and GitHub Personal Access Token

  - Open the script file (gh-report.py) and replace your-personal-access-token with your GitHub Personal Access Token and ORGANIZATION_NAME with your GitHub organization or enter it when prompted

2. Run the script:
```
python gh-report.py
```  

3. Follow prompts:

  - Follow the prompts to enter your organization name and select the team you want to process (or choose "All Teams" to process all teams). 

4. Output:

  - The script will fetch the security alerts and generate an Excel report with a filename in the format alerts_report_{team_slug|all_teams}_{timestamp}.xlsx.

## Example
```
Enter your organization name (default: my-org): my-org
Fetching teams for organization: my-org...

Teams in your organization:
1. Team A
2. Team B
3. All Teams

Enter the number of the team you want to process (or 'All Teams' option): 3
You chose to process all teams.

Fetching repositories for team: team-a...
Fetching repositories for team: team-b...
Total unique repositories found: 10

Processing 1/10: my-org/repo1
Processing 2/10: my-org/repo2
...

Report generated and saved as alerts_report_all_teams_20230716_123456.xlsx
```
