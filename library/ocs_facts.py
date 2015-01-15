#!/usr/bin/env python

import sys
import os
import json
import httplib

def main():
  module = AnsibleModule(
    argument_spec = dict(
    )
  )

  conn = httplib.HTTPConnection("169.254.42.42")
  conn.request("GET", "/conf?format=json")
  res = conn.getresponse()
  data = res.read()
  raw_facts = json.loads(data)
  facts = {}
  for k,v in raw_facts.iteritems():
    facts["ocs_{0}".format(k)] = v

  result = { 'ansible_facts': facts }
  module.exit_json(**result)


from ansible.module_utils.basic import *
main()

