from __future__ import print_function
import os

CATKIN_MARKER_FILE = '.catkin'


def get_workspaces():
    """
    Based on CMAKE_PREFIX_PATH return all catkin workspaces

    :param _environ: environment module to use, ``dict``
    """
    # get all cmake prefix paths
    env_name = 'CMAKE_PREFIX_PATH'
    paths = [path for path in os.environ.get(env_name, '').split(os.pathsep) if path]
    # remove non-workspace paths
    workspaces = [path for path in paths if os.path.isfile(os.path.join(path, CATKIN_MARKER_FILE))]
    return workspaces


def get_source_paths(workspace):
    """
    reads catkin workspace files and returns the list of all declared
    source paths

    :param workspace: path to catkin workspace folder, ``str``
    """
    # determine source spaces
    data = ''
    filename = os.path.join(workspace, CATKIN_MARKER_FILE)
    if not os.path.isfile(filename):
        raise ValueError('Not a catkin workspace: "%s", missing file %s' % (workspace, filename))
    with open(filename) as f:
        data = f.read()

    if data == '':
        source_paths = []
    else:
        source_paths = data.split(';')
    return source_paths
