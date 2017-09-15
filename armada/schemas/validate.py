#!/usr/bin/env python

import yaml
from jsonschema import validate
chart = 'armada/Chart/v1'
chart_group = 'armada/ChartGroup/v1'
manifest = 'armada/Manifest/v1'

SCHEMA = {}

def _load_schemas():
    pass

def validate_armada_documents(schema, documents):
    pass


schema = yaml.safe_load(open('armada-manifest-schema.yaml').read())
print schema

manifest = yaml.safe_load(open('simple-test.yaml').read())
print manifest

print validate(manifest.get('data'), schema.get('data'))
