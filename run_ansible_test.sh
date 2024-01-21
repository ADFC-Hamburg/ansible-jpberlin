#!/bin/sh
TMPDIR=$(mktemp -d)
ansible-galaxy collection build --output-path "$TMPDIR" .
ansible-galaxy collection install --force "$TMPDIR"/hamburg_adfc-jpberlin-*.tar.gz
rm -rf "$TMPDIR"
MYDIR=$(pwd)
cd ~/.ansible/collections/ansible_collections/hamburg_adfc/jpberlin
#ansible-test sanity --docker default  -v --python 3.11
ansible-test coverage erase
ansible-test units --requirements --coverage  --docker default  -v --python 3.11
echo cov html
ansible-test coverage html  -v --python 3.11
ansible-test coverage report  -v --python 3.11
cd "$MYDIR"
