# Jirafe Python Client

# Install
```
pip install git+ssh://git@github.com:jirafe/jirafe-python-client.git#egg=jirafe-python-client
```

# Usage
```python
session = UsernameSession('site_id', 'username', 'password', 'client_id', 'client_secret')

profile = session.get_profile()

client = JirafeClient()

response = client.product_change(session, product_dict)
```
