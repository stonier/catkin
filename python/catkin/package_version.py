from __future__ import print_function
import os
import re


def bump_version(version, bump='patch'):
    """
    Increases version number.

    :param version: str, must be in version format "int.int.int"
    :param bump: str, one of 'patch, minor, major'
    :returns: version with the given part increased, and all inferior parts reset to 0
    """
    # split the version number
    match = re.match('^(\d+)\.(\d+)\.(\d+)$', version)
    if match is None:
        raise ValueError('Invalid version string, must be int.int.int: "%s"' % version)
    new_version = match.groups()
    new_version = [int(x) for x in new_version]
    # find the desired index
    idx = dict(major=0, minor=1, patch=2)[bump]
    # increment the desired part
    new_version[idx] += 1
    # reset all parts behind the bumped part
    new_version = new_version[:idx + 1] + [0 for x in new_version[idx + 1:]]
    return '%d.%d.%d' % tuple(new_version)


def _replace_version(package_str, new_version):
    """
    replaces the version tag in contents if there is only one instance

    :param package_str: str contents of package.xml
    :param new_version: str version number
    :returns: str new package.xml
    :raises RuntimeError:
    """
    # try to replace contens
    new_package_str, number_of_subs = re.subn('<version([^<>]*)>[^<>]*</version>', '<version\g<1>>%s</version>' % new_version, package_str)
    if number_of_subs != 1:
        raise RuntimeError('Illegal number of version tags: %s' % (number_of_subs))
    return new_package_str


def _check_for_version_comment(package_str, new_version):
    """
    checks if a comment is present behind the version tag and return it

    :param package_str: str contents of package.xml
    :param version: str version number
    :returns: str comment if available, else None
    """
    version_tag = '>%s</version>' % new_version
    pattern = '%s[ \t]*%s *(.+) *%s' % (re.escape(version_tag), re.escape('<!--'), re.escape('-->'))
    comment = re.search(pattern, package_str)
    if comment:
        comment = comment.group(1)
    return comment


def update_versions(paths, new_version):
    """
    bulk replace of version: searches for package.xml files directly in given folders and replaces version tag within.

    :param paths: list of string, folder names
    :param new_version: version string "int.int.int"
    :raises RuntimeError: if any one package.xml cannot be updated
    """
    files = {}
    for path in paths:
        package_path = os.path.join(path, 'package.xml')
        with open(package_path, 'r') as f:
            package_str = f.read()
        try:
            new_package_str = _replace_version(package_str, new_version)
            comment = _check_for_version_comment(new_package_str, new_version)
            if comment:
                print('NOTE: The package manifest "%s" contains a comment besides the version tag:\n  %s' % (path, comment))
        except RuntimeError as rue:
            raise RuntimeError('Could not bump version number in file %s: %s' % (package_path, str(rue)))
        files[package_path] = new_package_str
    # if all replacements successful, write back modified package.xml
    for package_path, new_package_str in files.iteritems():
        with open(package_path, 'w') as f:
            f.write(new_package_str)