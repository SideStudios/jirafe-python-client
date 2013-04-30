from mock import Mock
import requests
import unittest
from jirafe import JirafeSession, UsernameSession, Oauth2Session

class TestJirafeSession(unittest.TestCase):
    def setUp(self):
        self.site_id = 'id'
        self.mock_requests = Mock()
        self.session = JirafeSession(self.site_id, requests=self.mock_requests)

    def test_constructor_defaults(self):
        session = JirafeSession(self.site_id)
        self.assertEqual(self.site_id, self.session.site_id)
        self.assertEqual('https://accounts.jirafe.com/oauth2/authorize', session.auth_url)
        self.assertEqual('https://accounts.jirafe.com/oauth2/access_token', session.token_url)
        self.assertEqual('https://accounts.jirafe.com/accounts/profile', session.profile_url)
        self.assertIsNone(self.session.access_token)
        self.assertEqual(requests, session.requests)

    def test_constructor_change(self):
        kwargs = {
            'auth_url': 'a',
            'token_url': 't',
            'profile_url': 'p',
            'requests': Mock()
        }
        session = JirafeSession(self.site_id, **kwargs)
        self.assertEqual('a', session.auth_url)
        self.assertEqual('t', session.token_url)
        self.assertEqual('p', session.profile_url)
        self.assertEqual(kwargs['requests'], session.requests)

    def test_get_header(self):
        self.session.access_token = 'some_token'
        expected = {
            'Authorization': 'Bearer some_token'
        }
        self.assertEqual(expected, self.session.get_header())

    def test_update_token(self):
        self.session._get_token = Mock(return_value='token')
        self.assertEqual('token', self.session.update_token())
        self.assertEqual('token', self.session.update_token())
        self.session._get_token.assert_called_once()

    def test_invalidate(self):
        self.session.access_token = 'some_token'
        self.assertEqual('some_token', self.session.access_token)
        self.session.invalidate()
        self.assertIsNone(self.session.access_token)

    def test_get_profile(self):
        json_response = {'a': 'profile'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value=json_response)
        self.mock_requests.get = Mock(return_value=mock_response)
        self.session.get_header = Mock(return_value={'mock': 'header'})

        profile = self.session.get_profile()

        self.assertEqual(json_response, profile)
        mock_response.json.assert_called_once()
        self.mock_requests.get.assert_called_once_with('https://accounts.jirafe.com/accounts/profile', headers={'mock': 'header'})

    def test_get_profile_fail(self):
        mock_response = Mock()
        mock_response.status_code = 403
        self.mock_requests.get = Mock(return_value=mock_response)
        self.session.get_header = Mock()
        self.session.invalidate = Mock()

        self.assertIsNone(self.session.get_profile())
        self.session.invalidate.assert_called_once()

    def test_get_site(self):
        profile = {'sites': [{'id': 'id'}]}
        self.session.get_profile = Mock(return_value=profile)

        self.assertEqual({'id': 'id'}, self.session.get_site())

    def test_get_site_empty(self):
        profile = {'sites': []}
        self.session.get_profile = Mock(return_value=profile)

        self.assertIsNone(self.session.get_site())

    def test_get_site_missing(self):
        profile = {'a': 'profile'}
        self.session.get_profile = Mock(return_value=profile)

        self.assertIsNone(self.session.get_site())

    def test__get_token(self):
        self.assertRaises(NotImplementedError, self.session._get_token)

