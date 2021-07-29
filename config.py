def get_auth_token():
  data = ""
  # Read GitHub PAT from file
  with open('./auth-token.txt', 'r') as file:
    data = file.read().replace('\n', '')
  authorization_token = "token " + data
  return authorization_token
