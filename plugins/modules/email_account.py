#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


DOCUMENTATION = r'''
author:
- Sven Anders (@tabacha)
description: Creates or ensusres than an E-mail account is there
extends_documentation_fragment:
- hamburg_adfc.jpberlin.login
module: email_account
options:
  email:
    description: Mail Address
    type: str
    required: true
  password:
    description: Password
    type: str
  force_password_set:
    description: Force password set if account exists
    type: bool
    default: false
  memo:
    description: Name or something you want to specify, if not specified it will be the old value
    type: str
  forwards:
    description: Mail to forward the email to
    type: list
    elements: str
    default: []
  mail_type:
    description: forwards or also save mail in mailbox
    type: str
    default: inbox
    choices:
        - inbox
        - forward
        - inboxforward
  state:
    description: Create = present or Delete = absent value
    type: str
    choices:
        - present
        - absent
    default: present
short_description: Create mailaccount

'''

EXAMPLES = r'''
name: Create an account
hamburg_adfc.jpberlin.email_account:
  login:
    username: info@example.com
    password: info_secret
  email: hans.muster@example.com
  password: hans_secret
  force_password_set: true
  forwards:
    - hans2nd@sub.example.com
    - hans3nd@sub.example.com
  mail_type: inboxforward
  memo: Hans Muster
'''

RETURN = r'''
changed:
  description: Are there changes?
  returned: always
  type: bool
'''

from ansible_collections.hamburg_adfc.jpberlin.plugins.module_utils.jp_api_module import JPAPIModule

try:
    import validators
    import yaml
except ImportError:
    pass


def run_module():
    module_args = dict(
        login=JPAPIModule.get_login_argspec(),
        email=dict(type='str', required=True),
        password=dict(type='str', required=False, no_log=True),
        memo=dict(type='str', required=False),
        force_password_set=dict(type='bool', default=False),
        forwards=dict(type='list', elements="str", default=[]),
        mail_type=dict(type='str', default='inbox', choices=[
                       'inbox', 'forward', 'inboxforward']),
        state=dict(type='str', default='present', choices=[
            'present', 'absent'])
    )

    result = dict(
        changed=False,
    )

    module = JPAPIModule(argument_spec=module_args)

    if not validators.email(module.params['email']):
        module.fail_json(msg="email syntax invalid")

    for forward in module.params['forwards']:
        if not validators.email(forward):
            module.fail_json(msg="forward syntax invalid (%s)" % forward)
    domain = module.params['email'].split('@')[1]
    module.login_jpberlin()
    res = module.json_rpc_call('q.domain.mail.list', {'domain': domain})
    found = False
    for entry in res:
        if entry['mail'] == module.params['email']:
            found = True
    if module.params['state'] == 'absent' and found is False:
        result['msg'] = 'Nothing to do, entry does not exists.'
        module.exit_json(**result)
    if module.params['state'] == 'absent':
        if not module.check_mode:
            res = module.json_rpc_call('q.domain.mail.del', {
                'domain': domain, 'mail': module.params['email']})
        result['changed'] = True
        result['msg'] = 'Entry deleted.'
        module.logout_jpberlin()
        module.exit_json(**result)

    if module.params['state'] != 'present':
        module.fail_json(msg='State not defined, must be present or absent.')

    if (module.params['mail_type'] in ['forward', 'inboxforward']) and len(module.params['forwards']) == 0:
        module.fail_json(
            msg='forwards must contain one or more e-mail addresses on mail_type: %s' % module.params['mail_type'])
    if (module.params['mail_type'] == 'inbox') and len(module.params['forwards']) > 0:
        module.fail_json(msg='forwards must be empty on mail_type: inbox')

    if found:
        res_mail_get = module.json_rpc_call(
            'q.mail.get', {'mail': module.params['email']})
        call_inboxsave = False
        new = {
            'email': module.params['email'],
            'forwards': sorted(module.params['forwards']),
            'mail_type': module.params['mail_type'],
        }
        old = {
            'email': res_mail_get['mail'],
            'memo': res_mail_get['memo'],
            'forwards': sorted(res_mail_get['forwards']),
            'mail_type': res_mail_get['type'],
        }
        if 'memo' in module.params.keys() or module.params['memo'] is None:
            new['memo'] = module.params['memo']
        else:
            new['memo'] = res_mail_get['memo']

        if res_mail_get['type'] != module.params['mail_type']:
            call_inboxsave = True
            if module.params['mail_type'] == 'forward':
                result['changed'] = True
                inboxsave = False
            else:
                result['changed'] = True
                inboxsave = True
        if 'memo' in module.params.keys() and module.params['memo'] is not None and res_mail_get['memo'] != module.params['memo']:
            result['changed'] = True
            if not module.check_mode:
                res = module.json_rpc_call('q.mail.memo.set', {
                    'mail': module.params['email'], 'memo': module.params['memo']})
        if call_inboxsave and inboxsave:
            if not module.check_mode:
                res = module.json_rpc_call('q.mail.inboxsave.set', {
                    'mail': module.params['email'], 'inboxsave': inboxsave})

        if sorted(res_mail_get['forwards']) != sorted(module.params['forwards']):
            result['changed'] = True
            if not module.check_mode:
                res = module.json_rpc_call('q.mail.forward.set', {
                    'mail': module.params['email'], 'forwards': module.params['forwards']})
        if call_inboxsave and not inboxsave:
            if not module.check_mode:
                res = module.json_rpc_call('q.mail.inboxsave.set', {
                                           'mail': module.params['email'], 'inboxsave': inboxsave})
        if module.params['force_password_set']:
            result['changed'] = True
            old['password'] = 'unknown'
            new['password'] = 'cenored'
            if not module.check_mode:
                res = module.json_rpc_call('q.mail.password.set', {
                    'mail': module.params['email'], 'password': module.params['password']})

    else:
        if 'password' not in module.params.keys() or module.params['password'] is None:
            module.fail_json(
                msg='Password must be specified as email does not exists')

        if 'memo' not in module.params.keys() or module.params['memo'] is None:
            module.params['memo'] = ''
        params = {
            "domain": domain,
            "mail": module.params['email'],
            "pass": module.params['password'],
            "memo": module.params['memo'],
            "catchall": False,
            "inboxsave": (module.params['mail_type'] in ['inbox', 'inboxforward'])
        }
        old = {}
        new = {
            'email': module.params['email'],
            'password': 'ceonsored',
            'memo': module.params['memo'],
            'mail_type': module.params['mail_type'],
        }
        if (module.params['mail_type'] in ['forward', 'inboxforward']):
            params['forwards'] = sorted(module.params['forwards'])
            new['forwards'] = sorted(module.params['forwards'])
        else:
            params['forwards'] = []
            new['forwards'] = []

        result['changed'] = True
        if not module.check_mode:
            res = module.json_rpc_call('q.domain.mail.add', params)

    if module._diff:
        result['diff'] = dict(
            before=yaml.safe_dump(old),
            after=yaml.safe_dump(new),
        )
    module.logout_jpberlin()
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
