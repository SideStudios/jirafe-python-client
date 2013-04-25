# Jirafe Python Client

# Install
```
pip install git+https://github.com/jirafe/jirafe-python-client#egg=jirafe-python-client
```

# Usage
```python
session = JirafeSession('username', 'password', 'site-id', 'https://accounts.jirafe.com/oauth2/access_token', 'client-id', 'client-secret')

client = JirafeClient('https://api.jirafe.com/')

client.product_change(session, product_dict)
```
