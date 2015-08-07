#!/usr/bin/env python

import os
import re
import sys
from time import sleep
from scaleway.apis import ComputeAPI,AccountAPI

def main():
  module = AnsibleModule(
    argument_spec = dict(
    state         = dict(default='running', choices=['running', 'stopped', 'terminated', 'deleted']),
    name          = dict(required=False),
    environment   = dict(default=None),
    restarted     = dict(default=False, choices=BOOLEANS),
    delay         = dict(default=5),
    batch         = dict(default=10),
    )
  )

  api = ComputeAPI(auth_token=os.environ['SCW_TOKEN'])
  account = AccountAPI(auth_token=os.environ['SCW_TOKEN'])

  organizations = account.query().organizations.get()
  organization_id = organizations['organizations'][0]['id']

  environment = "environment:" + str(module.params.get('environment'))
  name = module.params.get('name')
  delay = int(module.params.get('delay'))
  batch = int(module.params.get('batch'))

  servers = api.query().servers.get()['servers']

  action_servers = []

  for server in servers:
    if server['name'] == name:
      action_servers.append(server)
    if environment in server['tags']:
      action_servers.append(server)

  def generic_action(server_id, action):
      api.query().servers(server_id).action.post({'action': action})

  if module.params.get('restarted'):
    for server in action_servers:
      if server['state'] == 'running':
        generic_action(server['id'], 'reboot')
        sleep(delay)
  else:
    if module.params.get('state') == 'running':
      for server in action_servers:
        if server['state'] == 'stopped':
          generic_action(server['id'], 'poweron')
          sleep(delay)
          batch -= 1
          if batch == 0: break
    if module.params.get('state') == 'stopped':
      for server in action_servers:
        if server['state'] == 'running':
          generic_action(server['id'], 'poweroff')
          sleep(delay)
          batch -= 1
          if batch == 0: break
    if module.params.get('state') == 'terminated':
        for server in action_servers:
          if server['state'] == 'running':
            generic_action(server['id'], 'terminate')
    if module.params.get('state') == 'deleted':
        for server in action_servers:
          if server['state'] == 'stopped':
            api.query().servers(server).delete()

  module.exit_json(failed=False, success=True, msg="OK")

from ansible.module_utils.basic import *
main()

