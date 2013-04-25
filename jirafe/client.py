import requests
import json

class JirafeClient(object):
    def __init__(self, api_url):
        self.api_url = api_url if api_url.endswith('/') else api_url + '/'

    def product_change(self, session, data):
        return self._put(session, 'v1/%s/product' % (session.site_id), data)

    def _put(self, session, path, data, retry=0):
        if type(data) is not str:
            data = json.dumps(data, separators=(',',':'))

        options = {
            "data": data,
            "headers": session.get_header()
        }

        r = requests.put(self.api_url + path, **options)

        if r.status_code is not 200 and retry < 1:
            session.invalidate()
            return self._put(path, data, 1)
        else:
            return r.json()

class JirafeSession(object):
    def __init__(self, username, password, site_id, token_url, client_id, client_secret):
        self.username = username
        self.password = password
        self.site_id = site_id
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def get_header(self):
        self._refresh_token()
        auth_header = 'Bearer %s' % (self.access_token)
        return {'Authorization': auth_header}

    def invalidate(self):
        self.access_token = None

    def _refresh_token(self):
        if self.access_token is not None:
            return self.access_token

        data = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        r = requests.post(self.token_url, data=data)

        if r.status_code is 200:
            self.access_token = r.json()['access_token']
        else:
            self.access_token = None
