# Jirafe Python Client

## Install
```
pip install git+ssh://git@github.com/jirafe/jirafe-python-client.git#egg=jirafe-python-client
```

## Usage
### Username Session
If you need to work with the Jirafe API from a secure non web based service, use the `UsernameSession`.
```python
session = UsernameSession('site_id', 'username', 'password', 'client_id', 'client_secret')

profile = session.get_profile()
```

### Oauth2 Session
After retrieving an authorization code from the redirected first step of the the Oauth2 process, you can pass it into the `Oauth2Session` to give it the ability to fetch access and refresh tokens
```python
# with a code
session = Oauth2Session('site_id', 'client_id', 'client_secret', code='5b94429c64c8f604cc2bd0422f4f5bc2b88d997d')

profile = session.get_profile()
```

If you have stored a refresh token, available at `session.get_refresh_token()`, you can pass it into a session to give it the ability to fetch new refresh and access tokens

```python
# with a refresh_token
session = Oauth2Session('site_id', 'client_id', 'client_secret', refresh_token='KsV1q3F2enN65vzxrg410Dj7d7jVoeth40ZM4TUT')

profile = session.get_profile()
```

If you have an access token, you can pass it to the session and use it until it expires. _Note: An access token alone cannot fetch a new refresh or access token_

```python
# with a refresh_token
session = Oauth2Session('site_id', 'client_id', 'client_secret', access_token='KsV1q3F2enN65vzxrg410Dj7d7jVoeth40ZM4TUT')

profile = session.get_profile()
```


### API Client
Once you have a session with a valid access token you can make calls to the Jirafe API
```python
client = JirafeClient()

response = client.product_change(session, product_dict)
```
