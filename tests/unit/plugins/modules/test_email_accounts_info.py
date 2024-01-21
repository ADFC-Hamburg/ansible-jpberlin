# -*- coding: utf-8 -*-
# (c) 2021 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    BaseTestModule,
    FetchUrlCall,
)

from ansible_collections.hamburg_adfc.jpberlin.plugins.modules import email_accounts_info

# These imports are needed so patching below works
import ansible_collections.hamburg_adfc.jpberlin.plugins.module_utils.jp_api_module  # noqa


class TestEmailAccounts(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.hamburg_adfc.jpberlin.plugins.modules.email_accounts_info.JPAPIModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.hamburg_adfc.jpberlin.plugins.module_utils.jp_api_module.fetch_url'

    def test_invalid_login_response(self, mocker):
        result = self.run_module_failed(mocker, email_accounts_info, {
            'login': {
                'user': 'my-user',
                'password': 'my-pass'
            },
            'domain': 'example.com',
            '_ansible_remote_tmp': '/tmp/tmp',
            '_ansible_keep_remote_files': True,
        }, [
            FetchUrlCall('POST', 200)
            .expect_header('Content-type', 'application/json')
            .expect_url('https://api.mx.heinlein-hosting.de/', without_query=True)
            .expect_json_value(['params'], {'pass': 'my-pass', 'user': 'my-user'})
            .expect_json_value(['jsonrpc'], "2.0")
            .return_header('Content-Type', 'application/json')
            .result_json({"huhu": 32}),
        ])

        assert result['msg'] == 'result not found in result'

    def test_invalid_domain(self, mocker):
        result = self.run_module_failed(mocker, email_accounts_info, {
            'login': {
                'user': 'my-user',
                'password': 'my-pass',
                'jrpc_url': 'https://wrong-url:99999999/'
                ''
            },
            'domain': 'example.com',
            '_ansible_remote_tmp': '/tmp/tmp',
            '_ansible_keep_remote_files': True,
        }, [
        ])

        assert 'is not a valid url' in result['msg']

    def test_empty_login_pass(self, mocker):
        result = self.run_module_failed(mocker, email_accounts_info, {
            'login': {
                'user': 'my-user',
                'password': '',
            },
            'domain': 'example.com',
            '_ansible_remote_tmp': '/tmp/tmp',
            '_ansible_keep_remote_files': True,
        }, [
        ])

        assert 'password must not be empty' in result['msg']

    def test_successfull_run(self, mocker):
        result = self.run_module_success(mocker, email_accounts_info, {
            'login': {
                'user': 'my-user',
                'password': 'my-pass'
            },
            'domain': 'example.com',
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
        assert len(result['mail_accounts']) == 2
        assert result['mail_accounts'][0]['email'] == 'mail1@example.com'
        assert result['mail_accounts'][0]['type'] == 'inbox'
