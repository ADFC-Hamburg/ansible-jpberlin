#!/bin/sh
TMPDIR=$(mktemp -d)
ansible-galaxy collection build --output-path "$TMPDIR" .
ansible-galaxy collection install --force "$TMPDIR"/hamburg_adfc-jpberlin-*.tar.gz
rm -rf "$TMPDIR"
MYDIR=$(pwd)
cd ~/.ansible/collections/ansible_collections/hamburg_adfc/jpberlin
#ansible-test sanity --docker --python "3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11" -v default
ansible-test sanity --docker default --python 3.5 --python 3.6 --python 3.7 --python 3.8 --python 3.9 --python 3.10  -v
cd "$MYDIR"
