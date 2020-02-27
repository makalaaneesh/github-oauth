from django.shortcuts import render, redirect
from django.http import HttpResponse
from .api import GithubApi
from requests_oauthlib import OAuth2Session
from .analytics import WordCounter, HourCounter
from .oauth_settings import CLIENT_ID, CLIENT_SECRET, AUTHORIZATION_BASE_URL, TOKEN_URL

# Create your views here.
OAUTH_STATE = 'oauth_state'
OAUTH_TOKEN = 'oauth_token'

def index(request):
    return HttpResponse("Hello, World!")


def authorize(request):
    """
    Redirect user to the authorize prompt asking for access for resource
    In this case, we ask the user for access to github API with scope='repo'
    (to include private repos)
    """
    github_oauth_session = OAuth2Session(client_id=CLIENT_ID,)
    authorization_url, state = github_oauth_session.authorization_url(AUTHORIZATION_BASE_URL+"?scope=repo")

    request.session[OAUTH_STATE] = state

    return redirect(authorization_url)


def callback(request):
    """
    Redirection from the authorization prompt.
    This redirection will include the authorization code which will be used to
    get the access token. It also includes the state to be used for verification

    Save the access token in the session and redirect to dashboard.
    """
    github_oauth_session = OAuth2Session(client_id=CLIENT_ID,
                                         state=request.session[OAUTH_STATE])
    access_token_info = github_oauth_session.fetch_token(token_url=TOKEN_URL,
                                                         client_secret=CLIENT_SECRET,
                                                         authorization_response=request.get_full_path())
    request.session[OAUTH_TOKEN] = access_token_info
    return redirect(dashboard)
    # return HttpResponse("This is the callback.")


def dashboard(request):
    """
    Return data that the user is interested in.
    This will use the access token to fetch resources from the github API
    """
    # github_oauth_session = OAuth2Session(client_id=CLIENT_ID,
    #                                      token=request.session[OAUTH_TOKEN])
    # user_info = github_oauth_session.get('https://api.github.com/user').json()
    # events = github_oauth_session.get('https://api.github.com/users/makalaaneesh/events?page=2').json()
    #
    #
    # res = HttpResponse("This is your dashboard.<br><br><br> "
    #                     "Your access token is <br><br>%s<br><br> "
    #                     "Your info is <br><br>%s<br><br>"
    #                     "Your events are <br><br>%s" %
    #                     (request.session[OAUTH_TOKEN],
    #                      user_info,
    #                      events
    #                      ))

    github_api = GithubApi(access_token=request.session[OAUTH_TOKEN])

    # Recent commits
    commits_n = 10
    recent_n_commits = github_api.get_recent_comments(commits_n)
    print(recent_n_commits)

    # Frequent words
    wc = WordCounter()
    wc.process_documents(recent_n_commits)
    words_n = 5
    top_frequent_n_words = wc.get_frequent_words(words_n)

    # Most frequent hour
    hc = HourCounter()
    hc.process_documents(recent_n_commits)
    most_frequent_hour = hc.get_most_frequent_hour()

    context = {
        'commits_n' : commits_n,
        'commits': recent_n_commits,
        'words_n': words_n,
        'frequent_words' : top_frequent_n_words,
        'most_frequent_hour' : most_frequent_hour
    }
    return render(request, 'dashboard.html', context)
    # return HttpResponse("Your top comments are %s" %(recent_10_comments,))
