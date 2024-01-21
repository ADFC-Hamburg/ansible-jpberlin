#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
from ansible_collections.hamburg_adfc.jpberlin.plugins.module_utils.jp_api_module import JPAPIModule
import validators
__metaclass__ = type


DOCUMENTATION = r'''
author:
- Sven Anders (@tabacha)
description: Get Mail Accounts of an domain
extends_documentation_fragment:
- hamburg_adfc.jpberlin.login
module: idoit_cat_application_info
options:
  domain:
    description: E-Mail domain
    type: str
    required: true
short_description: Get Mail Accounts of an domain
'''

EXAMPLES = r'''
name: Create an account
hamburg_adfc.jpberlin.email_accounts_info:
  login:
    username: info@example.com
    password: info_secret
  domain: example.com
'''

RETURN = r'''
changed:
  description: Are there changes?
  returned: always
  type: bool
mail_accounts:
  description: Mail accounts
  returned: always
  type: list
  elements: dict
  options:
    email:
      description: Mail Address
      type: str
    type:
      description: Type of Mail-Address, forward or inbox
      type: choices
      choices:
        - forward
        - inbox
        - inboxforward
'''


def run_module():
    module_args = dict(
        login=JPAPIModule.get_login_argspec(),
        domain=dict(type='str', required=False)
    )

    result = dict(
        changed=False,
        mail_accounts=[],
    )

    module = JPAPIModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    if not validators.domain(module.params['domain']):
        module.exit_json(msg="Domain syntax invalid")
    module.login_jpberlin()
    res = module.json_rpc_call('q.domain.mail.list', {
                               'domain': module.params['domain']})
    module.logout_jpberlin()
    for entry in res:
        result['mail_accounts'].append(
            {'email': entry['mail'], 'type': entry['type']})

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
