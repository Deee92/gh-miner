# Find Java projects built with Maven

# curl -H "Accept: application/vnd.github.v3+json Authorization: token <PAT>" "https://api.github.com/search/repositories?q=language:java+NOT+android+in:description,readme&per_page=2&page=1&sort:stars"
# curl -H "Accept: application/vnd.github.v3+json Authorization: token <PAT>" "https://api.github.com/search/code?q=filename:pom+extension:xml+repo:full/name&per_page=1&page=1"

import argparse
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

# Parse command-line args
def parse_cli_args(args):
  global filename, extension, min_stars, max_stars
  filename = args.filename
  extension = args.extension
  min_stars = args.min
  max_stars = args.max

# Get repository language
def get_repo_language():
  if filename == "pom" and extension == "xml":
    return " language:java"
  else:
    return ""

# Find in README and description
def find_in_readme_description():
  if filename == "graphql" and extension == "schema":
    return " GraphQL in:readme,description"
  else:
    return ""

# Get query string for filename and extension
def get_filename_extension():
  return "filename:" + filename + " extension:" + extension + " "

# Get query string for range of stars, if provided in the CLI
def get_stars_query_string():
  if min_stars > 0 and max_stars > 0:
    return " stars:" + str(min_stars) + ".." + str(max_stars)
  elif min_stars > 0 and max_stars == 0:
    return " stars:>=" + str(min_stars)
  elif min_stars == 0 and max_stars > 0:
    return " stars:<=" + str(max_stars)
  else:
    return ""

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

# Get a list of repos with the search/repositories API
def get_list_of_repos():
  all_search_items = {}
  all_search_items["items"] = []
  global number_of_repos

  for i in range(1, 11):
    params = {
      'q': 'NOT leetcode in:readme,description' + find_in_readme_description() + get_repo_language() + get_stars_query_string(),
      'sort': 'stars',
      'per_page': '100',
      'page': i
    }
    headers = {
      'Authorization': auth_token,
      'Accept': response_type
    }
    print(params)
    response = requests.get('https://api.github.com/search/repositories', params=params, headers=headers)
    print("URL", response.request.url)
    print("Headers", response.request.headers)
    print("=================================")

    data_from_page = response.json()
    for i in range(len(data_from_page["items"])):
      this_repo = data_from_page["items"][i]
      skip_words = ["android", "sample", "demo", "tutorial", "example"]
      if not any(skip_word in this_repo["full_name"].lower() for skip_word in skip_words):
        all_search_items["items"].append(this_repo)
    number_of_repos = len(all_search_items["items"])
  print("=== Saving a list of", number_of_repos, "repos in", query_results_file)
  
  with open(query_results_file, 'w') as json_file:
    json.dump(all_search_items, json_file, indent=2)

# Get ready-made info for a repo
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
    "updated_at": single_repo_data["updated_at"],
    "size": single_repo_data["size"]
  }
  return single_repo

# Find the age of the project
def find_repo_age(created_at, updated_at):
  date_created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").date()
  date_updated_at = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ").date()
  age = (date_updated_at - date_created_at).days
  return age

# Find repos with filename.extension files with the search/code API
def find_repos_with_filename_extension(full_name):
  params = {
    'q': get_filename_extension() + 'repo:' + full_name,
    'per_page': 1,
    'page': 1
  }
  headers = {
    'Authorization': auth_token,
    'Accept': response_type
  }
  print(params)
  response = requests.get('https://api.github.com/search/code', params=params, headers=headers)
  print("URL", response.request.url)
  print("Headers", response.request.headers)
  response_data = response.json()
  # print(response_data)
  print("Total count:", response_data["total_count"])
  return (response_data["total_count"] > 0)

# Generate a subset of projects that meet all criteria
def get_projects():
  parent_dir = os.getcwd()
  output = []
  with open(query_results_file, 'r') as json_file:
    repo_data = json.load(json_file)
  print("=== Extracting data after a minute-long nap...")
  time.sleep(60)
  for i in range(len(repo_data["items"])):
    single_repo = extract_proprietary_info(repo_data["items"][i])
    if ((i + 1) % 30) == 0:
      print("=== Rate limit of 30 requests per minute reached. Resetting...")
      time.sleep(60)
    print("=== Finding", filename + "." + extension, "files in", single_repo["full_name"], "- repo", (i + 1), "of", number_of_repos)
    if (find_repos_with_filename_extension(single_repo["full_name"]) == True):
      print("=== Found at least one", filename + "." + extension, "in", single_repo["full_name"])
      single_repo["age_days"] = find_repo_age(repo_data["items"][i]["created_at"], repo_data["items"][i]["updated_at"])
      filename_extension_key = "has_" + filename + "_" + extension
      single_repo[filename_extension_key] = True
      output.append(single_repo)
    else:
      print("=== Did not find", filename + "." + extension, "in", single_repo["full_name"])
    print("=================================")

  # Save final outputs to file
  print("=== Saving a list of", len(output), "repos in", output_file)
  with open(output_file, 'w') as json_file:
    json.dump(output, json_file, indent=2)

def main(argv):
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--filename', type=str, metavar="filename", default="pom", help='name of search file')
  parser.add_argument('-e', '--extension', type=str, metavar="extension", default="xml", help='extension of search file')
  parser.add_argument('--min', type=int, metavar="min-stars", default=0, help='minimum number of stars')
  parser.add_argument('--max', type=int, metavar="max-stars", default=0, help='maximum number of stars')
  args = parser.parse_args()
  parse_cli_args(args)
  global auth_token
  auth_token = get_auth_token()
  global response_type
  response_type = "application/vnd.github.v3+json"
  print("=== Creating files...")
  create_query_result_output_files()
  print("=== Finding repos...")
  get_list_of_repos()
  print("=== Opening", query_results_file, "to find projects with at least one", filename + "." + extension, "file...")
  get_projects()

if __name__ == "__main__":
  main(sys.argv[1:])
