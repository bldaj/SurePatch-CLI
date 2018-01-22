# -*- coding: utf-8 -*-

import os
import sys
import yaml
import json
import importlib
import subprocess

from core.interface import print_line
from core.webapi import WebAPI

try:
    import pip
    from pip.utils import get_installed_distributions
except ImportError as import_exception:
    print_line(f"Can't import pip get_installed_distributions. Get an exception: {import_exception}.")
    sys.exit(0)


raw_npm_components = []

def walkdict(data):
    for k, v in data.items():
        if isinstance(v, dict):
            walkdict(v)
        else:
            raw_npm_components.append({"name": k, "version": v})

class API(object):

    def __init__(self):
        self.web_api = WebAPI()

    def run_action(self, api_data: dict) -> bool:

        if not self.check_action_type(api_data=api_data):
            return False

        if api_data['action'] == Actions.SAVE_CONFIG:
            return self.save_config(api_data=api_data)

        if not self.load_config(api_data=api_data):
            return False

        if not self.action_login(api_data=api_data):
            return False

        if not self.get_organization_parameters(api_data=api_data):
            return False

        if api_data['action'] == Actions.CREATE_PLATFORM:
            return self.action_create_platform(api_data=api_data)

        if api_data['action'] == Actions.CREATE_PROJECT:
            return self.action_create_project(api_data=api_data)

        if api_data['action'] == Actions.CREATE_SET:
            return self.action_create_set(api_data=api_data)

    @staticmethod
    def check_action_type(api_data: dict) -> bool:
        if 'action' not in api_data:
            return False
        if api_data['action'] != Actions.SAVE_CONFIG and \
                api_data['action'] != Actions.CREATE_PLATFORM and \
                api_data['action'] != Actions.CREATE_PROJECT and \
                api_data['action'] != Actions.CREATE_SET:
            return False
        return True

    @staticmethod
    def save_config(api_data: dict) -> bool:
        file_name = '.surepatch.yaml'
        file_path = os.path.expanduser('~')
        full_path = os.path.join(file_path, file_name)
        config = dict(
            team=api_data['team'],
            user=api_data['user'],
            password=api_data['password']
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

    @staticmethod
    def load_config(api_data: dict) -> bool:
        file_name = '.surepatch.yaml'
        file_path = os.path.expanduser('~')
        full_path = os.path.join(file_path, file_name)
        if not os.path.isfile(full_path):
            print_line(f'Config file does not exist: ~/{file_name}')
            print_line('Create config file first with parameter --action=save_config.')
            return False
        with open(full_path, 'r') as yaml_config_file:
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
                return True
            except yaml.YAMLError as yaml_exception:
                print_line(f'Config file save in yaml format exception: {yaml_exception}')
                return False
            finally:
                yaml_config_file.close()

    # LOGIN

    def action_login(self, api_data: dict) -> bool:
        return self.web_api.send_login_request(api_data=api_data)

    # GET ORGANIZATION PARAMETERS

    def get_organization_parameters(self, api_data: dict) -> bool:
        return self.web_api.send_get_organization_parameters_request(api_data=api_data)

    # CREATE PLATFORM

    def action_create_platform(self, api_data: dict) -> bool:
        if api_data['platform'] is None or api_data['platform'] == '':
            print_line('Empty platform name, please use --platform flag.')
            return False
        if api_data['description'] is None or api_data['description'] == '':
            print_line('Empty platform description. Change description to "default platform".')
            api_data['description'] = "default platform"
        return self.web_api.send_create_new_platform_request(api_data=api_data)

    # CREATE PROJECT

    def action_create_project(self, api_data: dict) -> bool:
        # Check parameters

        if api_data['platform'] is None or api_data['platform'] == '':
            print_line('Empty platform name.')
            return False
        if api_data['project'] is None or api_data['project'] == '':
            print_line('Empty project name.')
            return False
        platforms = self.get_platforms(api_data=api_data)
        if api_data['platform'] not in platforms:
            print_line(f"Platform {api_data['platform']} does not exists.")
            return False
        projects = self.get_projects(api_data=api_data)
        if api_data['project'] in projects:
            print_line(f"Project {api_data['project']} already exists.")
            return False

        # Select variant

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

        if api_data['target'] == Targets.REQUIREMENTS and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_requirements_auto_system_path(api_data=api_data)

        # Create new project with NPM packages {from shell request}
        if api_data['target'] == Targets.NPM and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is None:
            return self.create_project_npm_auto_system_none(api_data=api_data)

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

        # Create new project with GEMLIST file {from path}
        if api_data['target'] == Targets.GEMLIST and \
                api_data['method'] == Methods.AUTO and \
                api_data['format'] == Formats.SYSTEM and \
                api_data['file'] is not None:
            return self.create_project_gemlist_auto_system_path(api_data=api_data)

    def create_project_os_auto_system_none(self, api_data: dict) -> bool:
        components = []
        if api_data['os'] == 'windows':
            os_packages = self.get_windows_packages(api_data=api_data)
            if os_packages is None:
                components = []
            else:
                report = os_packages.decode('utf-8').replace('\r', '').split('\n')[9:]
                components = self.parse_windows_packages(report)
                if components is None:
                    components = []
        api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_os_auto_system_path(self, api_data: dict) -> bool:
        components = self.load_and_parse_os_components_from_file(os_type=api_data['os'], filename=api_data['file'])
        if not components:
            api_data['components'] = []
        else:
            api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_pip_auto_system_none(self, api_data: dict) -> bool:
        components = list()
        installations = {}
        try:
            for dist in get_installed_distributions(local_only=False, skip=[]):
                req = pip.FrozenRequirement.from_dist(dist, [])
                installations[req.name] = dist.version
            for key in installations:
                components.append({'name': key, 'version': installations[key]})
            api_data['components'] = components
            return self.web_api.send_create_new_project_request(api_data=api_data)
        except Exception as e:
            print_line(f'Get an exception: {e}.')
            return False

    def create_project_pip_auto_system_path(self, api_data: dict) -> bool:
        components = self.load_and_parse_pip_components_from_path(filename=api_data['file'])
        if not components:
            api_data['components'] = []
        else:
            api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_requirements_auto_system_path(self, api_data: dict) -> bool:
        components = self.load_and_parse_pip_components_from_path(filename=api_data['file'])
        if not components:
            api_data['components'] = []
        else:
            api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_npm_auto_system_none(self, api_data: dict) -> bool:
        if api_data['os'] == 'windows':
            print_line('For Windows system this feature does not work now. '
                       'Please use npm list --json > file_path command '
                       'and use --file=path mode.')
            return False
        else:
            print_line('Dont check yet')
            return False

    def create_project_npm_auto_system_path(self, api_data: dict) -> bool:
        components = self.load_and_parse_npm_components_from_file(filename=api_data['file'])
        if not components:
            api_data['components'] = []
        else:
            api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_package_json_auto_system_path(self, api_data: dict) -> bool:
        components = self.load_and_parse_package_json_components_from_path(filename=api_data['file'])
        if not components:
            api_data['components'] = []
        else:
            api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_gem_auto_system_none(self, api_data: dict) -> bool:
        print_line('Dont check yet')
        return False

    def create_project_gem_auto_system_path(self, api_data: dict) -> bool:
        components = self.load_and_parse_gem_components_from_path(filename=api_data['file'])
        if not components:
            api_data['components'] = []
        else:
            api_data['components'] = components
        return self.web_api.send_create_new_project_request(api_data=api_data)

    def create_project_gemlist_auto_system_path(self, api_data: dict) -> bool:
        print_line('Dont check yet')
        return False

    # CREATE SET

    def action_create_set(self, api_data: dict) -> bool:
        return True

    # ADDITION METHODS

    def load_and_parse_os_components_from_file(self, os_type: str, filename: str):
        components = []
        if os_type == 'windows':
            if os.path.exists(filename):
                with open(filename, encoding='utf-16') as cf:
                    os_packages = cf.read()
                    if os_packages is None:
                        components = []
                    else:
                        report = os_packages.replace('\r', '').split('\n')[9:]
                        components = self.parse_windows_packages(report)
                        if components is None:
                            components = []
                    return components
            else:
                print_line(f'File {filename} not exists. Return empty component set')
                return False

    def parse_npm_packages(self, comp) -> list:
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
                        proc = subprocess.Popen(
                            ["powershell", cmd],
                            stdout=subprocess.PIPE)
                        version = (proc.communicate()[0]).decode("utf-8")
                        version = version.replace('\n', '')
                    else:
                        # TODO: COMPLETE FOR ANOTHER PLATFORMS
                        version = '0.0.0'
                    components2.append({"name": name, "version": version})
        return components2

    @staticmethod
    def define_file_encoding(filename: str) -> str:
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

    def load_and_parse_npm_components_from_file(self, filename: str):
        components = []
        if os.path.exists(filename):
            enc = self.define_file_encoding(filename)
            if enc == 'undefined':
                print_line(f'Undefined file {filename} encoding.')
                return False
            try:
                with open(filename, 'r', encoding=enc) as pf:
                    data = json.load(pf)
                    walkdict(data)
                    components = self.parse_npm_packages(raw_npm_components)
                    return components
            except Exception as e:
                print_line(f'File read exception: {e}')
                return False
        print_line('File does not exist.')
        return False

    def load_and_parse_package_json_components_from_path(self, filename: str):
        components = []
        if os.path.exists(filename):
            enc = self.define_file_encoding(filename)

            if enc == 'undefined':
                print_line(f'Undefined file {filename} encoding.')
                return False

            try:
                with open(filename, 'r', encoding=enc) as pf:
                    packages = json.load(pf)
                    dependencies = packages['dependencies']
                    devDependencies = packages['devDependencies']
                    if devDependencies != {}:
                        for key in devDependencies.keys():
                            components.append({'name': key, 'version': str(devDependencies[key]).replace('^', '')})
                    if dependencies != {}:
                        for key in dependencies.keys():
                            components.append({'name': key, 'version': str(dependencies[key]).replace('^', '')})
                    return components
            except Exception as e:
                print_line(f'File {filename} read exception: {e}')
                return False
        print_line('File does not exist.')
        return False

    def load_and_parse_gem_components_from_path(self, filename: str):
        components = []
        if os.path.exists(filename):
            enc = self.define_file_encoding(filename)

            if enc == 'undefined':
                print_line(f'Undefined file {filename} encoding.')
                return False

            try:
                with open(filename, 'r', encoding=enc) as pf:
                    with open(filename, 'r') as pf:
                        cont = pf.read().replace('default: ', '').replace(' ', '').replace(')', '')
                        cont = cont.split('\n')
                        for c in cont:
                            if len(c) > 0:
                                cs = c.split('(')
                                try:
                                    components.append({'name': cs[0], 'version': cs[1]})
                                except:
                                    continue
                    return components
            except Exception as e:
                print_line(f'File {filename} read exception: {e}')
                return False
        print_line('File does not exist.')

    def load_and_parse_pip_components_from_path(self, filename: str):
        components = []
        if os.path.exists(filename):
            enc = self.define_file_encoding(filename)
            if enc == 'undefined':
                print_line(f'Undefined file {filename} encoding.')
                return False
            with open(filename, encoding=enc) as cf:
                rfp = cf.read()
                rfps = rfp.replace(' ', '').split('\n')
                for ref in rfps:
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
                                return False
                return components
        print_line('File does not exist.')
        return False

    @staticmethod
    def get_windows_packages(api_data: dict):
        if api_data['os'] != 'windows':
            print_line('Wrong platform defined.')
            return None
        if api_data['os_version'] == '10':
            cmd = "Get-AppxPackage -AllUsers | Select Name, PackageFullName"
            try:
                proc = subprocess.Popen(
                    ["powershell", cmd],
                    stdout=subprocess.PIPE)
                output, error = proc.communicate()
                if error:
                    print_line(f'Powershell command throw {proc.returncode} code and {error.strip()} error message.')
                if output:
                    return output
            except OSError as os_error:
                print_line(f'Powershell command throw errno: {os_error.errno}, strerror: {os_error.strerror} and '
                           f'filename: {os_error.filename}.')
                return None
            except:
                print_line(f'Powershell command throw an exception.')
                return None
        return None

    @staticmethod
    def parse_windows_packages(_report):
        packages = []
        report = _report
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
        except:
            print_line('Exception occured. Try run app with Administrator rights.')
            return None
        return packages

    @staticmethod
    def get_platforms(api_data: dict) -> list:
        platforms = []
        if api_data['organization'] is None:
            return platforms
        if api_data['organization']['platforms'] is None:
            return platforms
        for platform in api_data['organization']['platforms']:
            platforms.append(platform['name'])
        return platforms

    def get_projects(self, api_data: dict) -> list:
        projects = []
        if api_data['organization'] is None:
            return projects
        if api_data['organization']['platforms'] is None:
            return projects
        platform_number = self.web_api.get_platform_number_from_name(api_data=api_data)
        if platform_number == -1:
            return projects
        for project in api_data['organization']['platforms'][platform_number]['projects']:
            projects.append(project['name'])
        return projects


class Actions(object):
    SAVE_CONFIG = 'save_config'
    CREATE_PLATFORM = 'create_platform'
    CREATE_PROJECT = 'create_project'
    CREATE_SET = 'create_set'


class Targets(object):
    OS = 'os'
    PIP = 'pip'
    REQ = 'req'
    REQUIREMENTS = 'requirements'
    NPM = 'npm'
    PACKAGE_JSON = 'package_json'
    GEM = 'gem'
    GEMLIST = 'gemlist'
    GEMFILE = 'gemfile'


class Methods(object):
    AUTO = 'auto'
    MANUAL = 'manual'


class Formats(object):
    SYSTEM = 'system'
    MANUAL = 'manual'
