from json import dumps
from finalmark.academic_parser.ufcg import UfcgApi
from finalmark.work_distributer.ufcg import UfcgDistributer
from finalmark.cache import Cache

cache = Cache(caching_time=60)

def refresh_user(*args, **kwargs):
    data = kwargs
    username = data.get('username')
    password = data.get('password')
    api = UfcgApi(username, password)
    if api.authenticate():
        subjects = cache.get("{}:subjects".format(username))
        if subjects is None:
            subjects = api.get_subjects()
            cache.set("{}:subjects".format(username), subjects)

        dist_data = {
            "subjects": subjects,
            "username": username,
            "password": password,
            "cookies": dumps(extract_cookie(api.br.cookiejar))
        }
        user_info = {}
        distributer = UfcgDistributer(dist_data)
        distributer.distribute(user_info)

        return user_info
    return {"status": "login_error"}

def extract_cookie(cookiejar):

    for c in cookiejar:
        cookie = c

    extract = ['version', 'name', 'value', 'port', 'port_specified', 'domain',
               'domain_specified', 'domain_initial_dot',
               'path', 'path_specified', 'secure', 'expires',
               'discard', 'comment', 'comment_url', 'rfc2109']
    c = {}
    for attr in extract:
        c[attr] = getattr(cookie, attr)

    return c


POSSIBLE_ACTIONS = {
    "refresh_user": refresh_user
}
