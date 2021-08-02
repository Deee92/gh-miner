### Use the GitHub search API to find projects

#### Running:
- Create an `./auth-token.txt` for the [Personal Access Token](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Authenticate with PAT](https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api#authentication)
- Then, either:
  - Use the [`search/code`](https://docs.github.com/en/rest/reference/search#search-code) API to find projects, relatively faster
  ```
  python3 mine-without-clone.py -f, --filename <name of file to search for, default "pom">
                                -e, --extension <extension of file to search for, default "xml">
                                --min <number of stars, default (none)>
                                --max <number of stars, default (none)>
  ```
  **Example**: `python3 mine-without-clone.py -f schema -e graphql --min 300`

  - \[not maintained\] Clone repositories to find Maven projects, potentially more detail: `python3 mine.py`
