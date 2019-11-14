from json import dumps, loads
from cookielib import Cookie
from finalmark.academic_parser.ufcg import UfcgApi
from finalmark.work_distributer.ufcg import UfcgDistributer
from finalmark.cache import Cache
from prometheus_client import Counter

cache_counter = Counter('finalmark_cached_requests', 'Cached requests')
non_cache_counter = Counter('finalmark_non_cached_requests', 'Non cached requests')


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
            "cookie": dumps(extract_cookie(api.br.cookiejar))
        }
        user_info = {}
        distributer = UfcgDistributer(dist_data)
        distributer.distribute(user_info)

        return user_info
    return {"status": "login_error"}


def extract_cookie(cookiejar):

    for c in cookiejar:
        cookie = c

    extract = ['version', 'name', 'value',
               'port', 'port_specified',
               'domain', 'domain_specified', 'domain_initial_dot',
               'path', 'path_specified', 'secure', 'expires',
               'discard','comment', 'comment_url', 'rest', 'rfc2109']
    c = {}
    for attr in extract:
        if hasattr(cookie, attr):
            c[attr] = getattr(cookie, attr)

    return c


def get_auth(username, password, cookie=None, *args, **kwargs):
    api = UfcgApi(username, password)
    if cookie is not None:
        cookie = loads(cookie)
        cookie = Cookie(value=cookie.get('value'),
                        domain=cookie.get('domain'),
                        name=cookie.get('name'),
                        port_specified=cookie.get('port_specified'),
                        comment=cookie.get('comment'),
                        domain_initial_dot=cookie.get('domain_initial_dot'),
                        expires=cookie.get('expires'),
                        domain_specified=cookie.get('domain_specified'),
                        version=cookie.get('version'),
                        rfc2109=cookie.get('rfc2109'),
                        discard=cookie.get('discard'),
                        path_specified=cookie.get('path_specified'),
                        path=cookie.get('path'),
                        port=cookie.get('port'),
                        comment_url=cookie.get('comment_url'),
                        secure=cookie.get('secure'))
        api.br.cookiejar.set_cookie(cookie)
    else:
        api.authenticate()
    return api


def get_marks_from_subject(username, password, subject, cookie=None, *args, **kwargs):
    marks = cache.get("{}:{}:marks".format(username, subject.get('code')))
    if marks is None:
        non_cache_counter.inc()
        api = get_auth(username, password, cookie=cookie)
        marks = api.get_marks_from_subject(subject)
        cache.set("{}:{}:marks".format(username,
                                        subject.get('code')),
                                        marks)
    else:
        cache_counter.inc()
    return {"data": marks}


def get_absences_from_subject(username, password, subject, cookie=None, *args, **kwargs):
    absences = cache.get("{}:{}:absences".format(username, subject.get('code')))
    if absences is None:
        non_cache_counter.inc()
        api = get_auth(username, password, cookie=cookie)
        absences = api.get_absences_from_subject(subject)
        cache.set(u"{}:{}:absences".format(username,
                                          subject.get('code')),
                                          absences)
    else:
        cache_counter.inc()
    return {"data": absences }


def get_credits(username, password, subjects, cookie=None, *args, **kwargs):
    credits = cache.get("{}:credits".format(username))
    if credits is None:
        non_cache_counter.inc()
        api = get_auth(username, password, cookie=cookie)
        credits = api.get_credits(subjects)
        cache.set("{}:credits".format(username), credits)
    else:
        cache_counter.inc()
    return {"data": credits}


def get_user_info(username, password, cookie=None, *args, **kwargs):
    user_info = cache.get("{}:user_info".format(username))
    if user_info is None:
        non_cache_counter.inc()
        api = get_auth(username, password, cookie=cookie)
        user_info = api.get_user_info()
        cache.set("{}:user_info".format(username), user_info)
    else:
        cache_counter.inc()
    return {"data": user_info}



WORKER_ACTIONS = {
    "get_auth": get_auth,
    "get_marks_from_subject": get_marks_from_subject,
    "get_absences_from_subject": get_absences_from_subject,
    "get_credits": get_credits,
    "get_user_info": get_user_info
}

REFRESHER_ACTIONS = {
    "refresh_user": refresh_user
}
