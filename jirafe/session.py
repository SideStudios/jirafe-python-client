import requests

class JirafeSession(object):
    def __init__(self,
                 site_id,
                 auth_url='https://accounts.jirafe.com/oauth2/auth',
                 token_url='https://accounts.jirafe.com/oauth2/access_token',
                 profile_url='https://accounts.jirafe.com/accounts/profile'):
        self.access_token = None
        self.site_id = site_id
        self.profile_url = profile_url
        self.token_url = token_url
        self.auth_url = auth_url

    def get_header(self):
        self.refresh_token()
        auth_header = 'Bearer %s' % (self.access_token)
        return {'Authorization': auth_header}

    def invalidate(self):
        self.access_token = None

    def refresh_token(self):
        if self.access_token is None:
            self.access_token = self._get_token()
        return self.access_token

    def get_profile(self, retry=0):
        r = requests.get(self.profile_url, headers=self.get_header())

        if r.status_code is not 200 and retry < 1:
            self.invalidate()
            return self.get_profile(1)
        else:
            return r.json()

    def get_site(self):
        profile = self.get_profile()

        if profile and 'sites' in profile:
            try:
                return next(s for s in profile['sites'] if s['id'] == self.site_id)
            except StopIteration:
                pass

    def _get_token(self):
        raise NotImplementedError

class UsernameSession(JirafeSession):
    def __init__(self, site_id, username, password, client_id, client_secret, **kwargs):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        super(UsernameSession, self).__init__(site_id, **kwargs)

    def _get_token(self):
        data = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        r = requests.post(self.token_url, data=data)

        if r.status_code is 200:
            return r.json()['access_token']

class AuthorizationHeaderSession(JirafeSession):
    def __init__(self, site_id, auth_header, **kwargs):
        self.auth_header = auth_header
        super(AuthorizationHeaderSession, self).__init__(site_id, **kwargs)

    def _get_token(self):
        if self.auth_header is None:
            return None

        values = self.auth_header.split(' ')

        if len(values) is not 2:
            return None

        if values[0].lower() == 'bearer':
            return values[1]
