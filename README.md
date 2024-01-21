# Ansible Collection to create e-mail addresses for jpberlin with ansible

This collection can set and modify e-mail accounts for jpberlin.de. Perhabs (not tested), it works also for mailbox.org.

## Install

```bash
# On Apt
apt install python3-validator
# Or with
pip install validator

# Install Collection:
ansible-galaxy collection install git+https://github.com/ADFC-Hamburg/ansible-jpberlin
```

## Example:


```yaml
    - name: Create E-Mail
      hamburg_adfc.jpberlin.email_account:
        login:
          user: "my-user"
          password: "login-password"
        email: ansible.test@example.com
        password: "my-secret"
        memo: "Ansible Test"

    - name: Create E-Mail Forward
      hamburg_adfc.jpberlin.email_account:
        login:
          user: "my-user"
          password: "login-password"
        email: ansible-forward1@example.com
        forwards:
          - ansible-forward2@example.com
          - ansible-forward3@example.com
        mail_type: forward
        password: "my-secret"
```

# Questions

Please use Github Issues: https://github.com/ADFC-Hamburg/ansible-jpberlin/issues/new


# Donations

See:

https://hamburg.adfc.de/spende

Please use the keyword: ansible-jpberlin
