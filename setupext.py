from operator import attrgetter

from pkg_resources import parse_requirements
from setuptools import Command
from setuptools.command.test import test as TestCommand


def read_requirements_from_file(file_path, include_versions=False):
    if include_versions:
        to_string = str
    else:
        to_string = attrgetter('project_name')

    requirements = []
    with open(file_path) as handle:
        for line_no, line in enumerate(handle, 1):
            try:
                for req in parse_requirements([line]):
                    requirements.append(to_string(req))
            except ValueError as exc:
                print('Warning: {0} ({1}:{2})'.format(
                    ' '.join(exc.args), file_path, line_no))

    return requirements


class Tox(Command):

    user_options = [
        ('environment=', 'e', 'only run this set of environments'),
        ('only=', 'o', 'only run these tests'),
        ('with-coverage', None, 'generate coverage report'),
    ]

    def initialize_options(self):
        self.environment = None
        self.only = None
        self.with_coverage = False

    def finalize_options(self):
        self.tox_args = []
        addt_args = [
            r'--match=(^|[\b\._/])((The|When)|(have|be|should)_)',
            '--include=_tests',
        ]
        if self.environment:
            self.tox_args.append('-e')
            self.tox_args.append(self.environment)
        if self.with_coverage:
            packages = '{0},tests'.format(','.join(self.distribution.packages))
            addt_args.append('--cover-package={0}'.format(packages))
            addt_args.extend([
                '--with-coverage',
                '--cover-branches',
                '--cover-erase',
                '--cover-tests',
            ])
        if self.only:
            addt_args.extend(self.only.split())
        if addt_args:
            self.tox_args.append('--')
            self.tox_args.extend(addt_args)

    def run(self):
        import tox
        rc = tox.cmdline(self.tox_args)
        sys.exit(rc)
