from setuptools import setup

setup(
    name = 'armada',
    version = '0.1.0',
    description = 'Armada Helm Orchestrator',
    packages = ['armada',
                'hapi',
                'hapi.chart',
                'hapi.release',
                'hapi.services',
                'hapi.version'
    ],
    scripts = ['scripts/armada']
)
