# weppy-Oauth2

weppy-Oauth2 is an extension for [weppy framework](http://weppy.org) providing a simple interface to manage logins with OAuth2 standard.

## Installation

You can install weppy-Oauth2 using pip:

    pip install weppy-Oauth2

And add it to your weppy application:

```python
def get_oauth_user(user):
    # code to process the user from oauth service

from weppy_oauth2 import Oauth2

app.config.Oauth2.auth_url = "<url for auth>"
app.config.Oauth2.token_url = "<token url>"
app.config.Oauth2.client_id = "<your app id>"
app.config.Oauth2.client_secret = "<your app secret>"
app.config.Oauth2.get_user = get_oauth_user

app.use_extension(Oauth2)
```

## Documentation

The documentation will be soon available.
