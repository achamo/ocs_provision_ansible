#!/usr/bin/env python

import os
import re
import sys
from ocs_sdk.apis import ComputeAPI,AccountAPI

def main():
  module = AnsibleModule(
    argument_spec = dict(
    state         = dict(default='running', choices=['running', 'stopped']),
    name          = dict(required=True),
    image         = dict(required=True),
    environment   = dict(default=None),
    tags          = dict(default=None, type='list'),
    )
  )

  api = ComputeAPI(auth_token=os.environ['OCS_TOKEN'])
  account = AccountAPI(auth_token=os.environ['OCS_TOKEN'])

  organizations = account.query().organizations.get()
  organization_id = organizations['organizations'][0]['id']

  tags = module.params.get('tags')
  environment = module.params.get('environment')
  if tags == None:
    tags = []
  if environment != None:
    tags.append("environment:{0}".format(environment))


  images = api.query().images.get()['images']
  images_id = [ image['id'] for image in images if re.search(module.params.get('image'), image['name']) ]

  res = api.query().servers.post({'name': module.params.get('name'),
                                  'organization': organization_id,
                                  'image': images_id.pop(),
                                  'tags': tags})

  if module.params.get('state') == 'running':
    api.query().servers(res['server']['id']).action.post({'action': 'poweron'})

  module.exit_json(failed=False, success=True, msg="coincoin")

from ansible.module_utils.basic import *
main()

