import datetime
import requests

REPOS = ['solitude', 'marketplace', 'marketplace-api',
         'marketplace-webpay', 'amo-master', 'solitude']

def get_date(repo, build):
    url = ('https://ci-addons.allizom.org/job/{0}/{1}/api/json'
           .format(repo, build))
    res = requests.get(url, headers={'Accept': 'application/json'})
    return datetime.datetime.strptime(res.json()['id'], '%Y-%m-%d_%H-%M-%S')

allow = 10800

def get_jenkins(repos):
    reqs = []
    for key in repos:
        last_success = get_date(key, 'lastStableBuild')
        diff = datetime.datetime.now() - last_success
        if diff.total_seconds() > allow:
            reqs.append('{0} unstable for {1} days, {2} hours'.
                        format(key, diff.days, diff.seconds / 3600))

    return reqs


if __name__ == '__main__':
    print get_jenkins(REPOS)
