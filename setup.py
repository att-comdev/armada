from setuptools.command.test import test as TestCommand
import sys
import setuptools

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


try:
    import multiprocessing  # noqa
except ImportError:
    pass

setuptools.setup(
    setup_requires=['pbr>=2.0.0'],
    pbr=True)
