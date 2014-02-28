import requests

class GitHubError(Exception):
    pass


PULLS = {
    'solitude': {},
    'webpay': {},
    'zippy': {},
    'spartacus': {},
    'zamboni': {
        'users': ['kumar303', 'jkerim', 'muffinresearch', 'andymckay']
    }
}



def get(path):
    res = requests.get('https://api.github.com{0}'.format(path))
    if res.status_code == 200:
        return res.json()
    raise GitHubError(res.status_code)


def pulls(repo, **kwargs):
    found = []
    users = kwargs.get('users', [])
    res = get('/repos/mozilla/{0}/pulls'.format(repo))
    for pull in res:
        if pull['state'] != 'open':
            continue
        if users and pull['user']['login'] not in users:
            continue
        found.append([pull['html_url'] + '/files/', pull['user']['login']])
    return found


def get_pulls(config):
    found = []
    out = []
    for repo, values in config.items():
        found.extend(pulls(repo, **values))
    for item in found:
        out.append('r? {0} from {1}'.format(*item))
    return out


if __name__ == '__main__':
    get_pulls(PULLS)
