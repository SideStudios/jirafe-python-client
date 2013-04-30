import requests

class JirafeSession(object):
    def __init__(self,
                 site_id,
                 auth_url='https://accounts.jirafe.com/oauth2/authorize',
                 token_url='https://accounts.jirafe.com/oauth2/access_token',
                 profile_url='https://accounts.jirafe.com/accounts/profile',
                 requests=requests):
        self.access_token = None
        self.site_id = site_id
        self.profile_url = profile_url
        self.token_url = token_url
        self.auth_url = auth_url
        self.requests = requests

    def get_header(self):
        self.update_token()
        auth_header = 'Bearer %s' % (self.access_token)
        return {'Authorization': auth_header}

    def invalidate(self):
        self.access_token = None

    def update_token(self):
        if self.access_token is None:
            self.access_token = self._get_token()
        return self.access_token

    def get_profile(self, retry=0):
        r = self.requests.get(self.profile_url, headers=self.get_header())

        if r.status_code == 403:
            if retry < 1:
                self.invalidate()
                return self.get_profile(1)
        elif r.status_code == 200:
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

        r = self.requests.post(self.token_url, data=data)

        if r.status_code is 200:
            return r.json()['access_token']

class Oauth2Session(JirafeSession):
    def __init__(self, site_id, client_id, client_secret, code=None, refresh_token=None, access_token=None, **kwargs):
        super(Oauth2Session, self).__init__(site_id, **kwargs)
        self.code = code
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret

    def get_refresh_token(self):
        self.update_token()
        return self.refresh_token

    def _get_token(self):
        if self.access_token is not None:
            return self.access_token

        if self.refresh_token is not None:
            data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
            }
            return self._do_post(data)

        if self.code is not None:
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': self.code,
            }
            return self._do_post(data)

    def _do_post(self, data):
        r = self.requests.post(self.token_url, data=data)

        if r.status_code is 200:
            self.code = None
            self.refresh_token = r.json()['refresh_token']
            return r.json()['access_token']
