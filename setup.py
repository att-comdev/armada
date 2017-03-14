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


# In python < 2.7.4, a lazy loading of package `pbr` will break
# setuptools if some other modules registered functions in `atexit`.
# solution from: http://bugs.python.org/issue15881#msg170215

try:
    import multiprocessing  # noqa
except ImportError:
    pass

setuptools.setup(
    setup_requires=['pbr'],
    extras_require={'zabbix': ['pyzabbix==0.7.3']},
    pbr=True)
