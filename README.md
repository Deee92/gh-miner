### Use the GitHub search API to find projects

#### Running:
- Create an `./auth-token.txt` for the [Personal Access Token](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Authenticating with PAT](https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api#authentication)
- Then, either of:
  - `python3 mine-without-clone.py` (Uses the `search/code` API to find Maven projects, relatively faster)
  - `python3 mine.py` (Clones repositories to find Maven projects, potentially more detail)
