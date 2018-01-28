import ldap
import logging

from server.auth.base_authenticator import BaseAuthenticator


class LDAPAuthenticator(BaseAuthenticator):
    # TODO: secure connection

    def __init__(self, server, bind_dn, bind_pass, base_dn, filter):
        self.server = server
        self.bind_dn = bind_dn
        self.bind_pass = bind_pass
        self.base_dn = base_dn
        self.filter = filter
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

    def _find_user_info(self, ldap_conn, username):
        result = ldap_conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, self.filter.format(username))
        if not result:
            return (None, None)
        return result[0]

    def _extract_group_name(self, group_dn):
        return group_dn

    def _get_user_groups(self, user_tree):
        return filter(None, [self._extract_group_name(group_dn) for group_dn in user_tree['memberOf']])

    def _authorize_user(self, user_info):
        return True

    def _get_user_info(self, user_tree):
        return user_tree

    def authenticate(self, username=None, password=None):
        if username is not None and password is not None:
            ldap_conn = None
            try:
                # ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
                ldap_conn = ldap.initialize(self.server)
                ldap_conn.bind_s(self.bind_dn, self.bind_pass)
                user_dn, user_tree = self._find_user_info(ldap_conn, username)

                if user_dn is not None:
                    ldap_conn.bind_s(user_dn, password)
                    ldap_conn.unbind_s()

                    user_info = self._get_user_info(user_tree)
                    if self._authorize_user(user_info):
                        self._logger.info('User {} successfully authenticated'.format(username))
                        return user_info
                    else:
                        self._logger.info('User {} is not allowed to access the application'.format(username))

            except ldap.LDAPError as err:
                self._logger.warning(
                    'Couldn\'t authenticate with LDAP server: {}@{} ({}) - Details: {}'.format(username, self.server,
                                                                                               err.message.get('desc'),
                                                                                               err.message.get('info')))
                if ldap_conn is not None:
                    ldap_conn.unbind_s()
                return None
        self._logger.info('User {} could not be found on server {}'.format(username, self.server))
        return None


