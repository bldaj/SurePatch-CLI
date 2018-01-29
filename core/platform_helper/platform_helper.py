#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from core.interface import print_line
from core.webapi import WebAPI


class PlatformHelper(object):

    def __init__(self):
        self.web_api = WebAPI()

    @staticmethod
    def create_platform_validate(api_data: dict) -> bool:
        if api_data['platform'] is None or api_data['platform'] == '':
            print_line('Empty platform name, please use --platform flag.')
            return False

        if api_data['description'] is None or api_data['description'] == '':
            print_line('Empty platform description. Change description to "default platform".')
            api_data['description'] = "default platform"

        return True

    def create_platform(self, api_data: dict) -> bool:
        return self.web_api.send_create_new_platform_request(api_data=api_data)

    def delete_platform(self, api_data: dict) -> bool:
        """
        Run action: Delete defined Platform.
        :param api_data: api data set
        :return: result
        """
        api_data['platform_id'] = self.web_api.get_platform_id_by_name(api_data=api_data)
        if api_data['platform_id'] == -1:
            print_line(f"Platform {api_data['platform']} does not exist.")
            return False

        return self.web_api.send_delete_platform_request(api_data=api_data)

    def archive_platform(self, api_data: dict) -> bool:
        """
        Run action: Archive defined Platform.
        :param api_data: api data set
        :return: result
        """
        api_data['platform_id'] = self.web_api.get_platform_id_by_name(api_data=api_data)
        if api_data['platform_id'] == -1:
            print_line(f"Platform {api_data['platform']} does not exist.")
            return False

        return self.web_api.send_archive_platform_request(api_data=api_data)

    def restore_platform(self, api_data: dict) -> bool:
        """
        Run action: restore Platform from Archive.
        :param api_data: api data set
        :return: result
        """
        if api_data['platform'] is None or api_data['platform'] == '':
            print_line('Empty platform name.')
            return False

        if not self.web_api.send_get_archived_platforms_request(api_data=api_data):
            print_line('There were errors in obtaining archived platforms.')
            return False

        api_data['platform_id'] = None
        api_data['platform_url'] = None

        for archive_platform in api_data['archive_platforms']:
            if api_data['platform'] == archive_platform['name']:
                api_data['platform_id'] = archive_platform['_id']
                api_data['platform_url'] = archive_platform['url']
                break

        if api_data['platform_id'] is None:
            print_line(f"Not such platform {api_data['platform']} in archive.")
            return False

        return self.web_api.send_restore_platform_request(api_data=api_data)