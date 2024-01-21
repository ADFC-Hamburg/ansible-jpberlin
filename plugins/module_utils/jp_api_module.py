# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible.module_utils.basic import AnsibleModule
try:
    import requests
    import json
    import validators
except ImportError:
    pass


class JPAPIModule(AnsibleModule):
    def __init__(self, argument_spec):

        self.session = None
        super().__init__(argument_spec,
                         supports_check_mode=True)

    @staticmethod
    def get_login_argspec():
        login_argument_spec = dict(type="dict", required=True, options=dict(
            user=dict(type="str", required=True),
            password=dict(type="str", required=True, no_log=True),
            jrpc_url=dict(
                type="str", default="https://api.mx.heinlein-hosting.de/"),
        ))
        return login_argument_spec

    def json_rpc_call(self, method: str, params: dict):
        url = self.params['login']['jrpc_url']
        if not validators.url(url):
            self.fail_json(msg='longin.jrpc_url is not a valid url')

        headers = {
            'Content-Type': 'application/json'
        }
        if self.session is not None:
            headers['Hpls-Auth'] = self.session

        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 'adfc_ansible',
        }
        response = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
        err_out = {
            'payload': payload,
            'headers': headers,
            'response': response,
        }
        if 'error' in response.keys():
            self.fail_json(msg=response['error']['message'], **err_out)
        if 'result' not in response.keys():
            self.fail_json(msg='result not found in result', **err_out)
        if 'jsonrpc' not in response.keys():
            self.fail_json(msg='jsonrpc not found in result', **err_out)
        if response["jsonrpc"] != "2.0":
            self.fail_json(msg='Wrong jsonrpc version', **err_out)
        if response["id"] != payload['id']:
            self.fail_json(msg='Wrong response id', **err_out)
        return response["result"]

    def login_jpberlin(self):
        user = self.params['login']['user']
        password = self.params['login']['password']
        if password == '':
            self.fail_json(msg="login password must not be empty")
        login = self.json_rpc_call('auth', {'user': user, 'pass': password})
        self.session = login['session']

    def logout_jpberlin(self):
        return self.json_rpc_call('deauth', {})
