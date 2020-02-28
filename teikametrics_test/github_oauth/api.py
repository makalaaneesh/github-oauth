from .oauth_settings import CLIENT_ID
from requests_oauthlib import OAuth2Session
from cached_property import cached_property
from abc import ABC, abstractmethod
from datetime import datetime

USER_INFO_URL = 'https://api.github.com/user'
EVENTS_INFO_URL = "https://api.github.com/users/{username}/events?page={page}"


class IHasText(ABC):
    """
    To be implemented by classes that have a textual attribute
    """
    @abstractmethod
    def get_text(self):
        pass


class IHasCreatedTime(ABC):
    """
    To be implemented by classes that have a time(created) attribute
    """
    @abstractmethod
    def get_created_time(self):
        pass


class Commit(IHasText, IHasCreatedTime):
    """
    A github commit
    """
    def __init__(self,
                 sha,
                 repo,
                 author,
                 text,
                 created_at):
        datetime_format = "%Y-%m-%dT%H:%M:%SZ" # 2020-02-06T12:02:05Z
        self.sha = sha
        self.author = author
        self.repo = repo
        self.text = text
        self.created_at = datetime.strptime(created_at,
                                            datetime_format)

    def __repr__(self):
        return "{text} - {time}".format(text=self.get_text(),
                                        time=self.get_created_time())

    @classmethod
    def parse_api_payload(cls, repo, created_at, payload):
        """
        Parses the PushEvent payload and returns a L{Commit} object

        :param repo: repo name
        :param created_at: time the event was created at
        :param payload: payload from the PushEvent
        :return: L{Commit} object
        """
        return Commit(sha=payload['sha'],
                      author=payload['author'],
                      repo=repo,
                      text=payload['message'],
                      created_at=created_at)

    def get_text(self):
        return self.text

    def get_created_time(self):
        return self.created_at


class GithubApi:
    """
    Retrieves high level information by making use of the
    github APIs (for example, user, events, etc)
    """
    def __init__(self,
                 access_token):
        """
        :param access_token: Access Token obtained after authorizing user
        """
        self.github_oauth_session = OAuth2Session(client_id=CLIENT_ID,
                                                  token=access_token)

    @cached_property
    def username(self):
        """
        :return: username associated with the access token
        """
        user_info = self.github_oauth_session.get(USER_INFO_URL).json()
        return user_info['login']

    def _get_events(self, page):
        """
        Get events from page number

        :param page: page number
                The fixed page size is 30 items. Fetching up to ten pages is supported,
                for a total of 300 events.
        :return: list of events
        """
        if page > 10 or page < 1:
            raise ValueError("Invalid page number %s. Valid page numbers = 1-10"
                             %(page,))

        events_info_url = EVENTS_INFO_URL.format(username=self.username,
                                                 page=page)
        events_info = self.github_oauth_session.get(url=events_info_url).json()

        return events_info

    def _get_commits(self, page, n):
        """
        Filters the events to find PushEvents (corresponding to some commit pushes),
        retrieves the commits from those PushEvents and returns.

        :param page: page number
                The fixed page size is 30 items. Fetching up to ten pages is supported,
                for a total of 300 events.
        :param n: how many to fetch
        :return: list of L{Commit} objects
        """
        events_info = self._get_events(page)
        commit_events_info = [event_info for event_info in events_info
                              if event_info['type'] == 'PushEvent']
        commits = []

        for commit_event_info in commit_events_info:
            if len(commits) >= n:
                break
            repo = commit_event_info['repo']
            created_at = commit_event_info['created_at']
            commits_payload = commit_event_info['payload']['commits']
            for commit_payload in commits_payload:
                commits.append(Commit.parse_api_payload(repo,
                                                        created_at,
                                                        commit_payload))
        return commits

    def get_recent_commits(self, n):
        """
        Get the n most recent commits made by user.

        :param n: how many
        :return: list of L{Commit} objects
        """
        valid_pages = range(1, 11)
        commits = []
        for page in valid_pages:
            page_commits = self._get_commits(page, n-len(commits))
            commits.extend(page_commits)
            if len(commits) >= n:
                break
        return commits[:n]



