# Find Java + Maven projects on GitHub

import calendar
import json
import os
import requests
import subprocess
import sys
import time
from datetime import datetime
from datetime import date

# OAuth token for GitHub API calls
from config import get_auth_token

def create_file(filepath):
  if not os.path.exists(os.path.dirname(filepath)):
    try:
      os.makedirs(os.path.dirname(filepath))
    except OSError as exc:
      if exc.errno != errno.EEXIST:
          raise

# Create output files 
def create_query_result_output_files():
  query_timestamp = str(calendar.timegm(time.gmtime()))
  global query_results_file
  global output_file
  query_results_file = "./dataset/query_results_" + query_timestamp +".json"
  output_file = "./output/output_" + query_timestamp +".json"
  create_file(query_results_file)
  create_file(output_file)

# Get a list of repos using the GitHub search API
def get_repos():
  response_type = "application/vnd.github.v3+json"

  all_search_items = {}
  all_search_items["items"] = []

  for i in range(1, 11):
    params = {
      'q': ' NOT android in:readme,description NOT leetcode in:readme,description language:Java',
      'sort': 'stars',
      'per_page': '100',
      'page': i
    }
    headers = {
    'Authorization': get_auth_token(),
    'Accept': response_type
    }
    print(params)
    response = requests.get('https://api.github.com/search/repositories', params=params, headers=headers)
    print("URL", response.request.url)
    print("Headers", response.request.headers)
    print("=================================")

    data_from_page = response.json()
    for i in range(len(data_from_page["items"])):
      all_search_items["items"].append(data_from_page["items"][i])
  print("=== Saving a list of", len(all_search_items["items"]), "repos in", query_results_file)
  
  with open(query_results_file, 'w') as json_file:
    json.dump(all_search_items, json_file, indent=2)

def extract_proprietary_info(single_repo_data):
  single_repo = {
    "current_timestamp": calendar.timegm(time.gmtime()),
    "name": single_repo_data["name"],
    "full_name": single_repo_data["full_name"],
    "description": single_repo_data["description"],
    "fork": single_repo_data["fork"],
    "clone_url": single_repo_data["clone_url"],
    "html_url": single_repo_data["html_url"],
    "stargazers_count": single_repo_data["stargazers_count"],
    "language": single_repo_data["language"],
    "default_branch": single_repo_data["default_branch"],
    "size": single_repo_data["size"],
    "candidate": False
  }
  return single_repo

# Clone a repo
def clone_repo(repo_clone_url):
  clone_cmd = "git clone " + repo_clone_url
  print(clone_cmd)
  os.system(clone_cmd)

# Find the build tools used by project 
def find_build_tools():
  find_ant_cmd = "find . -name \"build.xml\" | wc -l"
  find_maven_cmd = "find . -name \"pom.xml\" | wc -l"
  find_gradle_cmd = "find . -name \"build.gradle\" | wc -l"
  build_tools = []
  if int(os.popen(find_ant_cmd).read().strip()) > 0:
    build_tools.append("Ant")
  if int(os.popen(find_maven_cmd).read().strip()) > 0:
    build_tools.append("Maven")
  if int(os.popen(find_gradle_cmd).read().strip()) > 0:
    build_tools.append("Gradle")
  return build_tools

# Find the age of the project
def find_repo_age(created_at, updated_at):
  date_created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").date()
  date_updated_at = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ").date()
  age = (date_updated_at - date_created_at).days
  return age

# Find a subset of Maven projects
def get_maven_projects():
  parent_dir = os.getcwd()
  output = []
  with open(query_results_file, 'r') as json_file:
    repo_data = json.load(json_file)
  print("=== Extracting data...")
  for i in range(len(repo_data["items"])):
    single_repo = extract_proprietary_info(repo_data["items"][i])
    # Clone the repo
    clone_repo(single_repo["clone_url"])
    # cd into project
    os.chdir(parent_dir + "/" + single_repo["name"])
    # Find build tools
    build_tools = find_build_tools()
    if len(build_tools) > 0 and "Maven" in build_tools:
      single_repo["candidate"] = True
      single_repo["build_tools"] = build_tools
      # Find repo age in days
      single_repo["age_days"] = find_repo_age(repo_data["items"][i]["created_at"], repo_data["items"][i]["updated_at"])
    # cd to parent directory
    os.chdir(parent_dir)
    # Remove repo directory
    rm_repo_dir_cmd = "rm -rf " + single_repo["name"]
    os.system(rm_repo_dir_cmd)
    if single_repo["candidate"] == True:
      output.append(single_repo)

  # Save final outputs to file
  with open(output_file, 'w') as json_file:
    json.dump(output, json_file, indent=2)

def main():
  print("=== Creating files...")
  create_query_result_output_files()
  print("=== Finding repos...")
  get_repos()
  print("=== Opening", query_results_file, "to find Maven projects...")
  get_maven_projects()

if __name__ == "__main__":
  main()