class TestUsernameSession(unittest.TestCase):
    def setUp(self):
        self.site_id = 'id'
        self.mock_requests = Mock()
        self.username = 'username'
        self.password = 'password'
        self.client_id = 'client_id'
        self.client_secret = 'client_secret'
        self.session = UsernameSession(self.site_id,
                                       self.username,
                                       self.password,
                                       self.client_id,
                                       self.client_secret,
                                       requests=self.mock_requests)

    def test_constructor_defaults(self):
        session = UsernameSession(self.site_id,
                               self.username,
                               self.password,
                               self.client_id,
                               self.client_secret)
        self.assertEqual(self.site_id, session.site_id)
        self.assertEqual(self.username, session.username)
        self.assertEqual(self.password, session.password)
        self.assertEqual(self.client_id, session.client_id)
        self.assertEqual(self.client_secret, session.client_secret)
        self.assertEqual('https://accounts.jirafe.com/oauth2/authorize', session.auth_url)
        self.assertEqual('https://accounts.jirafe.com/oauth2/access_token', session.token_url)
        self.assertEqual('https://accounts.jirafe.com/accounts/profile', session.profile_url)
        self.assertIsNone(session.access_token)
        self.assertEqual(requests, session.requests)

    def test__get_token_happy(self):
        data = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={'access_token': 'teh_token'})
        self.mock_requests.post = Mock(return_value=mock_response)

        self.assertEqual('teh_token', self.session._get_token())
        self.mock_requests.post.assert_called_once_with(self.session.token_url, data=data)

    def test__get_token_sad(self):
        data = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        mock_response = Mock()
        mock_response.status_code = 403
        self.mock_requests.post = Mock(return_value=mock_response)

        self.assertIsNone(self.session._get_token())
        self.mock_requests.post.assert_called_once_with(self.session.token_url, data=data)

class TestOauth2Session(unittest.TestCase):
    def setUp(self):
        self.site_id = 'id'
        self.mock_requests = Mock()
        self.client_id = 'client_id'
        self.client_secret = 'client_secret'
        self.code = 'code'
        self.refresh_token = 'refresh_token'
        self.access_token = 'access_token'

    def test_constructor_defaults(self):
        session = Oauth2Session(self.site_id,
                                self.client_id,
                                self.client_secret)
        self.assertEqual(self.site_id, session.site_id)
        self.assertEqual(self.client_id, session.client_id)
        self.assertEqual(self.client_secret, session.client_secret)
        self.assertIsNone(session.code)
        self.assertIsNone(session.access_token)
        self.assertIsNone(session.refresh_token)
        self.assertEqual('https://accounts.jirafe.com/oauth2/authorize', session.auth_url)
        self.assertEqual('https://accounts.jirafe.com/oauth2/access_token', session.token_url)
        self.assertEqual('https://accounts.jirafe.com/accounts/profile', session.profile_url)
        self.assertEqual(requests, session.requests)

    def test_constructor_change(self):
        session = Oauth2Session(self.site_id,
                                self.client_id,
                                self.client_secret,
                                self.code,
                                self.refresh_token,
                                self.access_token,
                                requests=self.mock_requests)
        self.assertEqual(self.code, session.code)
        self.assertEqual(self.access_token, session.access_token)
        self.assertEqual(self.refresh_token, session.refresh_token)
        self.assertEqual(self.mock_requests, session.requests)

    def test__do_post(self):
        session = Oauth2Session(self.site_id,
                                self.client_id,
                                self.client_secret,
                                code='some_code',
                                requests=self.mock_requests)
        data = {'some': 'data'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={'access_token': 'teh_token', 'refresh_token': 'ref_token'})
        self.mock_requests.post = Mock(return_value=mock_response)

        self.assertEqual('teh_token', session._do_post(data))
        self.assertEqual('ref_token', session.refresh_token)
        self.assertIsNone(session.code)
        self.mock_requests.post.assert_called_once_with(session.token_url, data=data)

    def test__get_token_with_access_token(self):
        session = Oauth2Session(self.site_id,
                                self.client_id,
                                self.client_secret,
                                access_token='some_token',
                                requests=self.mock_requests)
        session._do_post = Mock()

        self.assertEqual('some_token', session._get_token())
        self.assertFalse(session._do_post.called)

    def test__get_token_with_refresh_token(self):
        session = Oauth2Session(self.site_id,
                                self.client_id,
                                self.client_secret,
                                refresh_token='some_token',
                                requests=self.mock_requests)
        session._do_post = Mock(return_value='access_token')
        expected_data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': 'some_token',
        }

        self.assertEqual('access_token', session._get_token())
        session._do_post.assert_called_once_with(expected_data)

    def test__get_token_with_code(self):
        session = Oauth2Session(self.site_id,
                                self.client_id,
                                self.client_secret,
                                code='some_code',
                                requests=self.mock_requests)
        session._do_post = Mock(return_value='access_token')
        expected_data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': 'some_code',
        }

        self.assertEqual('access_token', session._get_token())
        session._do_post.assert_called_once_with(expected_data)
