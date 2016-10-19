#! python

HAS_CLICK = False
try:
    import click
    HAS_CLICK = True
except ImportError:
    raise SystemExit("Please install click library using 'pip install click'")

HAS_REQUESTS = False
try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    pass

try:
    import urllib3
    if callable(getattr(urllib3, 'disable_warnings')):
        urllib3.disable_warnings()
except ImportError:
    pass


@click.command()
@click.argument('endpoint', required=True)
@click.argument('username', required=True)
@click.argument('password', required=True)  # Wrap in single quotes to escape
@click.argument('eauth', default='pam')
@click.argument('ssh_user', default='deploy')
def saltstack(endpoint, username, password, eauth, ssh_user):
    if not HAS_REQUESTS:
        raise SystemExit(
            "Please install requests library using 'pip install requests'"
        )

    login_url = "{0}/login".format(endpoint)
    parameters = {"username": username, "password": password, "eauth": eauth}
    login_headers = {"Accept": "application/json"}
    response = requests.post(
        login_url,
        data=parameters,
        headers=login_headers,
        verify=True
    )
    if response.status_code == 200:
        data = response.json()
        minions_headers = {
            "Accept": "application/json",
            'X-Auth-Token': data['return'][0]['token']
        }
        vm_query_url = "{0}/minions/".format(endpoint)
        response = requests.get(
            vm_query_url,
            headers=minions_headers,
            verify=True
        )
        if response.status_code == 200:
            json = response.json()
            for data in json['return']:
                host = data.keys().pop()
                print("{0}:".format(host))
                print("  username: {0}".format(ssh_user))
                print("  description:")
                print("  tags: {0}".format(','.join(data[host]['roles'])))
                print("  osFamily: {0}".format(data[host]['os_family']))
                print("  osArch: {0}".format(data[host]['cpuarch']))
                print("  osName: {0}".format(data[host]['os']))
                print("  osVersion: {0}".format(data[host]['osrelease']))
                print("  cpus: {0}".format(data[host]['num_cpus']))
                print("  memory: {0}".format(data[host]['mem_total']))
                print("  salt: {0}".format(data[host]['saltversion']))
                print("  python: {0}".format(
                    '.'.join(str(x) for x in data[host]['pythonversion'][:3])
                ))
    else:
        raise SystemExit(
            "Invalid[{0}] endpoint: '{1}'".format(
                response.status_code,
                endpoint
            )
        )


if __name__ == '__main__':
    saltstack()
