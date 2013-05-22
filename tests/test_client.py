from mock import Mock, call
import requests
import unittest
from jirafe import JirafeClient

class TestJirafeSession(unittest.TestCase):
    def setUp(self):
        self.requests = Mock()
        self.client = JirafeClient(requests=self.requests)

    def test_constructor_defaults(self):
        client = JirafeClient()
        self.assertEqual('https://api.jirafe.com/', client.api_url)
        self.assertEqual(requests, client.requests)

    def test_constructor_change(self):
        url = 'http://example.com/'
        r = Mock()
        client = JirafeClient(url, r)
        self.assertEqual(url, client.api_url)
        self.assertEqual(r, client.requests)

    def test_constructor_trailing_slash(self):
        client = JirafeClient('http://no-slash.com')
        self.assertEqual('http://no-slash.com/', client.api_url)

    def test_product_change(self):
        response = Mock()
        self.client._put = Mock(return_value=response)
        session = Mock()
        data = {}
        self.assertEqual(response, self.client.product_change(session, data))
        self.client._put.assert_called_once_with(session, 'product', data)

    def test__get_url(self):
        session = Mock()
        session.site_id = 'id'
        path = 'foo'
        self.assertEqual('https://api.jirafe.com/v1/id/foo', self.client._get_url(session, path))

    def test_happy_put(self):
        path = 'foo'
        url = 'https://api.jirafe.com/v1/id/foo'
        data_string = '{"bar":"baz"}'
        auth_header = "some header"
        session = Mock()
        session.site_id = 'id'
        session.get_header = Mock(return_value=auth_header)
        options = {
            "data": data_string,
            "headers": auth_header
        }
        json_response = {'success': True}
        mock_response = Mock()
        mock_response.json = Mock(return_value=json_response)
        self.requests.put = Mock(return_value=mock_response)
        mock_response.status_code = 200

        actual_response = self.client._put(session, path, data_string)

        self.requests.put.assert_called_with(url, **options)
        self.assertEqual(json_response, actual_response)

    def test_put_converts_dict_to_string(self):
        data = {'bar': 'baz'}
        data_string = '{"bar":"baz"}'
        auth_header = "some header"
        session = Mock()
        session.site_id = 'id'
        session.get_header = Mock(return_value=auth_header)
        options = {
            "data": data_string,
            "headers": auth_header
        }

        self.client._put(session, '', data)

        self.requests.put.assert_called_with('https://api.jirafe.com/v1/id/', **options)

    def test_put_validation_error(self):
        path = 'foo'
        url = 'https://api.jirafe.com/v1/id/foo'
        data_string = '{"bar":"baz"}'
        auth_header = "some header"
        session = Mock()
        session.site_id = 'id'
        session.get_header = Mock(return_value=auth_header)
        options = {
            "data": data_string,
            "headers": auth_header
        }
        errors = {
            'foo': 'foo error',
            'bar': 'bar error',
        }
        json_response = {'success': False, 'error_type': 'validation', 'errors': errors}
        put_response = {'errors': errors}
        mock_response = Mock()
        mock_response.json = Mock(return_value=put_response)
        mock_response.status_code = 400
        self.requests.put = Mock(return_value=mock_response)

        actual_response = self.client._put(session, path, data_string)

        self.requests.put.assert_called_with(url, **options)
        self.assertEqual(json_response, actual_response)

    def test_put_authorization_error(self):
        path = 'foo'
        url = 'https://api.jirafe.com/v1/id/foo'
        data_string = '{"bar":"baz"}'
        auth_header = "some header"
        session = Mock()
        session.site_id = 'id'
        session.get_header = Mock(return_value=auth_header)
        options = {
            "data": data_string,
            "headers": auth_header
        }
        json_response = {'success': False, 'error_type': 'authorization'}
        mock_response = Mock()
        mock_response.status_code = 403
        self.requests.put = Mock(return_value=mock_response)

        actual_response = self.client._put(session, path, data_string)

        self.requests.put.assert_has_calls([call(url, **options), call(url, **options)])
        self.assertEqual(json_response, actual_response)
        session.invalidate.assert_called_once()

    def test_put_unknown(self):
        path = 'foo'
        url = 'https://api.jirafe.com/v1/id/foo'
        data_string = '{"bar":"baz"}'
        auth_header = "some header"
        session = Mock()
        session.site_id = 'id'
        session.get_header = Mock(return_value=auth_header)
        options = {
            "data": data_string,
            "headers": auth_header
        }
        json_response = {'success': False, 'error_type': 'unknown', 'raw': 'response text'}
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.text = 'response text'
        self.requests.put = Mock(return_value=mock_response)

        actual_response = self.client._put(session, path, data_string)

        self.requests.put.assert_called_once_with(url, **options)
        self.assertEqual(json_response, actual_response)
        session.invalidate.assert_called_once()
