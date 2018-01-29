# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
from textwrap import wrap
from terminaltables import AsciiTable


def print_logo():
    print('\n')
    print('+------------------------------------------------------------------------------------------------+')
    text = """
                     #####                       ######                             
                    #     # #    # #####  ###### #     #   ##   #####  ####  #    # 
                    #       #    # #    # #      #     #  #  #    #   #    # #    # 
                     #####  #    # #    # #####  ######  #    #   #   #      ###### 
                          # #    # #####  #      #       ######   #   #      #    # 
                    #     # #    # #   #  #      #       #    #   #   #    # #    # 
                     #####   ####  #    # ###### #       #    #   #    ####  #    # 
                    (c) WebSailors, 2018
     """
    print(text)
    print('+------------------------------------------------------------------------------------------------+')


def print_line(message: str) -> None:
    print('+------------------------------------------------------------------------------------------------+')
    print(message)
    print('+------------------------------------------------------------------------------------------------+')


def print_table(elements: list, title: str = None, filename: str = None) -> None:
    if len(elements) > 0:
        if 'version' in elements[0].keys():
            table_data = [
                ['Name', 'Version']
            ]
            table = AsciiTable(table_data)
            table.padding_left = 1
            table.padding_right = 1
            max_width = 80
            if title is not None:
                table.title = title
            for element in elements:
                table_data.append(
                    [element['name'],
                     '\n'.join(wrap(element['version'], max_width))]
                )
            print(table.table)
            if filename is not None:
                try:
                    with open(filename, 'w') as fp:
                        fp.write(table.table)
                except IOError as e:
                    print_line(f"Exception {e} occured while write file {filename}.")
        elif 'description' in elements[0].keys():
            table_data = [
                ['Name', 'Description']
            ]
            table = AsciiTable(table_data)
            table.padding_left = 1
            table.padding_right = 1
            max_width = 80 # table.column_max_width(1)
            if title is not None:
                table.title = title
            for element in elements:
                table_data.append(
                    [element['name'],
                    '\n'.join(wrap(element['description'], max_width))]
                )
            print(table.table)
            if filename is not None:
                try:
                    with open(filename, 'w') as fp:
                        fp.write(table.table)
                except IOError as e:
                    print_line(f"Exception occured while write file {filename}.")


def print_components(components: list,  title: str = None, filename: str = None) -> None:
    print_line('Components:')
    print_table(elements=components, title=title, filename=filename)


def print_platforms(platforms: list,  title: str = None, filename: str = None) -> None:
    print_line('Platforms:')
    print_table(elements=platforms, title=title, filename=filename)


def print_projects(projects: list,  title: str = None, filename: str = None) -> None:
    print_line('Projects:')
    print_table(elements=projects, title=title, filename=filename)


def print_issues(issues: list, title: str = None, filename: str = None) -> None:
    print_line('Issues:')
    print_table(elements=issues, title=title, filename=filename)


def ask(message: str) -> str:
    if sys.version_info > (3, 0):
        return input(message)
    else:
        return raw_input(message)
