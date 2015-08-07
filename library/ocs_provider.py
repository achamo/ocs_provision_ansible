#!/usr/bin/env python

import os
import re
import sys
from time import sleep
from scaleway.apis import ComputeAPI,AccountAPI

def main():
  module = AnsibleModule(
    argument_spec = dict(
    state         = dict(default='running', choices=['running', 'stopped', 'terminated']),
    name          = dict(required=True),
    image         = dict(required=True),
    environment   = dict(default=None),
    tags          = dict(default=None, type='list'),
    volumes       = dict(default=None, type='list'),
    restarted     = dict(default=False)
    )
  )

  api = ComputeAPI(auth_token=os.environ['SCW_TOKEN'])
  account = AccountAPI(auth_token=os.environ['SCW_TOKEN'])

  organizations = account.query().organizations.get()
  organization_id = organizations['organizations'][0]['id']

  tags = module.params.get('tags')
  environment = module.params.get('environment')
  volumes = module.params.get('volumes')

  volume_name = "extra-volume-%s" % (module.params.get('name'))

  volume_ids = []
  if volumes != None:
    for volume in volumes:
      volume_id = api.query().volumes.post({'name':volume_name,
                                            'organization': organization_id,
                                            'size': volume.get('size'),
                                            'volume_type': volume.get('type')
                                            })
      volume_ids.append(volume_id['volume'])

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

  volume_idx = 1
  for volume_id in volume_ids:
      res['server']['volumes']['%s' % (volume_idx)] = {'id': volume_id['id'], 'name': volume_id['name'] }
      volume_idx += 1

  api.query().servers(res['server']['id']).put(res['server'])

  if module.params.get('restarted') == True:
    api.query().servers(res['server']['id']).action.post({'action': 'reboot'})
  else:
    if module.params.get('state') == 'running':
      api.query().servers(res['server']['id']).action.post({'action': 'poweron'})
    if module.params.get('state') == 'stopped':
      api.query().servers(res['server']['id']).action.post({'action': 'poweroff'})
    if module.params.get('state') == 'terminated':
      api.query().servers(res['server']['id']).action.post({'action': 'terminate'})

  module.exit_json(failed=False, success=True, msg="coincoin")

from ansible.module_utils.basic import *
main()

