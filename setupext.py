from operator import attrgetter

from pkg_resources import parse_requirements


def read_requirements_from_file(file_path, include_versions=False):
    if include_versions:
        to_string = str
    else:
        to_string = attrgetter('project_name')

    handle = None
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
