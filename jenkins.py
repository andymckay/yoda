import datetime
import requests

REPOS = ['solitude', 'marketplace', 'marketplace-api', 'marketplace-assets',
         'amo-assets', 'olympia', 'marketplace-webpay', 'amo-master',
         'solitude']

def get_data(repo, build):
    url = ('https://ci-addons.allizom.org/job/{0}/{1}/api/json'
           .format(repo, build))
    res = requests.get(url, headers={'Accept': 'application/json'})
    return res.json()

allow = 10800

def get_jenkins(repos):
    reqs = []
    for key in repos:
        if get_data(key, 'lastSuccessfulBuild')['result'] == 'SUCCESS':
            continue

        last_failure = datetime.datetime.strptime(
            get_data(key, 'lastStableBuild')['id'],
            '%Y-%m-%d_%H-%M-%S')

        diff = datetime.datetime.now() - last_failure
        if diff.total_seconds() > allow:
            reqs.append('{0} unstable for {1} days, {2} hours'.
                        format(key, diff.days, diff.seconds / 3600))

    return reqs


if __name__ == '__main__':
    print get_jenkins(REPOS)
