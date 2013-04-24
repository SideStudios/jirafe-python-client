import requests

class JirafeClient(object):
    def __init__(self, api_url, client_id, client_secret, token_url, username, password):
        self.api_url = api_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.username = username
        self.password = password
        self.access_token = None

    def product_change(self, site_id, data):
        return self._put('v1/%s/product' % (site_id), data)

    def _put(self, path, data, retry=0):
        r = requests.put(self.api_url + path, data=data, headers=self._get_header())

        if r.status_code is not 200 and retry < 1:
            return self._put(path, data, 1)
        else:
            return r.json()

    def _get_header(self):
        self._refresh_token()
        auth_header = 'Bearer %s' % (self.access_token)
        return {'Authorization': auth_header}

    def _refresh_token(self):
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
