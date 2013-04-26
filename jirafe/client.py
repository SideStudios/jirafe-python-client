import json
import requests

class JirafeClient(object):
    version = 'v1'
    def __init__(self, api_url='https://api.jirafe.com'):
        self.api_url = api_url if api_url.endswith('/') else api_url + '/'

    def product_change(self, session, data):
        return self._put(session, 'product', data)

    def _put(self, session, path, data, retry=0):
        if type(data) is not str:
            data = json.dumps(data, separators=(',',':'))

        options = {
            "data": data,
            "headers": session.get_header()
        }

        r = requests.put('%s%s/%s/%s' % (self.api_url, self.version, session.site_id, path), **options)

        if r.status_code not in (200,503) and retry < 1:
            session.invalidate()
            return self._put(session, path, data, 1)
        else:
            return r.text
