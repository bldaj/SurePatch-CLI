#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# inputs

import sys
import platform
import argparse

from core.api import API
from core.api import OSs
from core.api import Methods
from core.api import Formats
from core.interface import print_line
from core.interface import print_logo

api = API()


def create_parser():
    """
    Create argument parser.
    :return: parser
    """

    parser = argparse.ArgumentParser(
        description="SurePatch Argument Parser")

    parser.add_argument(
        '--action',
        type=str,
        required=False,
        help='Define action: '
             'save_config, '
             'create_platform, '
             'create_project, '
             'create_set, '
             'show_platforms, '
             'show_projects, '
             'show_set, '
             'show_issues')

    parser.add_argument(
        '--file',
        type=str,
        required=False,
        help="Define file name")

    parser.add_argument(
        '--target',
        type=str,
        required=False,
        help="Define SurePatch target (os/pip/requirements/npm/packages_json/gem/gemlist/gemfile...)")

    parser.add_argument(
        '--method',
        type=str,
        required=False,
        help="Define packages collection mode (auto/manual/file)")

    parser.add_argument(
        '--format',
        type=str,
        required=False,
        help='Define file format (system/user)')

    parser.add_argument(
        '--team',
        type=str,
        required=False,
        help="Define your team")
    parser.add_argument(
        '--user',
        type=str,
        required=False,
        help="Define Username/email")
    parser.add_argument(
        '--password',
        type=str,
        required=False,
        help="Define Password")

    parser.add_argument(
        '--platform',
        type=str,
        required=False,
        help="Define Platform name")
    parser.add_argument(
        '--description',
        type=str,
        required=False,
        nargs='?',
        help="Define Project description")
    parser.add_argument(
        '--project',
        type=str,
        required=False,
        help="Define Project name")
    parser.add_argument(
        '--set',
        type=str,
        required=False,
        help='Define Set name. If is set None - \
            set name will be incremented automatically')
    parser.add_argument(
        '--auth_token',
        type=str,
        required=False,
        help='Define token from your web dashboard \
        to login without password'
    )
    parser.add_argument(
        '--logo',
        type=str,
        required=False,
        help='Print logo or not (on/off)'
    )
    return parser.parse_args()


def get_os_platform():
    """
    Get OS platform type.
    :return: platform
    """

    if sys.platform == 'darwin' or platform.system() == 'Darwin':
        return OSs.MACOS
    if sys.platform == 'linux2' or sys.platform == 'linux':
        dist = platform.dist()[0]
        if 'debian' in dist:
            return OSs.DEBIAN
        if 'fedora' in dist:
            return OSs.FEDORA
        if 'Ubuntu' in dist or 'ubuntu' in dist:
            return OSs.UBUNTU
    if sys.platform == 'win32' or sys.platform == 'win64':
        return OSs.WINDOWS


def get_os_version(os_platform):
    """
    Get OS version.
    :param os_platform: os
    :return: result
    """
    if os_platform == 'windows':
        return platform.uname()[2]
    return ''


def get_os_sp(os_platform):
    """
    Get OS service pack (for Windows)
    :param os_platform: os
    :return: SP
    """

    if os_platform == 'windows':
        return platform.win32_ver()[2][2:]
    return ''


def get_os_release() :
    """
    Get OS release.
    :return: release
    """

    return platform.release()


def get_os_machine():
    """
    Get OS machine code.
    :return: machine code
    """

    return platform.machine()


def main():
    """
    Application main function.
    :return:
    """

    arguments = create_parser()
    api_data = dict(
        action=arguments.action,
        team=arguments.team,
        user=arguments.user,
        password=arguments.password,
        file=arguments.file,
        target=arguments.target,
        method=arguments.method,
        format=arguments.format,
        platform=arguments.platform,
        description=arguments.description,
        project=arguments.project,
        set=arguments.set,
        os_type=get_os_platform(),
        os_version=get_os_version(get_os_platform()),
        os_sp=get_os_sp(get_os_platform()),
        os_release=get_os_release(),
        os_machine=get_os_machine(),
        components=[],
        auth_token=arguments.auth_token,
        logo=arguments.logo
    )

    if arguments.logo is not None:
        if arguments.logo == 'on':
            print_logo()

    if api_data['auth_token'] is not None and api_data['auth_token'] != '':
        api_data['login_method'] = 'token'
    else:
        if (api_data['user'] is not None and api_data['user'] != '') and \
                api_data['password'] is not None and api_data['password'] != '':
            api_data['login_method'] = 'username_and_password'
        else:
            api_data['login_method'] = 'config_file'

    if api_data['target'] is None:
        api_data['target'] = ''

    if api_data['file'] is None:
        api_data['file'] = 'no'

    if api_data['method'] is None:
        api_data['method'] = Methods.AUTO

    if api_data['format'] is None:
        api_data['format'] = Formats.SYSTEM

    targets = api_data['target'].replace('[', '').replace(']', '').replace(' ', '').split(',')
    if len(targets) == 0:
        print_line('Wrong number of targets.')
        return 1
    api_data['target'] = targets
    files = api_data['file'].replace('[', '').replace(']', '').replace(' ', '').split(',')
    if len(targets) != len(files):
        print_line('Number of targets not equals number of files. For targets, that do not require files - use "no".')
        print_line('For example: ... --target[os,req] --file=no,/home/user/project/requirements.txt.')
        return 1
    api_data['file'] = []
    for file in files:
        if file == 'no':
            api_data['file'].append(None)
        else:
            api_data['file'].append(file)
    api_data['components'] = []

    if api.run_action(api_data=api_data):
        print_line('Complete successfully with targets {0}'.format(targets))
        print_line('Process {0} components'.format(len(api_data['components'])))
    else:
        print_line('Complete with errors with targets {0}'.format(targets))
    return 0


if __name__ == '__main__':
    """
    Entry point
    """

    sys.exit(main())
