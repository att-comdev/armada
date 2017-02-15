from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

class Tox(TestCommand):
    """Runs Tox comands"""
    def finalize_options(self):
        """preps test suite"""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """runs test suite"""
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


setup(
    name='armada',
    version='0.1.0',
    description='Armada Helm Orchestrator',
    packages=['armada',
              'hapi',
              'hapi.chart',
              'hapi.release',
              'hapi.services',
              'hapi.version'],
    scripts=['scripts/armada']
)
