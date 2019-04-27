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


def get_auth(username, password, cookie=None, *args, **kwargs):
    api = UfcgApi(username, password)
    if cookie is not None:
        cookie = loads(cookie)
        cookie = Cookie(**cookie)
        api.br.cookiejar.set_cookie(cookie)
    else:
        api.authenticate()
    return api


def get_marks_from_subject(username, password, subject, cookie=None, *args, **kwargs):
    marks = cache.get("{}:{}:marks".format(username, subject.get('name')))
    if marks is None:
        api = get_auth(username, password, cookie=cookie)
        marks = api.get_marks_from_subject(subject)
        cache.set("{}:{}:marks".format(username,
                                       subject.get('name')),
                                       marks)

    return {"data": marks}


def get_absences_from_subject(username, password, subject, cookie=None, *args, **kwargs):
    absences = cache.get("{}:{}:absences".format(username, subject.get('name')))
    if absences is None:
        api = get_auth(username, password, cookie=cookie)
        absences = api.get_absences_from_subject(subject)
        cache.set("{}:{}:absences".format(username,
                                          subject.get('name')),
                                          absences)

    return {"data": absences }


def get_credits(username, password, subjects, cookie=None, *args, **kwargs):
    credits = cache.get("{}:credits".format(username))
    if credits is None:
        api = get_auth(username, password, cookie=cookie)
        credits = api.get_credits(subjects)
        cache.set("{}:credits".format(username), credits)

    return {"data": credits}


def get_user_info(username, password, cookie=None, *args, **kwargs):
    user_info = cache.get("{}:user_info".format(username))
    if user_info is None:
        api = get_auth(username, password, cookie=cookie)
        user_info = api.get_user_info()
        cache.set("{}:user_info".format(username), user_info)
    return {"data": user_info}



WORKER_ACTIONS = {
    "get_auth": get_auth,
    "get_marks_from_subject": get_marks_from_subject,
    "get_absences_from_subject": get_absences_from_subject,
    "get_credits": get_credits,
    "get_user_info": get_user_info
}

REFRESH_ACTIONS = {
    "refresh_user": refresh_user
}
