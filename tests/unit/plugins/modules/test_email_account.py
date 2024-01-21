# -*- coding: utf-8 -*-
# (c) 2021 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    BaseTestModule,
    FetchUrlCall,
)

from ansible_collections.hamburg_adfc.jpberlin.plugins.modules import email_account

# These imports are needed so patching below works
import ansible_collections.hamburg_adfc.jpberlin.plugins.module_utils.jp_api_module  # noqa


class TestEmailAccounts(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.hamburg_adfc.jpberlin.plugins.modules.email_accounts_info.JPAPIModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.hamburg_adfc.jpberlin.plugins.module_utils.jp_api_module.fetch_url'

    def test_successfull_add_run(self, mocker):
        result = self.run_module_success(mocker, email_account, {
            'login': {
                'user': 'my-user',
                'password': 'my-pass'
            },
            'email': 'ansible-test@example.com',
            'password': 'secret',
            'memo': 'Ansible-Test',
            '_ansible_remote_tmp': '/tmp/tmp',
            '_ansible_keep_remote_files': True,
        }, [
            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'auth')
            .expect_json_value(['params'], {'pass': 'my-pass', 'user': 'my-user'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": {"session": "my-session", "level": "account", "_info": "v4"}, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.domain.mail.list')
            .expect_json_value(['params'], {'domain': 'example.com'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": [{"mail": "mail1@example.com", "type": "inbox"},
                                                       {"mail": "mail2@example.com", "type": "forward"}], "id": "adfc_ansible"}),
            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.domain.mail.add')
            .expect_json_value(['params'], {'domain': 'example.com', 'mail': 'ansible-test@example.com', 'pass': 'secret', 'memo': 'Ansible-Test', 'catchall': False, 'inboxsave': True, 'forwards': []})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": True, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'deauth')
            .result_json({"jsonrpc": "2.0", "result": True, "id": "adfc_ansible"}),
        ]
        )

        assert result['changed'] == True

    def test_successfull_modify_run(self, mocker):
        result = self.run_module_success(mocker, email_account, {
            'login': {
                'user': 'my-user',
                'password': 'my-pass'
            },
            'email': 'mail1@example.com',
            'memo': 'Ansible-Test NEW',
            'forwards': ['my-forward@example.com'],
            'mail_type': 'inboxforward',
            '_ansible_diff': True,
            '_ansible_remote_tmp': '/tmp/tmp',
            '_ansible_keep_remote_files': True,
        }, [
            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'auth')
            .expect_json_value(['params'], {'pass': 'my-pass', 'user': 'my-user'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": {"session": "my-session", "level": "account", "_info": "v4"}, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.domain.mail.list')
            .expect_json_value(['params'], {'domain': 'example.com'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": [{"mail": "mail1@example.com", "type": "inbox"},
                                                       {"mail": "mail2@example.com", "type": "forward"}], "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.mail.get')
            .expect_json_value(['params'], {'mail': 'mail1@example.com'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": {
                'mail': 'mail1@example.com',
                'forwards': [],
                'type': 'inbox',
                'memo': 'Ansible-Test OLD',
            }, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.mail.memo.set')
            .expect_json_value(['params'], {'mail': 'mail1@example.com', 'memo': 'Ansible-Test NEW'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": True, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.mail.inboxsave.set')
            .expect_json_value(['params'], {'mail': 'mail1@example.com', 'inboxsave': True})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": True, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.mail.forward.set')
            .expect_json_value(['params'], {'mail': 'mail1@example.com', 'forwards': ['my-forward@example.com']})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": True, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'deauth')
            .result_json({"jsonrpc": "2.0", "result": True, "id": "adfc_ansible"}),
        ]
        )

        assert result['changed'] == True

    def test_successfull_password_set(self, mocker):
        result = self.run_module_success(mocker, email_account, {
            'login': {
                'user': 'my-user',
                'password': 'my-pass'
            },
            'email': 'mail1@example.com',
            'memo': 'Ansible-Test',
            'password': 'new-pass',
            'mail_type': 'inbox',
            'force_password_set': True,
            '_ansible_remote_tmp': '/tmp/tmp',
            '_ansible_keep_remote_files': True,
        }, [
            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'auth')
            .expect_json_value(['params'], {'pass': 'my-pass', 'user': 'my-user'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": {"session": "my-session", "level": "account", "_info": "v4"}, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.domain.mail.list')
            .expect_json_value(['params'], {'domain': 'example.com'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": [{"mail": "mail1@example.com", "type": "inbox"},
                                                       {"mail": "mail2@example.com", "type": "forward"}], "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.mail.get')
            .expect_json_value(['params'], {'mail': 'mail1@example.com'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": {
                'mail': 'mail1@example.com',
                'forwards': [],
                'type': 'inbox',
                'memo': 'Ansible-Test',
            }, "id": "adfc_ansible"}),


            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.mail.password.set')
            .expect_json_value(['params'], {'mail': 'mail1@example.com', 'password': 'new-pass'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": True, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'deauth')
            .result_json({"jsonrpc": "2.0", "result": True, "id": "adfc_ansible"}),
        ]
        )

        assert result['changed'] == True

    def test_successfull_del_run(self, mocker):
        result = self.run_module_success(mocker, email_account, {
            'login': {
                'user': 'my-user',
                'password': 'my-pass'
            },
            'email': 'mail2@example.com',
            'state': 'absent',
            '_ansible_remote_tmp': '/tmp/tmp',
            '_ansible_keep_remote_files': True,
        }, [
            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'auth')
            .expect_json_value(['params'], {'pass': 'my-pass', 'user': 'my-user'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": {"session": "my-session", "level": "account", "_info": "v4"}, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.domain.mail.list')
            .expect_json_value(['params'], {'domain': 'example.com'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": [{"mail": "mail1@example.com", "type": "inbox"},
                                                       {"mail": "mail2@example.com", "type": "forward"}], "id": "adfc_ansible"}),
            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.domain.mail.del')
            .expect_json_value(['params'], {'domain': 'example.com', 'mail': 'mail2@example.com'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": True, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'deauth')
            .result_json({"jsonrpc": "2.0", "result": True, "id": "adfc_ansible"}),
        ]
        )

        assert result['changed'] == True

    def test_successfull_del_not_existing(self, mocker):
        result = self.run_module_success(mocker, email_account, {
            'login': {
                'user': 'my-user',
                'password': 'my-pass'
            },
            'email': 'mail3@example.com',
            'state': 'absent',
            '_ansible_remote_tmp': '/tmp/tmp',
            '_ansible_keep_remote_files': True,
        }, [
            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'auth')
            .expect_json_value(['params'], {'pass': 'my-pass', 'user': 'my-user'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": {"session": "my-session", "level": "account", "_info": "v4"}, "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'q.domain.mail.list')
            .expect_json_value(['params'], {'domain': 'example.com'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"jsonrpc": "2.0", "result": [{"mail": "mail1@example.com", "type": "inbox"},
                                                       {"mail": "mail2@example.com", "type": "forward"}], "id": "adfc_ansible"}),

            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_header('Hpls-Auth', 'my-session')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['method'], 'deauth')
            .result_json({"jsonrpc": "2.0", "result": True, "id": "adfc_ansible"}),
        ]
        )

        assert result['changed'] == False
