from server.auth.base_authenticator import BaseAuthenticator


class DummyAuthenticator(BaseAuthenticator):
    passwords = {'a': 'a',
                 'b' : 'b',
                 'c': 'c',
                 'sebastian.seitner': '1234'}

    def authenticate(self, username=None, password=None):
        if self.passwords.get(username) == password:
            if username =='a':
                return {'username': username,
                        'name': 'foo',
                        'surname': 'bar',
                        'email': 'foo@bar.com',
                        'groups': ['djamei']}
            elif username =='b':
                return {'username': username,
                        'name': 'SyT',
                        'surname': 'TyS',
                        'email': 'syt@bar.com',
                        'groups': ['djamei']}
            elif username == 'sebastian.seitner':
                return {'username': username,
                        'name': 'Sebastian',
                        'surname': 'Seitner',
                        'email': 'sebastian_seitner@gmi.oeaw.ac.at',
                        'groups': ['djamei']}
            if username == 'c':
                return {'username': 'angelika.czedik',
                        'name': 'Angelika',
                        'surname': 'Czedik-Eysenberg',
                        'email': 'angelika.czedik@gmi.oeaw.ac.at',
                        'groups': ['djamei']}
        return None
