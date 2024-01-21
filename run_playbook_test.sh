#!/bin/sh
TMPDIR=$(mktemp -d)
ansible-galaxy collection build --output-path "$TMPDIR" .
ansible-galaxy collection install --force "$TMPDIR"/hamburg_adfc-jpberlin-*.tar.gz
rm -rf "$TMPDIR"
ansible-playbook --diff --check -vvv example/my_play.yml
ansible-playbook --diff  -v example/my_play.yml
