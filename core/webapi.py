# -*- coding: utf-8 -*-

import json
import requests
import datetime

from core.interface import print_line


class WebAPI(object):
    """
    Web API for Surepatch CLI Application.
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) \
        Gecko/20100101 Firefox/45.0',
        'token': ''}
    base_url = "https://beta.surepatch.net"
    login_url = base_url + "/api/auth/login"
    login_token_url = base_url + "/api/auth/token/login"
    organization_url = base_url + "/api/organization"
    platform_url = base_url + "/api/platforms"
    project_url = base_url + "/api/projects"
    issues_url = base_url + "/api/projects/partial"
    components_url = base_url + "/api/components"
    login_payload = dict(
        username=None,
        password=None,
        referalToken=None,
        organization=None)
    platform_payload = dict(
        name='',
        description='')
    project_payload = dict(
        platform_id='',
        parent=None,
        project_url=None,
        project_id=None,
        required_right='manage_projects',
        name='',
        denied_if_unpaid=True,
        logo=None,
        components=[])
    components_payload = dict(
        set_name='0.0.0',
        components=[],
        project_url=None)
    issues_payload = dict(

    )

    def send_login_token_request(self, api_data):
        # type: (dict) -> bool
        """
        Send login request with auth token to Surepatch server
        :param api_data: api data set
        :return: result
        """
        self.login_payload['authToken'] = api_data['auth_token']
        self.login_payload['org_domain'] = api_data['team']
        try:
            response = requests.post(
                url=self.login_token_url,
                headers=self.headers,
                json=self.login_payload)
            if response.status_code == 200:
                try:
                    text = response.text
                    login_response_text = json.loads(text)
                    api_data['token'] = login_response_text['token']
                    api_data['user_id'] = login_response_text['userID']
                    api_data['org_id'] = login_response_text['orgID']
                    api_data['organization'] = None
                    print_line('Login success.')
                    return True
                except ValueError as json_value_exception:
                    print_line('Response JSON parsing exception: {0}'.format(json_value_exception))
                    return False
            print_line('Login failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_login_user_password_request(self, api_data):
        # type: (dict) -> bool
        """
        Send login request with username and password to Surepatch server.
        :param api_data: api data set
        :return: result
        """

        self.login_payload['username'] = api_data['user']
        self.login_payload['password'] = api_data['password']
        self.login_payload['referalToken'] = None
        self.login_payload['organization'] = api_data['team']
        try:
            response = requests.post(
                url=self.login_url,
                headers=self.headers,
                json=self.login_payload)
            if response.status_code == 200:
                try:
                    text = response.text
                    login_response_text = json.loads(text)
                    if 'token' in login_response_text:
                        api_data['token'] = login_response_text['token']
                    else:
                        api_data['token'] = None
                        print_line('It seems that you have enabled two-factor authentication.')
                        print_line('CLI App does not support login/password with enabled MFA.')
                        print_line('To obtain auth token, please visit surepatch.com, login, go to Profile page.')
                        print_line('For successfull login in this case, use auth token in parameters or config file.')
                        return False
                    if 'userID' in login_response_text:
                        api_data['user_id'] = login_response_text['userID']
                    else:
                        api_data['user_id'] = None
                    if 'orgID' in login_response_text:
                        api_data['org_id'] = login_response_text['orgID']
                    else:
                        api_data['org_id'] = None
                    api_data['organization'] = None
                    print_line('Login success.')
                    return True
                except ValueError as json_value_exception:
                    print_line('Response JSON parsing exception: {0}'.format(json_value_exception))
                    return False
            print_line('Login failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_get_organization_parameters_request(self, api_data):
        # type: (dict) -> bool
        """
        Send special request to Surepatch server to get Organization information.
        :param api_data: api data set
        :return: result
        """
        self.headers['token'] = api_data['token']
        try:
            response = requests.get(
                url=self.organization_url,
                headers=self.headers)
            if response.status_code == 200:
                try:
                    text = response.text
                    organization_data = json.loads(text)[0]
                    api_data['organization'] = dict(
                        id=organization_data['_id'],
                        name=organization_data['name'],
                        token=organization_data['token'],
                        ownerID=organization_data['owner_id']['_id'],
                        username=organization_data['owner_id']['username'],
                        first_name=organization_data['owner_id']['firstname'],
                        last_name=organization_data['owner_id']['lastname'],
                        token_expires=organization_data['owner_id']['tokenExpires'],
                        password_expires=organization_data['owner_id']['passwordExpires'],
                        private_key=organization_data['owner_id']['privateKey'],
                        connection_id=organization_data['owner_id']['connectionID'],
                        version=organization_data['owner_id']['__v'],
                        password=organization_data['owner_id']['password'],
                        github=organization_data['owner_id']['github'],
                        notifications=organization_data['owner_id']['notifications'],
                        TFA=organization_data['owner_id']['TFA'],
                        open_key=organization_data['owner_id']['openKey'],
                        blocked_till=organization_data['owner_id']['blockedTill'],
                        failed_attempts=organization_data['owner_id']['failedAttempts'],
                        updated=organization_data['owner_id']['updated'],
                        super=organization_data['owner_id']['super'],
                        last_passwords=organization_data['owner_id']['lastPasswords'],
                        url=organization_data['url'],
                        stripe_id=organization_data['stripe_id'],
                        team_plan_id=organization_data['team_plan_id'],
                        all_projects=organization_data['allProjects'],
                        platforms=[])
                    for platform_data in organization_data['platforms']:
                        platform = dict(
                            id=platform_data['_id'],
                            name=platform_data['name'],
                            description=platform_data['description'],
                            url=platform_data['url'],
                            version=platform_data['__v'],
                            projects=[])
                        for project_data in platform_data['projects']:
                            project = dict(
                                id=project_data['_id'],
                                name=project_data['name'],
                                logo=project_data['logo'],
                                organization_id=project_data['organization_id'],
                                platform_id=project_data['platform_id'],
                                current_component_set=project_data['current_component_set'],
                                token=project_data['token'], url=project_data['url'],
                                version=project_data['__v'], updated=project_data['updated'],
                                created=project_data['created'], issues=project_data['issues'],
                                component_set_history=project_data['component_set_history'],
                                child_projects=project_data['child_projects'],
                                parent_projects=project_data['parent_projects'])
                            platform['projects'].append(project)
                        api_data['organization']['platforms'].append(platform)
                    return True
                except ValueError as json_value_exception:
                    print_line('Response JSON parsing exception: {0}'.format(json_value_exception))
                    return False
            print_line('Get organization parameters failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_create_new_platform_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to Surepatch server to create new Platform.
        :param api_data: api data set
        :return: result
        """
        self.headers['token'] = api_data['token']
        self.platform_payload['name'] = api_data['platform']
        self.platform_payload['description'] = api_data['description']
        try:
            response = requests.post(
                url=self.platform_url,
                headers=self.headers,
                json=self.platform_payload)
            if response.status_code == 200:
                return True
            print_line('Create platform failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_create_new_project_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to Surepatch server to create new Project.
        :param api_data: api data set
        :return: result
        """
        self.headers['token'] = api_data['token']
        self.project_payload['name'] = api_data['project']
        self.project_payload['platform_id'] = self.get_platform_id_by_name(api_data=api_data)
        self.project_payload['components'] = api_data['components']
        try:
            response = requests.post(
                url=self.project_url,
                headers=self.headers,
                json=self.project_payload)
            if response.status_code == 200:
                return True
            print_line('Create project failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_create_new_component_set_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to Surepatch server to create new Component Set.
        :param api_data: api data set
        :return:
        """
        self.headers['token'] = api_data['token']
        self.components_payload['set_name'] = api_data['set']
        self.components_payload['project_url'] = api_data['project_url']
        self.components_payload['components'] = api_data['components']
        try:
            response = requests.post(
                url=self.components_url,
                headers=self.headers,
                json=self.components_payload)
            if response.status_code == 200:
                return True
            print_line('Create component set failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_delete_platform_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to delete Platform.
        :param api_data: api data set
        :return: result
        """
        self.headers['token'] = api_data['token']
        try:
            response = requests.delete(
                url=self.platform_url + '/' + str(api_data['platform_id']),
                headers=self.headers,
                json=self.platform_payload)
            if response.status_code == 200:
                return True
            print_line('Delete Platform failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_delete_project_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to delete Project.
        :param api_data: api data set
        :return: result
        """
        self.headers['token'] = api_data['token']
        try:
            response = requests.delete(
                url=self.project_url + '/' + str(api_data['project_id']),
                headers=self.headers,
                json=self.project_payload)
            if response.status_code == 200:
                return True
            print_line('Delete Project failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_archive_platform_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to archive Platform.
        :param api_data: api data set
        :return: result
        """
        self.headers['token'] = api_data['token']
        self.platform_payload = dict(
            newPlatform=dict(
                id=api_data['platform_id'],
                url=api_data['platform_url'],
                options=dict(
                    updated=datetime.datetime.now().isoformat() + 'Z',
                    state='archive',
                    archivedBy=api_data['user']
                )
            )
        )
        try:
            response = requests.put(
                url=self.platform_url,
                headers=self.headers,
                json=self.platform_payload
            )
            if response.status_code == 200:
                return True
            print_line('Archive Platform failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_archive_project_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to archive Project.
        :param api_data: api data set
        :return: result
        """
        self.headers['token'] = api_data['token']
        self.project_payload['options'] = dict(
            newProject=dict(
                id=api_data['project_id'],
                url=api_data['project_url'],
                options = dict(
                    updated=datetime.datetime.now().isoformat() + 'Z',
                    state='archive',
                    archivedBy=api_data['user']
                )
            )
        )
        try:
            response = requests.put(
                url=self.project_url,
                headers=self.headers,
                json=self.project_payload)
            if response.status_code == 200:
                return True
            print_line('Archive Project failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_restore_platform_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to restore defined Platform from archive.
        :param api_data:
        :return:
        """
        self.headers['token'] = api_data['token']
        self.platform_payload = dict(
            newPlatform=dict(
                id=api_data['platform_id'],
                url=api_data['platform_url'],
                options=dict(
                    updated=datetime.datetime.now().isoformat() + 'Z',
                    state='open',
                    archived=None
                )
            )
        )
        try:
            response = requests.put(
                url=self.platform_url,
                headers=self.headers,
                json=self.platform_payload)
            if response.status_code == 200:
                return True
            print_line('Archive Platform failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_restore_project_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to restore defined Project from archive.
        :param api_data: api data set
        :return: result
        """
        self.headers['token'] = api_data['token']
        self.project_payload = dict(
            newProject=dict(
                id=api_data['project_id'],
                url=api_data['project_url'],
                options=dict(
                    updated=datetime.datetime.now().isoformat() + 'Z',
                    state='open',
                    archived=None
                )
            )
        )
        try:
            response = requests.put(
                url=self.project_url,
                headers=self.headers,
                json=self.project_payload)
            if response.status_code == 200:
                return True
            print_line('Archive Platform failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_get_archived_platforms_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to get all archived platforms.
        :param api_data: api data set
        :return: result
        """
        self.headers['token'] = api_data['token']
        try:
            response = requests.get(
                url=self.platform_url + '/archive/' + api_data['organization']['id'],
                headers=self.headers,
                json=self.platform_payload)
            api_data['archive_platforms'] = None
            if response.status_code == 200:
                try:
                    text = response.text
                    api_data['archive_platforms'] = json.loads(text)
                except json.JSONDecodeError as json_decode_error:
                    print_line('An exception occured with json decoder: {0}.'.format(json_decode_error))
                    return False
                return True
            print_line('Archive Platform get information failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_get_archived_projects_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to get all archived projects.
        :param api_data: api data set
        :return: result, modify api_data
        """
        self.headers['token'] = api_data['token']
        try:
            response = requests.get(
                url=self.project_url + '/archive/' + api_data['organization']['id'],
                headers=self.headers,
                json=self.project_payload)
            api_data['archive_projects'] = None
            if response.status_code == 200:
                try:
                    text = response.text
                    api_data['archive_projects'] = json.loads(text)
                except json.JSONDecodeError as json_decode_error:
                    print_line('An exception occured with json decoder: {0}.'.format(json_decode_error))
                    return False
                return True
            print_line('Archive Project get information failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    def send_get_issues_request(self, api_data):
        # type: (dict) -> bool
        """
        Send request to get Issues.
        :param api_data:
        :return:
        """
        self.headers['token'] = api_data['token']
        try:
            response = requests.post(
                url=self.issues_url + '/' + api_data['project_url'],
                headers=self.headers,
                json=self.issues_payload)
            api_data['archive_projects'] = None
            if response.status_code == 200:
                try:
                    content = response.content.decode("utf-8")
                    api_data['issues'] = json.loads(content)['project']['issues']
                    return True
                except json.JSONDecodeError as json_decode_error:
                    print_line('An exception occured with json decoder: {0}.'.format(json_decode_error))
                    return False
            print_line('Archive Project get information failed. Status code: {0}'.format(response.status_code))
            return False
        except requests.exceptions.HTTPError as http_exception:
            print_line('HTTP Error: {0}'.format(http_exception))
            return False
        except requests.exceptions.ConnectionError as connection_exception:
            print_line('Connection error: {0}'.format(connection_exception))
            return False
        except requests.exceptions.Timeout as timeout_exception:
            print_line('Connection timeout: {0}'.format(timeout_exception))
            return False
        except requests.exceptions.RequestException as request_exception:
            print_line('Request exception: {0}'.format(request_exception))
            return False

    @staticmethod
    def get_platform_id_by_name(api_data):
        # type: (dict) -> int
        """
        Get platform ID by its name.
        :param api_data: api data set
        :return: result
        """
        platform_name = api_data['platform']
        for platform in api_data['organization']['platforms']:
            if platform['name'] == platform_name:
                return platform['id']
        return -1

    @staticmethod
    def get_platform_number_by_name(api_data):
        # type: (dict) -> int
        """
        Get Platform number in list by its name.
        :param api_data: api data set
        :return:result
        """

        platform_name = api_data['platform']
        for index, platform in enumerate(api_data['organization']['platforms']):
            if platform['name'] == platform_name:
                return index
        return -1

    def get_project_number_by_name(self, api_data):
        # type: (dict) -> int
        """
        Get project number (index) by its name.
        :param api_data: api data set
        :return: result
        """

        project_name = api_data['project']
        platform_number = self.get_platform_number_by_name(api_data=api_data)
        for index, project in enumerate(api_data['organization']['platforms'][platform_number]['projects']):
            if project['name'] == project_name:
                return index
        return -1
