import re

import requests


class GitHubError(Exception):
    pass


PULLS = {
    #'apk-signer': {},
    #'fxpay': {},
    #'solitude': {},
    #'webpay': {},
    #'zippy': {},
    #'spartacus': {},
    'zamboni': {},
    #'fireplace': {},
    #'commonplace': {}
}


def _jugs():
    return {
        '1': {'name': 'foo', 'people': ['jared', 'kumar']},
        '2': {'name': 'bar', 'people': ['cvan', 'kumar']}
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
            'name': entry['name'],
            'people': entry.get('team_developers', [])
        }
    return found


def blocks(bug):
    res = requests.get('https://api-dev.bugzilla.mozilla.org/latest/bug/%s'
                       % bug, headers={'Accept': 'application/json'})
    return res.json().get('blocks', [])


def _blockers(bug):
    if bug == '3':
        return ['1', '2']
    if bug == '5':
        return ['1']
    return []


def blockers(bug):
    bugs = set(blocks(bug))
    for bug in frozenset(bugs):
        bugs.update(set(blockers(bug)))

    return list(bugs)


def get(path):
    res = requests.get('https://api.github.com{0}'.format(path))
    if res.status_code == 200:
        return res.json()
    raise GitHubError(res.status_code)

def _pulls(repo, **kwargs):
    return [{
        'login': 'andy',
        'number': '3',
        'url': 'http://foo/bar/3+',
    }, {
        'login': 'andy-a',
        'number': '4',
        'url': 'http://foo/bar/4***',
    }, {
        'login': 'andy-b',
        'number': '5',
        'url': 'http://foo/bar/5~~~',
    }, {
        'login': 'andy-b',
        'number': 'none',
        'url': 'http://foo/bar/8-',
    }]

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


def process(config, project=None, person=None):
    projects = jugs()
    pull_requests = []
    found = {'none': []}

    for repo, values in config.items():
        pull_requests.extend(pulls(repo, **values))

    for pull in pull_requests:
        # Convert the pull request number into a tracker.
        # There could be more than one tracker.
        # The tracker could not exist in jugband, in which case it ends up
        # as none.
        num = pull.get('number', 'none')
        if num != 'none':
            num = blockers(num) or 'none'
        if not isinstance(num, list):
            num = [num]
        for k, v in enumerate(num):
            if v not in projects:
                num[k] = 'none'
        for n in num:
            found.setdefault(n, [])
            found[n].append(pull)

    if project:
        return projects, {project: found.get(project, [])}

    if person:
        data = {}
        for project, values in found.items():
            if person not in projects.get(project, {}).get('people', []):
                continue
            data.setdefault(project, [])
            data[project].extend(values)

        return projects, data

    return projects, found


def get_pulls(config, project=None, person=None):
    projects, data = process(config, project=project, person=person)
    out = []
    for k, v in data.items():
        if not v:
            continue
        if k in projects:
            out.append('pull requests for tracker {0}: {1}'.format(
                       k, projects[k]['name']))
        else:
            out.append('pull requests with no tracker')
        for bug in v:
            out.append('  r? {url} from {login}'.format(**bug))
    if not out:
        out.append('pull requests there are not')
    return out


if __name__ == '__main__':
    for x in get_pulls(PULLS):
        print x
