#!/bin/bash
ansible-galaxy collection build --force .
ansible-galaxy collection install --force hamburg_adfc-jpberlin-0.1.0.tar.gz
ansible-playbook --diff --check -vvv example/my_play.yml
ansible-playbook --diff  -v example/my_play.yml
