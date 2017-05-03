
ARMADA_DEFINITION = 'armada'
RELEASE_PREFIX = 'release_prefix'
CHARTS_DEFINITION = 'charts'


def valid_manifest(config):
    if not (isinstance(config.get(ARMADA_DEFINITION, None), dict)):
        raise Exception("Did not declare armada object")

    armada_config = config.get('armada')

    if not isinstance(armada_config.get(RELEASE_PREFIX), basestring):
        raise Exception('Release needs to be a string')

    if not isinstance(armada_config.get(CHARTS_DEFINITION), list):
        raise Exception('Check yaml invalid chart definition must be array')

    for chart in armada_config.get('charts', []):
        if not isinstance(chart.get('chart').get('name'), basestring):
            raise Exception('Chart name needs to be a string')

    return True
