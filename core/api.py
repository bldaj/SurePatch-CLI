# -*- coding: utf-8 -*-

import os
import re
import sys
import yaml
import json
import importlib
import subprocess

from core.interface import ask
from core.interface import print_line
from core.interface import print_platforms
from core.interface import print_projects
from core.interface import print_components

from core.webapi import WebAPI

try:
    import pip
    from pip.utils import get_installed_distributions
except ImportError as import_exception:
    print_line(f"Can't import pip get_installed_distributions.")
    print_line(f"Get an exception: {import_exception}.")
    sys.exit(0)


raw_npm_components = []


def walkdict(data):
    """
    Recursive dict processing for npm list parsing.
    :param data:
    :return:
    """
    for k, v in data.items():
        if isinstance(v, dict):
            walkdict(v)
        else:
            raw_npm_components.append({"name": k, "version": v})


class API(object):
    """Main CLI App API.
    """

    def __init__(self):
        self.web_api = WebAPI()

    # -------------------------------------------------------------------------
    # Run actions
    # -------------------------------------------------------------------------

    def run_action(self, api_data: dict) -> bool:
        """
        Main routing method for app actions.
        :param api_data: api data set
        :return: result, modify api_data
        """

        if not self.check_action_type_match(api_data=api_data):
            return False

        if api_data['action'] == Actions.SAVE_CONFIG:
            return self.save_config_to_file(api_data=api_data)

        if not self.load_config_from_file(api_data=api_data):
            return False

        if not self.action_login_server_success(api_data=api_data):
            return False

        if not self.get_organization_parameters_from_server(api_data=api_data):
            return False

        if api_data['action'] == Actions.CREATE_PLATFORM:
            return self.action_create_new_platform(api_data=api_data)

        elif api_data['action'] == Actions.CREATE_PROJECT:
            return self.action_create_new_project(api_data=api_data)

        elif api_data['action'] == Actions.CREATE_SET:
            return self.action_create_new_set(api_data=api_data)

        elif api_data['action'] == Actions.SHOW_PLATFORMS or \
                api_data['action'] == Actions.SHOW_PROJECTS or \
                api_data['action'] == Actions.SHOW_SET:
            return self.action_show_platforms_projects_or_sets(api_data=api_data)

        elif api_data['action'] == Actions.DELETE_PLATFORM:
            return self.action_delete_platform(api_data=api_data)

        elif api_data['action'] == Actions.DELETE_PROJECT:
            return self.action_delete_project(api_data=api_data)

        elif api_data['action'] == Actions.ARCHIVE_PLATFORM:
            return self.action_archive_platform(api_data=api_data)

        elif api_data['action'] == Actions.ARCHIVE_PROJECT:
            return self.action_archive_project(api_data=api_data)

        print_line(f"Unknown action code: {api_data['action']}.")
        return False

    # -------------------------------------------------------------------------
    # LOGIN
    # -------------------------------------------------------------------------

    def action_login_server_success(self, api_data: dict) -> bool:
        """
        Log in into server.
        :param api_data: api data set
        :return: result, modify api_data
        """

        return self.web_api.send_login_request(api_data=api_data)

    # -------------------------------------------------------------------------
    # GET ORGANIZATION PARAMETERS
    # -------------------------------------------------------------------------

    def get_organization_parameters_from_server(self, api_data: dict) -> bool:
        """
        Get organization parameters from Surepatch server and fill the
        appropriate structure.
        :param api_data: api data set
        :return: result, modify api_data
        """

        return self.web_api.send_get_organization_parameters_request(api_data=api_data)

    # -------------------------------------------------------------------------
    # PLATFORM
    # -------------------------------------------------------------------------

    def action_create_new_platform(self, api_data: dict) -> bool:
        """
        Run action: CREATE New Platform.
        :param api_data: api data set
        :return: result, modify api_data
        """

        if api_data['platform'] is None or api_data['platform'] == '':
            print_line('Empty platform name, please use --platform flag.')
            return False

        if api_data['description'] is None or api_data['description'] == '':
            print_line('Empty platform description. Change description to "default platform".')
            api_data['description'] = "default platform"

        return self.web_api.send_create_new_platform_request(api_data=api_data)

    # -------------------------------------------------------------------------
    # PROJECT
    # -------------------------------------------------------------------------

    def action_create_new_project(self, api_data: dict) -> bool:
        """
        Run action: CREATE New Project in different cases.
        :param api_data: api data set
        :return: result, modify api_data
        """

        if api_data['platform'] is None or api_data['platform'] == '':
            print_line('Empty platform name.')
            return False

        if api_data['project'] is None or api_data['project'] == '':
            print_line('Empty project name.')
            return False

        platforms = self.get_my_platforms(api_data=api_data)

        if api_data['platform'] not in platforms:
            print_line(f"Platform {api_data['platform']} does not exists.")
            return False

        projects = self.get_my_projects(api_data=api_data)

        if api_data['project'] in projects:
            print_line(f"Project {api_data['project']} already exists.")
            return False

        # Select variant of CREATE Project action

        # Create new project with OS packages {from shell request}
        if api_data['target'] == Targets.OS and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is None:
            return self.create_project_os_auto_system_none(api_data=api_data)

        # Create new project with OS packages from shell request unloading file {from path}
        if api_data['target'] == Targets.OS and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_os_auto_system_path(api_data=api_data)

        # Create new project with PIP packages {from shell request}
        if api_data['target'] == Targets.PIP and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is None:
            return self.create_project_pip_auto_system_none(api_data=api_data)

        # Create new project with PIP from file {from path}
        if api_data['target'] == Targets.PIP and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_pip_auto_system_path(api_data=api_data)

        # Create new project with PIP requirements.txt {from path}
        if api_data['target'] == Targets.REQ and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_requirements_auto_system_path(api_data=api_data)

        # Create new project with NPM packages {from shell request} - global
        if api_data['target'] == Targets.NPM and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is None:
            return self.create_project_npm_auto_system_none(api_data=api_data)

        # Create new project with NPM packages {from shell request} - local
        if api_data['target'] == Targets.NPM_LOCAL and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_npm_local_auto_system_none(api_data=api_data)

        # Create new project with NPM packages {from file}
        if api_data['target'] == Targets.NPM and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_npm_auto_system_path(api_data=api_data)

        # Create new project with NPM package.json file {from path}
        if api_data['target'] == Targets.PACKAGE_JSON and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_package_json_auto_system_path(api_data=api_data)

        # Create new project with NPM package_lock.json file {from path}
        if api_data['target'] == Targets.PACKAGE_LOCK_JSON and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_package_lock_json_auto_system_path(api_data=api_data)

        # Create new project with GEM packages {from shell request}
        if api_data['target'] == Targets.GEM and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is None:
            return self.create_project_gem_auto_system_none(api_data=api_data)

        # Create new project with GEM packages from shell request unloading file {from path}
        if api_data['target'] == Targets.GEM and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_gem_auto_system_path(api_data=api_data)

        # Create new project with GEMFILE file {from path}
        if api_data['target'] == Targets.GEMFILE and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_gemfile_auto_system_path(api_data=api_data)

        # Create new project with GEMFILE.lock file {from path}
        if api_data['target'] == Targets.GEMFILE_LOCK and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_gemfile_lock_auto_system_path(api_data=api_data)

        if api_data['method'] == Methods.AUTO and \
                    api_data['format'] == Formats.USER and \
                    api_data['file'] is not None:
                return self.create_project_any_auto_user_path(api_data=api_data)

        if api_data['method'] == Methods.MANUAL and \
                api_data['format'] == Formats.USER and \
                api_data['file'] is None:
            return self.create_project_any_manual_user_none(api_data=api_data)

        print_line('Something wrong with app parameters. Please, look through README.md')
        return False

    # Target = OS packages

    def create_project_os_auto_system_none(self, api_data: dict) -> bool:
        """
        Create project with OS packages, collected by shell command.
        :param api_data: api data set
        :return: result, modify api_data
        """

        components = self.get_components_os_auto_system_none(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_os_auto_system_path(self, api_data: dict) -> bool:
        """
        Create project with OS packages, collected from shell command
        and stored in file, defined in path.
        :param api_data: api data set
        :return: result, modify api_data
        """

        components = self.get_components_os_auto_system_path(api_data=api_data)
        
        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    # Target = Python packages

    def create_project_pip_auto_system_none(self, api_data: dict) -> bool:
        """
        Create project with Python PIP packages, collected from shell command.
        :param api_data: api data set
        :return: result, modify api_data
        """
        components = self.get_components_pip_auto_system_none(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_pip_auto_system_path(self, api_data: dict) -> bool:
        """
        Create project with Python PIP packages, collected from shell command
        and stored in file, defined in path.
        :param api_data: api data set
        :return: result, modify api_data
        """
        components = self.get_components_pip_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_requirements_auto_system_path(self, api_data: dict) -> bool:
        """
        Create project with Python requirements.txt file, defined in path.
        :param api_data: api data set
        :return: result, modify api_data
        """
        components = self.get_components_requirements_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    # Target = NodeJS NPM packages

    def create_project_npm_auto_system_none(self, api_data: dict) -> bool:
        """
        Create project with NPM packages, collected from shell command (nmp list --json).
        Shell command runs global from root path.
        :param api_data: api data set
        :return: result, modify api_data
        """
        components = self.get_components_npm_auto_system_none(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_npm_auto_system_path(self, api_data: dict) -> bool:
        """
        Create project with NPM packages, collected from shell command (npm list --json)
        and stored in file, defined in path.
        :param api_data: api data set
        :return: result, modify api_data
        """
        components = self.get_components_npm_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_npm_local_auto_system_none(self, api_data: dict) -> bool:
        """
        Create project with NPM packages, collected from shell command (npm list --json).
        Shell command runs local from path, defined by --file parameter.
        :param api_data: api data set
        :return: result, modify api_data
        """
        components = self.get_components_npm_local_auto_system_none(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_package_lock_json_auto_system_path(self, api_data: dict) -> bool:
        """
        Create project with NPM packages from package-lock.json, defined by --file parameter.
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_npm_lock_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_package_json_auto_system_path(self, api_data: dict) -> bool:
        """
        Create project with NPM packages from package.json, defined by --file parameter.
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_package_json_auto_system_path(api_data=api_data)
        if components[0] is None:
            return False
        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    # Target = Ruby packages

    def create_project_gem_auto_system_none(self, api_data: dict) -> bool:
        """
        Create project with Ruby packages, collected from shell command.
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_gem_auto_system_none(api_data=api_data)
        if components[0] is None:
            return False
        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_gem_auto_system_path(self, api_data: dict) -> bool:
        """
        Create project with Ruby packages, collected from shell command and
        stored in gem list file, defined in --file parameter.
        :param api_data:
        :return:
        """
        components = self.get_components_gem_auto_system_path(api_data=api_data)
        if components[0] is None:
            return False
        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_gemfile_auto_system_path(self, api_data: dict) -> bool:
        """
        Create project with Ruby packages, collected from Gemfile, defined
        by --file parameter.
        :param api_data:
        :return:
        """
        components = self.get_components_gemfile_auto_system_path(api_data=api_data)
        if components[0] is None:
            return False
        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_gemfile_lock_auto_system_path(self, api_data: dict) -> bool:
        """
        Create project with Ruby packages, collected from Gemfile.lock file,
        defined by --file parameter.
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_gemfile_lock_auto_system_path(api_data=api_data)
        if components[0] is None:
            return False
        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_any_auto_user_path(self, api_data: dict) -> bool:
        """
        Create project with different packages, collected in file,
        defined by path with simple multiline format: name=version…
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_any_auto_user_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_any_manual_user_none(self, api_data: dict) -> bool:
        """
        Create project with different packages, asked in interactive mode.
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_any_manual_user_none()

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    # -------------------------------------------------------------------------
    # SET
    # -------------------------------------------------------------------------

    def action_create_new_set(self, api_data: dict) -> bool:
        """
        Run action: CREATE New Set in different cases.
        :param api_data: api data set
        :return: result, modify api_data
        """
        if api_data['platform'] is None:
            print_line('Empty Platform name. Please use --platform=platform_name parameter.')
            return False

        platforms = self.get_my_platforms(api_data=api_data)

        if api_data['platform'] not in platforms:
            print_line(f"Platform {api_data['platform']} does not exists.")
            return False

        if api_data['project'] is None:
            print_line('Empty Project name. Please use --project=project_name parameter.')
            return False

        projects = self.get_my_projects(api_data=api_data)

        if api_data['project'] not in projects:
            print_line(f"Project {api_data['project']} does not exists.")
            return False

        set_name = api_data['set']
        current_set_name = self.get_current_set_name(api_data=api_data)[0]

        if current_set_name == set_name:
            print_line(f'Current set with name {set_name} already exists.')
            print_line('Please, use another name, or use no --set parameter to autoincrement set name.')
            return False

        if set_name is None:
            if current_set_name[-1].isdigit():
                d = int(current_set_name[-1])
                d = d + 1
                current_set_name = current_set_name[:-1]
                set_name = current_set_name + str(d)

            else:
                set_name = current_set_name + '.1'

            api_data['set'] = set_name

        # Create new set with OS packages {from shell request}
        if api_data['target'] == Targets.OS and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is None:
            return self.create_set_os_auto_system_none(api_data=api_data)

        # Create set with OS packages from shell request unloading file {from path}
        if api_data['target'] == Targets.OS and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_set_os_auto_system_path(api_data=api_data)

        # Create set with PIP packages {from shell request}
        if api_data['target'] == Targets.PIP and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is None:
            return self.create_set_pip_auto_system_none(api_data=api_data)

        # Create set with PIP from file {from path}
        if api_data['target'] == Targets.PIP and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_set_pip_auto_system_path(api_data=api_data)

        # Create set with PIP requirements.txt {from path}
        if api_data['target'] == Targets.REQ and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_set_requirements_auto_system_path(api_data=api_data)

        if api_data['target'] == Targets.REQUIREMENTS and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_set_requirements_auto_system_path(api_data=api_data)

        # Create set with NPM packages {from shell request} - global
        if api_data['target'] == Targets.NPM and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is None:
            return self.create_set_npm_auto_system_none(api_data=api_data)

        # Create set with NPM packages {from shell request} - local
        if api_data['target'] == Targets.NPM_LOCAL and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_set_npm_local_auto_system_path(api_data=api_data)

        # Create set with NPM packages {from file}
        if api_data['target'] == Targets.NPM and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_set_npm_auto_system_path(api_data=api_data)

        # Create set with NPM package.json file {from path}
        if api_data['target'] == Targets.PACKAGE_JSON and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_set_package_json_auto_system_path(api_data=api_data)

        # Create set with NPM package_lock.json file {from path}
        if api_data['target'] == Targets.PACKAGE_LOCK_JSON and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_set_package_lock_json_auto_system_path(api_data=api_data)

        # Create set with GEM packages {from shell request}
        if api_data['target'] == Targets.GEM and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is None:
            return self.create_set_gem_auto_system_none(api_data=api_data)

        # Create set with GEM packages from shell request unloading file {from path}
        if api_data['target'] == Targets.GEM and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_set_gem_auto_system_path(api_data=api_data)

        # Create set with GEMLIST file {from path}
        if api_data['target'] == Targets.GEMFILE and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_set_gemfile_auto_system_path(api_data=api_data)

        # Create set with GEMLIST file {from path}
        if api_data['target'] == Targets.GEMFILE_LOCK and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_set_gemfile_lock_auto_system_path(api_data=api_data)

        if api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.USER and \
                api_data['file'] is not None:
            return self.create_set_any_auto_user_path(api_data=api_data)

        if api_data['method'] == Methods.MANUAL and \
                api_data['format'] == Formats.USER and \
                api_data['file'] is None:
            return self.create_set_any_manual_user_none(api_data=api_data)

    # Target = OS packages

    def create_set_os_auto_system_none(self, api_data: dict) -> bool:
        """
        Create Component Set with OS packages, collected by shell command.
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_os_auto_system_none(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_os_auto_system_path(self, api_data: dict) -> bool:
        """
        Create Component Set with OS packages, collected from shell command
        and stored in file, defined in path.
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_os_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    # Target = Python packages

    def create_set_pip_auto_system_none(self, api_data: dict) -> bool:
        """
        Create Component Set with Python PIP packages, collected from shell command.
        :param api_data:
        :return:
        """
        components = self.get_components_pip_auto_system_none(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_pip_auto_system_path(self, api_data: dict) -> bool:
        """
        Create Component Set with Python PIP packages, collected from shell command
        and stored in file, defined in path.
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_pip_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_requirements_auto_system_path(self, api_data: dict) -> bool:
        """
        Create Component Set with Python requirements.txt file, defined in path.
        :param api_data: spi data set
        :return: result
        """
        components = self.get_components_requirements_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_npm_auto_system_none(self, api_data: dict) -> bool:
        """
        Create Component Set with NPM packages, collected from shell command (nmp list --json).
        Shell command runs global from root path.
        :param api_data:
        :return:
        """
        components = self.get_components_npm_auto_system_none(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_npm_local_auto_system_path(self, api_data: dict) -> bool:
        """
        Create Component Set with NPM packages, collected from shell command (npm list --json).
        Shell command runs local from path, defined by --file parameter.
        :param api_data:
        :return:
        """
        components = self.get_components_npm_local_auto_system_none(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_npm_auto_system_path(self, api_data: dict) -> bool:
        """
        Create Component Set with NPM packages, collected from shell command (npm list --json)
        and stored in file, defined in path.
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_npm_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_package_json_auto_system_path(self, api_data: dict) -> bool:
        """
        Create Component Set with NPM packages from package.json, defined by --file parameter.
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_package_json_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_package_lock_json_auto_system_path(self, api_data: dict) -> bool:
        """
        Create Component Set with NPM packages from package-lock.json, defined by --file parameter.
        :param api_data:
        :return:
        """
        components = self.get_components_npm_local_auto_system_none(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_gem_auto_system_none(self, api_data: dict) -> bool:
        """
        Create Component Set with Ruby packages, collected from shell command.
        :param api_data:
        :return:
        """
        components = self.get_components_gem_auto_system_none(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_gem_auto_system_path(self, api_data: dict) -> bool:
        """
        Create Component Set with Ruby packages, collected from shell command and
        stored in gem list file, defined in --file parameter.
        :param api_data:
        :return:
        """
        components = self.get_components_gem_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_gemfile_auto_system_path(self, api_data: dict) -> bool:
        """
        Create Component Set with Ruby packages, collected from Gemfile, defined
        by --file parameter.
        :param api_data:
        :return:
        """
        components = self.get_components_gemfile_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_gemfile_lock_auto_system_path(self, api_data: dict) -> bool:
        """
        Create Component Set with Ruby packages, collected from Gemfile.lock file,
        defined by --file parameter.
        :param api_data:
        :return:
        """
        components = self.get_components_gemfile_lock_auto_system_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_any_auto_user_path(self, api_data: dict) -> bool:
        """
        Create Component Set with different packages, collected in file,
        defined by path with simple multiline format: name=version…
        :param api_data:
        :return:
        """
        components = self.get_components_any_auto_user_path(api_data=api_data)

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    def create_set_any_manual_user_none(self, api_data: dict) -> bool:
        """
        Create Component Set with different packages, asked in interactive mode.
        :param api_data: api data set
        :return: result
        """
        components = self.get_components_any_manual_user_none()

        if components[0] is None:
            return False

        api_data['components'] = components
        return self.web_api.send_create_new_component_set_request(api_data=api_data)

    # -------------------------------------------------------------------------
    # Show
    # -------------------------------------------------------------------------

    def action_show_platforms_projects_or_sets(self, api_data: dict) -> bool:
        """
        Run action: Show platforms, projects or component sets.
        :param api_data: api data set
        :return: result
        """
        if api_data['action'] == Actions.SHOW_PLATFORMS:
            return self.action_show_platforms(api_data=api_data)

        elif api_data['action'] == Actions.SHOW_PROJECTS:
            if api_data['platform'] is None or \
                    api_data['platform'] == '':
                print_line('Empty platform name.')
                return False

            platform_number = self.web_api.get_platform_number_by_name(api_data=api_data)

            if platform_number == -1:
                print_line(f"No such platform: {api_data['platform']}.")
                return False

            return self.action_show_projects(api_data=api_data)

        elif api_data['action'] == Actions.SHOW_SET:
            if api_data['platform'] is None or \
                    api_data['platform'] == '':
                print_line('Empty platform name.')
                return False

            platform_number = self.web_api.get_platform_number_by_name(api_data=api_data)

            if platform_number == -1:
                print_line(f"No such platform: {api_data['platform']}.")
                return False

            if api_data['project'] is None or \
                    api_data['project'] == '':
                print_line('Empty platform name.')
                return False

            project_number = self.web_api.get_project_number_by_name(api_data=api_data)

            if project_number == -1:
                print_line(f"No such project {api_data['project']} in platform {api_data['platform']}.")
                return False

            return self.action_show_set(api_data=api_data)

    @staticmethod
    def action_show_platforms(api_data: dict) -> bool:
        """
        Print existing platforms.
        :param api_data: api data set
        :return: result
        """
        platforms = []

        if 'organization' not in api_data:
            print_line(f'Organization info error.')
            return False

        if 'platforms' not in api_data['organization']:
            print_line(f'Platform info error.')
            return False

        if len(api_data['organization']['platforms']) == 0:
            print_line(f'You have not Platforms.')
            return False

        for platform in api_data['organization']['platforms']:
            platforms.append({'name': platform['name'], 'description': platform['description']})

        print_platforms(platforms=platforms)

        return True

    def action_show_projects(self, api_data: dict) -> bool:
        """
        Print existing project for defined Platform.
        :param api_data: api data set
        :return: result
        """
        projects = []

        if 'organization' not in api_data:
            print_line(f'Organization info error.')
            return False

        if 'platforms' not in api_data['organization']:
            print_line(f'Platform info error.')
            return False

        if len(api_data['organization']['platforms']) == 0:
            print_line(f'You have not Platforms.')
            return False

        platform_number = self.web_api.get_platform_number_by_name(api_data=api_data)

        if platform_number == -1:
            print_line(f"No such platform: {api_data['platform']}.")
            return False

        if len(api_data['organization']['platforms'][platform_number]['projects']) == 0:
            print_line(f'You have not Projects.')
            return False

        for project in api_data['organization']['platforms'][platform_number]['projects']:
            projects.append({'name': project['name'], 'description': 'default project'})

        print_projects(projects=projects)

        return True

    def action_show_set(self, api_data: dict) -> bool:
        """
        Print current Component set for defined Platform/Project.
        :param api_data: api data set
        :return: result
        """
        my_set = self.get_current_set_name(api_data=api_data)

        if my_set[0] is None:
            print_line(f'Get set name error.')
            return False

        print_line(f'Current component set: {my_set[0]}.')

        components = self.get_current_component_set(api_data=api_data)[0]['components']

        if components[0] is None:
            print_line(f'Get component set error.')
            return False

        print_components(components=components[0])

        return True

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------

    def action_delete_platform(self, api_data: dict) -> bool:
        return self.web_api.send_delete_platform_request(api_data=api_data)

    def action_delete_project(self, api_data: dict) -> bool:
        return self.web_api.send_delete_project_request(api_data=api_data)

    # -------------------------------------------------------------------------
    # Archive
    # -------------------------------------------------------------------------

    def action_archive_platform(self, api_data: dict) -> bool:
        return self.web_api.send_archive_platform_request(api_data=api_data)

    def action_archive_project(self, api_data: dict) -> bool:
        return self.web_api.send_archive_project_request(api_data=api_data)

    # -------------------------------------------------------------------------
    # Components
    # -------------------------------------------------------------------------

    def get_components_os_auto_system_none(self, api_data: dict) -> list:
        """
        Get components of OS by calling of shell script and than parse them.
        :param api_data: api data set
        :return: result
        """

        if api_data['os_type'] == OSs.WINDOWS:
            if api_data['os_version'] == '10' or api_data['os_version'] == '8':
                os_packages = self.load_windows_10_packages_from_powershell()[0]

                if os_packages is None:
                    print_line('Failed to load OS components.')
                    return [None]

                report = os_packages.decode('utf-8').replace('\r', '').split('\n')[9:]

                components = self.parse_windows_10_packages(report)

                if components[0] is None:
                    print_line('Failed parse OS components.')
                    return [None]

                return components

            elif api_data['os_version'] == '7':
                print_line('Windows 7 does not support yet.')
                return [None]

            else:
                print_line('Windows type not defined.')
                return [None]

        elif api_data['os_type'] == OSs.CENTOS:
            print_line('Centos not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.DEBIAN:
            print_line('Debian not support yet')
            return [None]

        elif api_data['os_type'] == OSs.FEDORA:
            print_line('Fedora not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.MACOS:
            print_line('MacOS dont support yet.')
            return [None]

        return [None]

    def get_components_os_auto_system_path(self, api_data: dict) -> list:
        """
        Get OS packages from file, defined by path, which were created by calling the shell command.
        :param api_data: api data set
        :return: result
        """
        if api_data['os_type'] == OSs.WINDOWS:
            if api_data['os_version'] == '10' or api_data['os_version'] == '8':

                report = self.load_windows_10_packages_from_powershell_unloaded_file(api_data['file'])[0]

                if report is None:
                    return [None]

                components = self.parse_windows_10_packages(report=report)

                if components[0] is None:
                    return [None]

                return components

            if api_data['os_version'] == '7':
                print_line('Windows 7 does not support yet.')
                return [None]

        elif api_data['os_type'] == OSs.CENTOS:
            print_line('Centos does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.DEBIAN:
            print_line('Debian does not support yet')
            return [None]

        elif api_data['os_type'] == OSs.FEDORA:
            print_line('Fedora does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.MACOS:
            print_line('MacOS does not support yet.')
            return [None]

        return [None]

    def get_components_pip_auto_system_none(self, api_data: dict) -> list:
        """
        Get Python PIP components, collected by pip frozen requirements call.
        :param api_data: api data set
        :return: result
        """
        return self.load_pip_packages_from_frozen_requirement()

    def get_components_pip_auto_system_path(self, api_data: dict) -> list:
        """
        Get Python PIP components from file, defined by path.
        :param api_data: api data set
        :return: result
        """
        packages = self.load_pip_packages_from_path(api_data['file'])

        if packages[0] is not None:
            return self.parse_pip_packages_from_path(packages=packages)

        print_line('Something wrong with packages in file path')
        return [None]

    def get_components_requirements_auto_system_path(self, api_data: dict) -> list:
        """
        Get Python PIP components from requirements.txt file, defined by path.
        :param api_data: api data set
        :return: result
        """
        packages = self.load_pip_packages_from_path(api_data['file'])

        if packages[0] is not None:
            return self.parse_pip_packages_from_path(packages=packages)

        print_line('Something wrong with packages in file path')
        return [None]

    def get_components_npm_auto_system_path(self, api_data: dict) -> list:
        """
        Get NPM packages, collected from file, defined by path.
        :param api_data:
        :return:
        """
        packages = self.load_npm_packages_from_path(api_data['file'])
        if packages[0] is not None:
            return self.parse_npm_packages(raw_npm_components)
        print_line('Something wrong with packages in file path')
        return [None]

    def get_components_package_json_auto_system_path(self, api_data: dict) -> list:
        """
        Get NPM packages from package.json file, defined by path.
        :param api_data: api data set
        :return: result
        """
        packages = self.load_package_json_packages_from_path(api_data['file'])

        if packages[0] is not None:
            return self.parse_package_json_packages_from_path(packages[0])

        print_line('Something wrong with packages in file path')
        return [None]

    def get_components_gem_auto_system_path(self, api_data: dict) -> list:
        """
        Get Ruby gem packages, collected from file, defined by path.
        :param api_data: api data set
        :return: result
        """
        packages = self.load_gem_packages_from_path(api_data['file'])

        if packages[0] is not None:
            return self.parse_gem_packages_from_path(packages[0])

        print_line('Something wrong with packages in file path')
        return [None]

    def get_components_npm_auto_system_none(self, api_data: dict) -> list:
        """
        Get NPM packages, collected from shell command, that is called globally.
        :param api_data: api data set
        :return: result
        """
        if api_data['os_type'] == OSs.WINDOWS:
            packages = self.load_npm_packages(path='', local=False)

            if packages[0] is not None:
                return self.parse_npm_packages(raw_npm_components)

            print_line('Something wrong with packages in file path')
            return [None]

        elif api_data['os_type'] == OSs.CENTOS:
            print_line('Centos does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.DEBIAN:
            print_line('Debian does not support yet')
            return [None]

        elif api_data['os_type'] == OSs.FEDORA:
            print_line('Fedora does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.MACOS:
            print_line('MacOS does not support yet.')
            return [None]

    def get_components_npm_local_auto_system_none(self, api_data: dict) -> list:
        """
        Get NPM packages, collected from shell command, that is called locally from path.
        :param api_data: api data set
        :return: result
        """
        if api_data['os_type'] == OSs.WINDOWS:

            packages = self.load_npm_packages(path=api_data['file'], local=True)

            if packages[0] is not None:
                return self.parse_npm_packages(raw_npm_components)

            print_line('Something wrong with packages in file path')
            return [None]

        elif api_data['os_type'] == OSs.CENTOS:
            print_line('Centos does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.DEBIAN:
            print_line('Debian does not support yet')
            return [None]

        elif api_data['os_type'] == OSs.FEDORA:
            print_line('Fedora does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.MACOS:
            print_line('MacOS does not support yet.')
            return [None]

    def get_components_npm_lock_auto_system_path(self, api_data: dict) -> list:
        """
        Get NPM packages from lock file, defined by path.
        :param api_data: api data set
        :return: result
        """
        if api_data['os_type'] == OSs.WINDOWS:

            packages = self.load_npm_lock_packages_from_path(filename=api_data['file'])

            if packages[0] is not None:
                return self.parse_npm_lock_packages(packages[0])

            print_line('Something wrong with packages in file path')
            return [None]

        elif api_data['os_type'] == OSs.CENTOS:
            print_line('Centos does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.DEBIAN:
            print_line('Debian does not support yet')
            return [None]

        elif api_data['os_type'] == OSs.FEDORA:
            print_line('Fedora does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.MACOS:
            print_line('MacOS does not support yet.')
            return [None]

    def get_components_gem_auto_system_none(self, api_data: dict) -> list:
        """
        Get Ruby gem packages, collected from shell command, that is called globally.
        :param api_data: api data set
        :return: result
        """
        if api_data['os_type'] == OSs.WINDOWS:
            packages = self.load_gem_packages_system(local=False, api_data=api_data)
            if packages[0] is not None:
                return self.parse_gem_packages_system(packages=packages[0])
            print_line('Something wrong with packages in file path')
            return [None]

        elif api_data['os_type'] == OSs.CENTOS:
            print_line('Centos does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.DEBIAN:
            print_line('Debian does not support yet')
            return [None]

        elif api_data['os_type'] == OSs.FEDORA:
            print_line('Fedora does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.MACOS:
            print_line('MacOS does not support yet.')
            return [None]

    def get_components_gemfile_auto_system_path(self, api_data: dict) -> list:
        """
        Get Ruby gem packages, collected from Gemfile, defined by path.
        :param api_data:
        :return:
        """
        packages = self.load_gemfile_packages_from_path(filename=api_data['file'])

        if packages[0] is None:
            print(f'Gemfile packages loading error.')
            return [None]

        components = self.parse_gemfile_packages(packages=packages)

        if components[0] is None:
            print_line(f'Failed parse Gemfile packages.')
            return [None]

        return components

    def get_components_gemfile_lock_auto_system_path(self, api_data: dict) -> list:
        """
        Get Ruby gem packages, collected from Gemfile.lock, defined by path.
        :param api_data:
        :return:
        """
        packages = self.load_gemfile_lock_packages_from_path(filename=api_data['file'])

        if packages[0] is None:
            print(f'Gemfile packages loading error.')
            return [None]

        components = self.parse_gemfile_lock_packages(packages=packages)

        if components[0] is None:
            print_line(f'Failed parse Gemfile packages.')
            return [None]

        return components

    def get_components_any_auto_user_path(self, api_data: dict) -> list:
        """
        Get any components from file, defined by path.
        :param api_data: api data set
        :return: result
        """
        filename = api_data['file']
        if os.path.isfile(filename):
            enc = self.define_file_encoding(filename=filename)

            if enc == 'undefined':
                print_line('Undefined file encoding. Please, use utf-8 or utf-16.')
                return [None]

            components = []

            with open(filename, 'r', encoding=enc) as pf:
                packages = pf.read().split('\n')
                for package in packages:
                    if len(package) != 0:
                        if '=' in package:
                            splitted_package = package.split('=')
                            if len(splitted_package) == 2:
                                components.append({'name': splitted_package[0], 'version': splitted_package[1]})
                return components

        print_line(f'File {filename} not found.')
        return [None]

    @staticmethod
    def get_components_any_manual_user_none() -> list:
        """
        Get packages from console.
        :return:
        """
        components = []

        if ask('Continue (y/n)? ') == 'n':
            return [None]

        while True:
            name = ask('Enter component name: ')
            version = ask('Enter component version: ')
            components.append({'name': name, 'version': version})
            if ask('Continue (y/n)? ') == 'n':
                break

        return components

    # -------------------------------------------------------------------------
    # Loaders
    # -------------------------------------------------------------------------

    @staticmethod
    def load_windows_10_packages_from_powershell() -> list:
        """
        Load OS packages for Windows platform by powershell command.
        :return: result
        """
        cmd = "Get-AppxPackage -AllUsers | Select Name, PackageFullName"
        try:
            proc = subprocess.Popen(
                ["powershell", cmd],
                stdout=subprocess.PIPE)

            output, error = proc.communicate()

            if error:
                print_line(f'Powershell command throw {proc.returncode} code and {error.strip()} error message.')
                return [None]

            if output:
                return [output]

        except OSError as os_error:
            print_line(f'Powershell command throw errno: {os_error.errno}, '
                       f'strerror: {os_error.strerror} and '
                       f'filename: {os_error.filename}.')
            return [None]

        except Exception as common_exception:
            print_line(f'Powershell command throw an exception: {common_exception}.')
            return [None]

    def load_windows_10_packages_from_powershell_unloaded_file(self, filename: str) -> list:
        """
        Get OS packages for Windows platform from unloaded file, that was created by shell command manually.
        :param filename: path to file
        :return: result
        """
        if os.path.exists(filename):

            enc = self.define_file_encoding(filename=filename)

            if enc == 'undefined':
                print_line('Undefined file encoding. Please, use utf-8 or utf-16.')
                return [None]

            try:
                with open(filename, 'r', encoding=enc) as cf:
                    os_packages = cf.read()
                    if os_packages is None:
                        print_line(f'Cant read file: {filename}.')
                        return [None]
                    report = os_packages.replace('\r', '').split('\n')[9:]
                    return [report]
            except:
                print_line(f'File read exception.')
                return [None]

        print_line(f'File {filename} does not exists.')
        return [None]

    @staticmethod
    def load_pip_packages_from_frozen_requirement():
        """
        Load Python PI packages with pip.FrozenRequirement method.
        :return: result
        """
        components = []
        installations = {}
        try:
            for dist in get_installed_distributions(local_only=False, skip=[]):
                req = pip.FrozenRequirement.from_dist(dist, [])
                installations[req.name] = dist.version

            for key in installations:
                components.append({'name': key, 'version': installations[key]})

            return components

        except Exception as e:
            print_line(f'Get an exception: {e}.')
            return [None]

    def load_pip_packages_from_path(self, filename: str) -> list:
        """
        Load Python PIP packages from file.
        :param filename: path to file
        :return: result
        """
        if os.path.exists(filename):

            enc = self.define_file_encoding(filename)

            if enc == 'undefined':
                print_line(f'Undefined file {filename} encoding.')
                return [None]

            try:
                with open(filename, encoding=enc) as cf:
                    rfp = cf.read()
                    rfps = rfp.replace(' ', '').split('\n')
                    return rfps

            except:
                print_line(f'Get an exception, when read file {filename}')
                return [None]

        print_line(f'File {filename} does not exists.')
        return [None]

    def load_npm_packages_from_path(self, filename: str) -> list:
        """
        Load NPM packages from file, defined by path.
        :param filename: path to file
        :return: result
        """
        if os.path.exists(filename):

            enc = self.define_file_encoding(filename)

            if enc == 'undefined':
                print_line(f'Undefined file {filename} encoding.')
                return [None]

            try:
                with open(filename, 'r', encoding=enc) as pf:
                    data = json.load(pf)
                    walkdict(data)
                    return [True]

            except Exception as e:
                print_line(f'File read exception: {e}')
                return [None]

        print_line('File does not exist.')
        return [None]

    def load_npm_packages(self, path: str, local: bool) -> list:
        """
        Load NPM packages from shell command through temporary file.
        :param path: path to directory, if method call locally
        :param local: run local or global
        :return: result
        """
        tmp_file_name = 'tmp_npm_list_json.txt'
        file_path = os.path.expanduser('~')
        full_path = os.path.join(file_path, tmp_file_name)

        try:
            with open(full_path, mode='w', encoding='utf-8') as temp:
                temp.write('')
                temp.seek(0)

        except Exception as e:
            print_line(f'Cant create temp file, get an exception: {e}.')
            return [None]

        cmd = "npm list --json > {0}".format(full_path)

        if os.name == 'nt':
            if local:
                os.chdir(path)
            else:
                os.chdir("c:\\")

            try:
                proc = subprocess.Popen(
                    ["powershell", cmd],
                    stdout=subprocess.PIPE)
                output, error = proc.communicate()
                proc.kill()

                if error:
                    print_line(f'Powershell command throw {proc.returncode} code:')
                    print_line(f'and {error.strip()} error message.')
                    return [None]

                try:
                    enc = self.define_file_encoding(full_path)

                    if enc == 'undefined':
                        print_line('An error with encoding occured in temp file.')
                        return [None]

                    with open(full_path, encoding=enc) as cf:
                        data = json.load(cf)
                        walkdict(data)
                        return [True]

                except Exception as e:
                    print_line(f'File read exception: {e}')
                    return [None]

                finally:
                    if os.path.isfile(full_path):
                        os.remove(full_path)

            except OSError as os_error:
                print_line(f'Powershell command throw errno: {os_error.errno}, strerror: {os_error.strerror}')
                print_line(f'and filename: {os_error.filename}.')

                if os.path.isfile(full_path):
                    os.remove(full_path)

                return [None]

            finally:
                if os.path.isfile(full_path):
                    os.remove(full_path)

        if os.path.isfile(full_path):
            os.remove(full_path)

        return [None]

    def load_package_json_packages_from_path(self, filename: str) -> list:
        """
        Load NPM packages from package.json file, defined by path.
        :param filename: path to file
        :return: result
        """
        if os.path.exists(filename):

            enc = self.define_file_encoding(filename)

            if enc == 'undefined':
                print_line(f'Undefined file {filename} encoding.')
                return [None]

            try:
                with open(filename, 'r', encoding=enc) as pf:
                    packages = json.load(pf)
                    return [packages]

            except Exception as e:
                print_line(f'File {filename} read exception: {e}')
                return [None]

        print_line('File does not exist.')
        return [None]

    def load_npm_lock_packages_from_path(self, filename: str) -> list:
        """
        Load NPM packages from lock file, defined by path.
        :param filename: path to file
        :return: result
        """
        if os.path.exists(filename):

            enc = self.define_file_encoding(filename)

            if enc == 'undefined':
                print_line(f'Undefined file {filename} encoding.')
                return [None]

            try:
                with open(filename, 'r', encoding=enc) as pf:
                    try:
                        packages = json.load(pf)
                        return [packages]

                    except json.JSONDecodeError as json_decode_error:
                        print_line(f'An exception occured with json decoder: {json_decode_error}.')
                        return [None]

            except Exception as e:
                print_line(f'File {filename} read exception: {e}')
                return [None]

        print_line('File does not exist.')
        return [None]

    def load_gem_packages_from_path(self, filename: str) -> list:
        """
        Load Ruby gem packages from file, defined by path.
        :param filename: path to file
        :return: result
        """
        if os.path.exists(filename):

            enc = self.define_file_encoding(filename)

            if enc == 'undefined':
                print_line(f'Undefined file {filename} encoding.')
                return [None]

            try:
                with open(filename, 'r', encoding=enc) as pf:
                    cont = pf.read().replace('default: ', '').replace(' ', '').replace(')', '')
                    cont = cont.split('\n')
                    return [cont]

            except Exception as e:
                print_line(f'File {filename} read exception: {e}')
                return [None]

        print_line('File does not exist.')
        return [None]

    def load_gem_packages_system(self, local: bool, api_data: dict) -> list:
        """
        Load Ruby gem packages from global or local call of shell commend.
        :param local: local or global
        :param api_data: api data set
        :return: result
        """
        if api_data['os_type'] == OSs.WINDOWS:

            if local:
                os.chdir(api_data['file'])
            else:
                os.chdir('c:\\')

            cmd = "gem list"

            try:
                proc = subprocess.Popen(
                    ["powershell", cmd],
                    stdout=subprocess.PIPE)
                output, error = proc.communicate()
                output = output.decode('utf-8').replace('\r', '').split('\n')

                if error:
                    print_line(f'Powershell command throw {proc.returncode} code and {error.strip()} error message.')
                    return [None]

                if output:
                    return [output]

            except OSError as os_error:
                print_line(f'Powershell command throw errno: {os_error.errno}, '
                           f'strerror: {os_error.strerror} and '
                           f'filename: {os_error.filename}.')
                return [None]

            except Exception as common_exception:
                print_line(f'Powershell command throw an exception: {common_exception}.')
                return [None]

        elif api_data['os_type'] == OSs.CENTOS:
            print_line('Centos does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.DEBIAN:
            print_line('Debian does not support yet')
            return [None]

        elif api_data['os_type'] == OSs.FEDORA:
            print_line('Fedora does not support yet.')
            return [None]

        elif api_data['os_type'] == OSs.MACOS:
            print_line('MacOS does not support yet.')
            return [None]

    def load_gemfile_packages_from_path(self, filename: str) -> list:
        """
        Load packages from Gemfile. defined by path.
        :param filename: filename
        :return: result
        """
        if os.path.isfile(filename):
            enc = self.define_file_encoding(filename=filename)

            if enc == 'undefined':
                print_line(f'Undefined file {filename} encoding.')
                return [None]

            try:
                with open(filename, 'r', encoding=enc) as pf:
                    cont = pf.read()
                    packages = cont.split('\n')
                    return packages

            except Exception as e:
                print_line(f'File {filename} read exception: {e}')
                return [None]

        print_line('File does not exist.')
        return [None]

    def load_gemfile_lock_packages_from_path(self, filename: str) -> list:
        if os.path.isfile(filename):
            enc = self.define_file_encoding(filename=filename)

            if enc == 'undefined':
                print_line(f'Undefined file {filename} encoding.')
                return [None]

            try:
                with open(filename, 'r', encoding=enc) as pf:
                    cont = pf.read()
                    packages = cont.split('\n')
                    return packages

            except Exception as e:
                print_line(f'File {filename} read exception: {e}')
                return [None]

        print_line('File does not exist.')
        return [None]

    # -------------------------------------------------------------------------
    # Parsers
    # -------------------------------------------------------------------------

    @staticmethod
    def parse_windows_10_packages(report: list) -> list:
        """
        Parse Windows 10 packages.
        :param report: raw report
        :return: result
        """
        packages = []
        try:

            for report_element in report:
                if len(report_element) > 0:
                    splitted_report_element = report_element.split()
                    component_and_version = splitted_report_element[len(splitted_report_element) - 1]
                    element_array = component_and_version.split('_')

                    if len(element_array) >= 2:
                        common_component_name = element_array[0]
                        common_component_version = element_array[1]
                        component = {'name': common_component_name.split('.')}

                        if len(common_component_name.split('.')) >= 3 and component['name'][1] == 'NET':
                            component['name'] = 'net_framework'

                        else:
                            component['name'] = common_component_name.split('.')
                            component['name'] = component['name'][len(component['name']) - 1]

                        component['version'] = common_component_version.split('.')
                        component['version'] = component['version'][0] + '.' + component['version'][1]
                        packages.append(component)
            return packages

        except:
            print_line('Exception occured. Try run app with Administrator rights.')
            return [None]

    @staticmethod
    def parse_pip_packages_from_path(packages: list) -> list:
        """
        Parse Python PIP packages report.
        :param packages: raw packages
        :return: result
        """
        components = []
        for ref in packages:
            if len(ref) > 0:
                if '==' in ref:
                    refs = ref.split('==')
                    components.append({'name': refs[0], 'version': refs[1]})
                elif '>' in ref:
                    refs = ref.split('>')
                    components.append({'name': refs[0], 'version': refs[1]})
                elif '<' in ref:
                    refs = ref.split('<')
                    components.append({'name': refs[0], 'version': refs[1]})
                elif '>=' in ref:
                    refs = ref.split('>=')
                    components.append({'name': refs[0], 'version': refs[1]})
                elif '<=' in ref:
                    refs = ref.split('<-')
                    components.append({'name': refs[0], 'version': refs[1]})
                else:
                    try:
                        mm = importlib.import_module(ref)
                        components.append({'name': ref, 'version': mm.__version__})
                    except ImportError as import_exception:
                        print_line(f'Get an exception {import_exception} when define component version.')
                        components.append({'name': ref, 'version': '*'})
                        continue
        return components

    @staticmethod
    def parse_npm_packages(comp: list) -> list:
        """
        Parse NPM raw packages.
        :param comp: raw packages.
        :return: result
        """
        components2 = []
        for c in comp:
            if c["name"] == "from":
                if '@' in c['version']:
                    p = c["version"].split('@')
                    p[1] = p[1].replace('~', '')
                    components2.append({"name": p[0], "version": p[1]})

                else:
                    name = c["version"]
                    cmd = "npm view {0} version".format(name)

                    if os.name == 'nt':
                        try:
                            proc = subprocess.Popen(
                                ["powershell", cmd],
                                stdout=subprocess.PIPE)
                            version, error = proc.communicate()
                            version = version.decode("utf-8").replace('\n', '')

                            if error:
                                print_line(f'Powershell command throw {proc.returncode} code '
                                           f'and {error.strip()} error message.')

                        except OSError as os_error:
                            print_line(f'Powershell command throw errno: {os_error.errno}, strerror: {os_error.strerror}')
                            print_line(f'and filename: {os_error.filename}.')
                            continue

                        except:
                            continue

                    else:
                        # TODO: COMPLETE FOR ANOTHER PLATFORMS
                        version = '*'
                    components2.append({"name": name, "version": version})
        return components2

    @staticmethod
    def parse_npm_lock_packages(packages: dict) -> list:
        """
        Parse NPM lock packages.
        :param packages: raw packages.
        :return: result
        """
        def already_in_components(components: list, key: str) -> bool:
            """
            Filter if coponent already in list.
            :param components: component list
            :param key: component key
            :return: filtered list
            """
            for component in components:
                if component['name'] == key:
                    return True
            return False

        dependencies = packages['dependencies']
        keys = dependencies.keys()
        components = []
        for key in keys:
            if not already_in_components(components=components, key=key):
                components.append({'name': key, "version": dependencies[key]['version']})
            if 'requires' in dependencies[key].keys():
                requires = dependencies[key]['requires']
                for rkey in requires.keys():
                    if not already_in_components(components=components, key=rkey):
                        components.append({'name': rkey, 'version': requires[rkey]})
            if 'dependencies' in dependencies[key].keys():
                deps = dependencies[key]['dependencies']
                for dkey in deps.keys():
                    if not already_in_components(components=components, key=dkey):
                        components.append({'name': dkey, 'version': deps[dkey]})
        return components

    @staticmethod
    def parse_package_json_packages_from_path(packages: dict) -> list:
        """
        Parse package.json file.
        :param packages: raw packages
        :return: result
        """
        components = []
        dependencies = packages['dependencies']
        dev_dependencies = packages['devDependencies']

        if dev_dependencies != {}:
            for key in dev_dependencies.keys():
                components.append({'name': key, 'version': str(dev_dependencies[key]).replace('^', '')})

        if dependencies != {}:
            for key in dependencies.keys():
                components.append({'name': key, 'version': str(dependencies[key]).replace('^', '')})

        return components

    def parse_gem_packages_system(self, packages: list) -> list:
        """
        Parse Ruby gem packages.
        :param packages: raw packages.
        :return: result
        """
        return self.parse_gem_packages_from_path(packages=packages)

    @staticmethod
    def parse_gem_packages_from_path(packages: list) -> list:
        """
        Parse Ruby gem packages from path.
        :param packages: raw packages
        :return: result
        """
        components = []
        for c in packages:
            if len(c) > 0:
                c = c.replace(' ', '').replace(')', '').replace('default:', '')
                cs = c.split('(')
                try:
                    if len(cs) == 2:
                        components.append({'name': cs[0], 'version': cs[1]})
                except:
                    continue
        return components

    def parse_gemfile_packages(self, packages: list) -> list:
        """
        Parse packages from Gemfile.
        :param packages: list of packages
        :return: result
        """
        content_splitted_by_strings = packages

        content_without_empty_strings = []
        for string in content_splitted_by_strings:
            if len(string) > 0:
                content_without_empty_strings.append(string)

        content_without_comments = []
        for string in content_without_empty_strings:
            if not string.lstrip().startswith('#'):
                if '#' in string:
                    content_without_comments.append(string.lstrip().split('#')[0])
                else:
                    content_without_comments.append(string.lstrip())

        cleared_content = []
        for string in content_without_comments:
            if string.startswith('gem '):
                cleared_content.append(string.split('gem ')[1])
            else:
                if string.startswith('gem('):
                    cleared_content.append(string.split('gem(')[1])


        prepared_data_for_getting_packages_names_and_versions = []
        for string in cleared_content:
            intermediate_result = re.findall(
                r'''('.*',\s*'.*\d.*?'|".*",\s*".*\d.*?"|".*",\s*'.*\d.*?'|'.*',\s*".*\d.*?")''', string)

            if intermediate_result:
                prepared_data_for_getting_packages_names_and_versions.append(intermediate_result[0])

        packages = []

        for prepared_string in prepared_data_for_getting_packages_names_and_versions:
            package = {
                'name': '*',
                'version': '*'
            }

            splitted_string_by_comma = prepared_string.split(',')

            package_name = splitted_string_by_comma[0][1:-1]
            package['name'] = package_name

            if len(splitted_string_by_comma) == 2:
                package['version'] = re.findall(r'(\d.*)', splitted_string_by_comma[1])[0][0:-1]
                packages.append(package)

            elif len(splitted_string_by_comma) == 3:
                min_package_version = re.findall(r'(\d.*)', splitted_string_by_comma[1])[0][0:-1]
                package['version'] = min_package_version
                packages.append(package)

                max_package_version = re.findall(r'(\d.*)', splitted_string_by_comma[2])[0][0:-1]
                package['version'] = max_package_version
                packages.append(package)

        # TODO: DELETE DUBLICATES

        # TODO: WHAT ABOUT PACKAGES WITHOUT VERSIONS?

        unique_packages = []
        for i in range(len(packages)):
            package = packages.pop()

            if package not in unique_packages:
                unique_packages.append(package)

        return unique_packages

    def parse_gemfile_lock_packages(self, packages: list) -> list:
        splitted_content_by_strings = packages

        ignore_strings_startswith = (
            'GIT', 'remote', 'revision',
            'specs', 'PATH', 'GEM',
            'PLATFORMS', 'DEPENDENCIES', 'BUNDLED')

        cleared_content = []
        for string in splitted_content_by_strings:
            if not string.lstrip().startswith(ignore_strings_startswith):
                cleared_content.append(string.lstrip())

        prepared_data_for_getting_packages_names_and_versions = []
        for string in cleared_content:
            intermediate_result = re.findall(r'(.*\s*\(.*\))', string)

            if intermediate_result:
                prepared_data_for_getting_packages_names_and_versions.append(intermediate_result)

        packages = []
        for data in prepared_data_for_getting_packages_names_and_versions:
            package = {
                'name': '*',
                'version': '*'
            }

            splitted_data = data[0].split(' ')

            package_name = splitted_data[0]
            package['name'] = package_name

            if len(splitted_data) == 2:
                package['version'] = splitted_data[1][1:-1]
                packages.append(package)
            elif len(splitted_data) == 3:
                package['version'] = splitted_data[2][0:-1]
                packages.append(package)
            elif len(splitted_data) == 5:
                min_version = splitted_data[2][0:-1]
                package['version'] = min_version
                packages.append(package)

                max_version = splitted_data[4][0:-1]
                package['version'] = max_version
                packages.append(package)

        unique_packages = []
        for i in range(len(packages)):
            package = packages.pop()

            if package not in unique_packages:
                unique_packages.append(package)

        return unique_packages

    # -------------------------------------------------------------------------
    # Addition methods
    # -------------------------------------------------------------------------

    @staticmethod
    def define_file_encoding(filename: str) -> str:
        """
        Define encoding of file.
        :param filename:
        :return:
        """

        encodings = ['utf-16', 'utf-8', 'windows-1250', 'windows-1252', 'iso-8859-7', 'macgreek']

        for e in encodings:
            try:
                import codecs
                fh = codecs.open(filename, 'r', encoding=e)
                fh.readlines()
                fh.seek(0)
                return e

            except:
                continue

        return 'undefined'

    @staticmethod
    def get_my_platforms(api_data: dict) -> list:
        """
        Get platforms names as list.
        :param api_data: api data set
        :return: result
        """

        if api_data['organization'] is None:
            return []

        if api_data['organization']['platforms'] is None:
            return []

        platforms = []
        for platform in api_data['organization']['platforms']:
            platforms.append(platform['name'])

        return platforms

    def get_my_projects(self, api_data: dict) -> list:
        """
        Get projects names as list.
        :param api_data: api data set
        :return: result
        """

        if api_data['organization'] is None:
            return []

        if api_data['organization']['platforms'] is None:
            return []

        platform_number = self.web_api.get_platform_number_by_name(api_data=api_data)

        if platform_number == -1:
            return []

        projects = []
        for project in api_data['organization']['platforms'][platform_number]['projects']:
            projects.append(project['name'])

        return projects

    def get_current_set_name(self, api_data: dict) -> list:
        """
        Get current component set name.
        :param api_data: api data set
        :return: result
        """

        if api_data['organization'] is None:
            return [None]

        if api_data['organization']['platforms'] is None:
            return [None]

        platform_number = self.web_api.get_platform_number_by_name(api_data=api_data)

        if platform_number == -1:
            return [None]

        project_number = self.web_api.get_project_number_by_name(api_data=api_data)

        if project_number == -1:
            return ['0.0.1']

        return [api_data['organization']['platforms'][platform_number]['projects'][project_number]['current_component_set']['name']]

    def get_current_component_set(self, api_data: dict) -> list:
        """
        Get current component set for platform/project.
        :param api_data: api data set
        :return: result
        """

        if api_data['organization'] is None:
            return [None]

        if api_data['organization']['platforms'] is None:
            return [None]

        platform_number = self.web_api.get_platform_number_by_name(api_data=api_data)

        if platform_number == -1:
            return [None]

        project_number = self.web_api.get_project_number_by_name(api_data=api_data)

        if project_number == -1:
            return [None]

        return [api_data['organization']['platforms'][platform_number]['projects'][project_number]['current_component_set']]

    # -------------------------------------------------------------------------
    # Checkers
    # -------------------------------------------------------------------------

    @staticmethod
    def check_action_type_match(api_data: dict) -> bool:
        """
        Check if action type, pointed in arguments match with template.
        :param api_data: api data set
        :return: result
        """

        if 'action' not in api_data:
            return False

        if api_data['action'] != Actions.SAVE_CONFIG and \
                api_data['action'] != Actions.CREATE_PLATFORM and \
                api_data['action'] != Actions.CREATE_PROJECT and \
                api_data['action'] != Actions.CREATE_SET and \
                api_data['action'] != Actions.SHOW_PLATFORMS and \
                api_data['action'] != Actions.SHOW_PROJECTS and \
                api_data['action'] != Actions.SHOW_SET:
            return False

        return True

    # -------------------------------------------------------------------------
    # Config actions
    # -------------------------------------------------------------------------

    @staticmethod
    def save_config_to_file(api_data: dict) -> bool:
        """
        Save data into config fle in yaml format.
        :param api_data: api data set
        :return: result
        """

        file_name = '.surepatch.yaml'
        file_path = os.path.expanduser('~')
        full_path = os.path.join(file_path, file_name)

        config = dict(
            team=api_data['team'],
            user=api_data['user'],
            password=api_data['password'],
            auth_token=api_data['auth_token']
        )

        with open(full_path, 'w') as yaml_config_file:
            try:
                yaml.dump(config, yaml_config_file)
                return True

            except yaml.YAMLError as yaml_exception:
                print_line(f'Config file save in yaml format exception: {yaml_exception}')
                return False

            finally:
                yaml_config_file.close()

    def load_config_from_file(self, api_data: dict) -> bool:
        """
        Load data from config file in yaml format.
        :param api_data: api data set
        :return: result
        """

        file_name = '.surepatch.yaml'
        file_path = os.path.expanduser('~')
        full_path = os.path.join(file_path, file_name)

        if not os.path.isfile(full_path):
            print_line(f'Config file does not exist: ~/{file_name}')
            print_line(f'Create config file first with parameter --action=save_config.')
            return False

        enc = self.define_file_encoding(full_path)

        if enc == 'undefined':
            print_line('Undefined file encoding. Please, use utf-8 or utf-16.')
            return False

        with open(full_path, 'r', encoding=enc) as yaml_config_file:
            try:
                config = yaml.load(yaml_config_file)

                if 'team' not in config or config['team'] is None or config['team'] == '':
                    return False

                api_data['team'] = config['team']

                if 'user' not in config or config['user'] is None or config['user'] == '':
                    return False

                api_data['user'] = config['user']

                if 'password' not in config or config['password'] is None or config['password'] == '':
                    return False

                api_data['password'] = config['password']

                if 'auth_token' not in config:
                    config['auth-token'] = ''

                api_data['auth_token'] = config['auth_token']

                return True

            except yaml.YAMLError as yaml_exception:
                print_line(f'Get an exception while read config file: {yaml_exception}.')
                return False

            finally:
                yaml_config_file.close()


class Actions(object):
    """Class for constant actions names.
    """

    SAVE_CONFIG = 'save_config'
    CREATE_PLATFORM = 'create_platform'
    CREATE_PROJECT = 'create_project'
    CREATE_SET = 'create_set'
    SHOW_PLATFORMS = 'show_platforms'
    SHOW_PROJECTS = 'show_projects'
    SHOW_SET = 'show_set'
    DELETE_PLATFORM = 'delete_platform'
    DELETE_PROJECT = 'delete_project'
    ARCHIVE_PLATFORM = 'archive_platform'
    ARCHIVE_PROJECT = 'archive_project'


class Targets(object):
    """Class for constant targets names.
    """

    OS = 'os'
    PIP = 'pip'
    REQ = 'req'
    REQUIREMENTS = 'requirements'
    NPM = 'npm'
    NPM_LOCAL = 'npm_local'
    PACKAGE_JSON = 'package_json'
    PACKAGE_LOCK_JSON = 'package_lock_json'
    GEM = 'gem'
    GEMFILE = 'gemfile'
    GEMFILE_LOCK = 'gemfile_lock'


class Methods(object):
    """Class for constant methods names.
    """

    AUTO = 'auto'
    MANUAL = 'manual'


class Formats(object):
    """Class for constant format names.
    """

    SYSTEM = 'system'
    USER = 'user'


class OSs(object):
    """Class for OS constant names.
    """

    WINDOWS = 'windows'
    UBUNTU = 'ubuntu'
    DEBIAN = 'debian'
    CENTOS = 'centos'
    FEDORA = 'fedora'
    OPENSUSE = 'opensuse'
    MACOS = 'macos'
