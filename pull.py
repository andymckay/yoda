import re

import requests


class GitHubError(Exception):
    pass


PULLS = {
    'apk-signer': {},
    'fxpay': {},
    'solitude': {},
    'webpay': {},
    'zippy': {},
    'spartacus': {},
    'zamboni': {},
    'fireplace': {},
    'commonplace': {}
}


def jugs():
    found = {}
    res = requests.get('https://jugband.paas.allizom.org',
                       headers={'Accept': 'application/json'})
    for entry in res.json()['podio']:
        if 'Build Bugs' not in entry:
            continue
        bug = entry['Build Bugs']
        found[re.search(r'\d+', bug).group()] = {
            'name': entry['name'], 'bugs': []
        }
    return found


def _deps(bug):
    res = requests.get('https://api-dev.bugzilla.mozilla.org/latest/bug/%s'
                       % bug, headers={'Accept': 'application/json'})
    return res.json().get('depends_on', [])


def deps(bugs):
    for k, v in bugs.items():
        v['bugs'] = _deps(k)
        # only one layer of recursion.
        #for b in v['bugs']:
        #    v['bugs'].extend(_deps(b))
    return bugs


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
        url = pull['html_url'] + '/files/'
        try:
            number = re.search('bug (\d+)', pull['title']).group(1)
        except AttributeError:
            number = 'none'
        found.append({
            'login': pull['user']['login'],
            'number': number,
            'url': url
        })
    return found


def invert(vals):
    res = {}
    for k, v in vals.items():
        for b in v['bugs']:
            res[str(b)] = str(k)
    return res


def get_pulls(config):
    trackers = deps(jugs())
    lookup = invert(trackers)

    found = {'none': []}
    for repo, values in config.items():
        for pull in pulls(repo, **values):
            k = lookup.get(pull['number'], 'none')
            found.setdefault(k, [])
            found[k].append(pull)

    out = []
    for tracker, values in found.items():
        if tracker in trackers:
            out.append('bugs for tracker {0}: {1}'.format(
                tracker, trackers[tracker]['name']))
        else:
            continue
            # Ignoring bugs without a tracker.
            #out.append('bugs without a tracker')
        for bug in values:
            out.append('  r? {url} from {login}'.format(**bug))
    return out


if __name__ == '__main__':
    for x in get_pulls(PULLS):
        print x
