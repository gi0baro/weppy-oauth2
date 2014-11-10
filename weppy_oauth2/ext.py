import time
import cgi
import urllib2
import json
from urllib import urlencode

from weppy import session, request, redirect
from weppy.extensions import Extension
from weppy.tools.auth import Auth, AuthLoginHandler


class Oauth2(Extension):
    config_default = dict(
        get_user=lambda u: None
    )
    config_mandatory = ['client_id', 'client_secret', 'auth_url', 'token_url']

    def _config_check(self):
        for key in self.config_mandatory:
            if self.config.get(key) is None:
                raise RuntimeError("Configuration missing for: %s" % key)

    def _config_load_wdef(self):
        for key in self.config_default.keys():
            self.config[key] = self.config.get(key, self.config_default[key])

    def load(self, auth):
        if not isinstance(auth, Auth):
            raise RuntimeError("Oauth needs an Auth instance to work properly")
        self.auth = auth
        self._config_check()
        self._config_load_wdef()
        self._add_action()

    def _add_action(self):
        self.auth.register_action('oauth', self.oauth)

    def oauth(self, *args):
        return self.auth._login_with_handler(LoginHandler, self.config)


class LoginHandler(AuthLoginHandler):
    socket_timeout = 60

    def __redirect_uri(self):
        """
        Build the uri used by the authenticating server to redirect
        the client back to the page originating the auth request.
        Appends the _next action to the generated url so the flows continues.
        """
        uri = '%s://%s%s' % (request.scheme, request.hostname,
                             request.path_info)
        if request.get_vars:
            uri += '?' + urlencode(request.get_vars)
        return uri

    def __build_url_opener(self, uri):
        """
        Build the url opener for managing HTTP Basic Athentication
        """
        # Create an OpenerDirector with support
        # for Basic HTTP Authentication...
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(realm=None,
                                  uri=uri,
                                  user=self.env.client_id,
                                  passwd=self.env.client_secret)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        return opener

    def accessToken(self):
        """
        Return the access token generated by the authenticating server.

        If token is already in the session that one will be used.
        Otherwise the token is fetched from the auth server.

        """
        if session.token and 'expires' in session.token:
            expires = session.token['expires']
            # reuse token until expiration
            if expires == 0 or expires > time.time():
                        return session.token['access_token']

        code = request.vars.code

        if code:
            data = dict(client_id=self.env.client_id,
                        client_secret=self.env.client_secret,
                        redirect_uri=session.redirect_uri,
                        code=code,
                        grant_type='authorization_code'
                        )

            open_url = None
            opener = self.__build_url_opener(self.env.token_url)
            try:
                open_url = opener.open(self.env.token_url, urlencode(data),
                                       self.socket_timeout)
            except urllib2.HTTPError, e:
                tmp = e.read()
                raise Exception(tmp)
            finally:
                if session.code:
                    del session.code
                if session.redirect_uri:
                    del session.redirect_uri

            if open_url:
                try:
                    data = open_url.read()
                    resp_type = open_url.info().gettype()
                    #: try json style first
                    if not resp_type or resp_type[:16] == 'application/json':
                        try:
                            tokendata = json.loads(data)
                            session.token = tokendata
                        except Exception, e:
                            raise Exception("Cannot parse oauth server response %s %s" % (data, e))
                    #: try with x-www-form-encoded
                    else:
                        tokendata = cgi.parse_qs(data)
                        session.token = \
                            dict([(k, v[-1]) for k, v in tokendata.items()])
                    #: we failed parsing
                    if not tokendata:
                        raise Exception("Cannot parse oauth server response %s" % data)
                    #: set expiration
                    if 'expires_in' in session.token:
                        exps = 'expires_in'
                    elif 'expires' in session.token:
                        exps = 'expires'
                    else:
                        exps = None
                    session.token['expires'] = exps and \
                        int(session.token[exps]) + \
                        time.time()
                finally:
                    opener.close()
                return session.token['access_token']

        session.token = None
        return None

    def __oauth_login(self):
        """
        This method redirects the user to the authenticating form
        on authentication server if the authentication code
        and the authentication token are not available to the
        application yet.

        Once the authentication code has been received this method is
        called to set the access token into the session by calling
        accessToken()
        """

        token = self.accessToken()
        if not token:
            session.redirect_uri = self.__redirect_uri()
            data = dict(redirect_uri=session.redirect_uri,
                        response_type='code',
                        client_id=self.env.client_id)
            auth_request_url = self.env.auth_url + "?" + urlencode(data)
            redirect(auth_request_url)
        return

    def login_url(self, _next="/"):
        self.__oauth_login()
        return _next

    def logout_url(self, _next="/"):
        del session.token
        return _next

    def get_user(self):
        if not self.accessToken():
            return None
        return self.env.get_user(dict())
