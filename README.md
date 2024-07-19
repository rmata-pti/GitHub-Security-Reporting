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

```python -m venv gh-report```
```[Mac] source gh-report/bin/activate```
```[Windows] gh-report\Scripts\activate```


3. Install required packages: 

-pip install -r requirements.txt
```
## Usage

1. Update Org and GitHub Personal Access Token

```
  - Open the script file (gh-report.py) and replace your-personal-access-token with your GitHub Personal Access Token and ORGANIZATION_NAME with your GitHub organization or enter it when prompted
```
2. Run the script:
```
  - python gh-report.py
```  
3. Follow prompts:
```
  - Follow the prompts to enter your organization name and select the team you want to process (or choose "All Teams" to process all teams). 
```
4. 
