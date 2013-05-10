import json
import requests

class JirafeClient(object):
    version = 'v1'
    url_mask = '{url}{version}/{site_id}/{path}'
    def __init__(self, api_url='https://api.jirafe.com/', requests=requests):
        self.api_url = api_url if api_url.endswith('/') else api_url + '/'
        self.requests = requests

    def category_change(self, session, data):
        return self._put(session, 'category', data)

    def cart_change(self, session, data):
        return self._put(session, 'cart', data)

    def order_change(self, session, data):
        return self._put(session, 'order', data)

    def product_change(self, session, data):
        return self._put(session, 'product', data)

    def customer_change(self, session, data):
        return self._put(session, 'customer', data)

    def _get_url(self, session, path):
        url_data = {
            'url': self.api_url,
            'version': self.version,
            'site_id': session.site_id,
            'path': path,
        }
        return self.url_mask.format(**url_data)

    def _put(self, session, path, data, retry=0):
        if type(data) is not str:
            data = json.dumps(data, separators=(',',':'))

        options = {
            "data": data,
            "headers": session.get_header()
        }
        response = self.requests.put(self._get_url(session, path), **options)


        if response.status_code == 200:
            return {
                'success': True
            }
        elif response.status_code == 400:
            data = response.json()
            return {
                'success': False,
                'error_type': 'validation',
                'errors': data['errors'] if 'errors' in data else {}
            }
        elif response.status_code == 403:
            if retry < 1:
                session.invalidate()
                return self._put(session, path, data, 1)
            else:
                return {
                    'success': False,
                    'error_type': 'authorization'
                }
        else:
            return {
                'success': False,
                'error_type': 'unknown',
            }
