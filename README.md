# github-oauth
A simple example of a webapp using github oauth to fetch recent commits and compute some metrics

## Setup
1. Set up a virtualenv
  `virtualenv venv` and activate `source venv/bin/activate`
2. `pip install -r requirements.txt`
3. Create a file `oauth_settings.py` under `teikametrics_test/github_oauth` with the following content
```
CLIENT_ID = "xyz" # the client id of the github oauth app
CLIENT_SECRET = "xyz" # the client secret of the github oauth app

AUTHORIZATION_BASE_URL = 'https://github.com/login/oauth/authorize'
TOKEN_URL = 'https://github.com/login/oauth/access_token'

```
4. set env `OAUTHLIB_INSECURE_TRANSPORT=1` This is so that python library 'oauthlib' works fine without SSL
5. `cd teikametrics_test` and `python manage.py runserver`
6. Visit `http://localhost:8000/github_oauth/`
