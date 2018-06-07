# Surepatch CLI Application
Surepatch CLI App - is a complex solution for your projects and OS security.
This application is designed to work with the Surepatch Project without using the web interface. You can use it both in manual and automatic mode in operating systems with a graphical interface and on server stations without a graphical interface. You can use the application as part of scripts for automatic builds to test the security of your application and the operating system packages after each change. You can constantly maintain the current state of security packages, including the application in the schedule. You can completely control your platforms, projects and component sets without using a browser, receive actual reports and solutions from periodically updated vulnerability database.
# CLI App Features
- Main Features:
    - Create, delete, archive and restore Platforms
    - Create, delete, archive and restore Projects
    - Create Component Sets with defined names and with autoincrement set numbers
    - Print and export to files Platforms, Projects, Components and Issues
    - Use more than one target to collect packages
- Operating modes:
    - Automatic
    - Manual
- Supported formats:
    - System formats for package manager like shell, python pip, gem, npm, composer, pom, etc.
    - User format for special files with custom packages
- Packages Management:
    - Collect Packages from Windows, MacOS, Linux Operation Systems
    - Collect Packages from Python PIP and requirements.txt sources
    - Collect Packages from NPM, yarn, NodeJS package.json and package-lock.json sources
    - Collect Packages from Ruby, Gemfile and Gemfile.lock sources
    - Collect Packages from PHP, composer.json and composer.lock files
    - Collect Packages from Maven pom.xml files
    - Collect Packages from user format file resources
    - Collect Packages in interactive dialog mode

# Table of contents
- Installation
- Build
- CLI App arguments
- CLI App config
- Login variants
- Important notes
- Operations with Platforms
- Operations with Projects
- Operations with Component Sets
- Show information
- Sample scenarios

# Installation
## From pip install
...
## From OS package
...
## From Gihtub
[Package](http://surepatch.com)

# Build
You can build your own executable "surepatch" file with pyinstaller. This module already included into project requirements.txt file,
so, you should install python3, download source code and execute "build" script from build_scripts folder or use the next command from project folder:
```sh
@ pip3 install -r requirements.txt
```
and than
```sh
@ pyinstaller --onefile surepatch.py
```
The executable file will be in /dist folder.

# CLI App arguments

|Argument|Value|Description|
|---|---|---|
|--team| <your_team> | Your Team on Surepatch project|
| | | |
|--user| <your_username> | Your username (e-mail)|
| | | |
|--password| <your_password> | Your password|
| | | |
|--auth_token| <your_token> | Token to authorize without username/password |
| | | |
|--action| <action_type> | CLI App action:|
| | save_config | Save account parameters |
| | create_platform | Create New Platform |
| | create_project | Create New Project in defined Platform |
| | create_set | Create New Components Set in defined Platform/Project|
| | delete_platform | Delete Platform |
| | delete_project | Delete Project in defined Platform|
| | archive_platform | Archive Platform |
| | archive_project | Archive Project for defined Platform |
| | restore_platform | Restore Platform |
| | restore_project | Restore Project in defined Platform |
| | show_platforms | Print all Platforms in account |
| | show_projects | Print all Projects in defined Platform |
| | show_set | Print current component set for defined Platform/Project |
| | show_issues | Print issues for defined Platform/Project |
| | | |
|--platform| <platform_name> | Name of Platform for different actions|
| | | |
|--description| <platform_description>| Description of Platform |
| | | |
|--project|<project_name>| Name of Project for different actions |
| | | |
|--set|<set_name>| Name of set for different actions |
| | | |
|--target|<target_type>| CLI App Targets: |
| |os| Target is Operation system Packages |
| |pip| Target is Python pip Packages |
| |pip3| Target is Python3 pip3 Packages |
| |req| Target is Python PIP Packages |
| |req3| Target is Python3 pip3 Packages |
| |requirements| Target is Python requirements.txt file |
| |requirements3| Target is Python3 requirements.txt file |
| |npm| Target is NPM Packages |
| |npm_local| Target is NPM Packages from defined directory |
| |package_json| Target is NPM package.json file |
| |package_lock_json| Target is NPN package-lock.json file |
| |gem| Target is Ruby gem Packages |
| |gemfile| Target is Ruby Gemfile source |
| |gemfile_lock| Target is Ruby Gemfile.lock source |
| |php_composer_json| Target is PHP composer.json source |
| |php_composer_lock| Target is PHP composer.lock source |
| |pom| Target is Maven pom.xml source |
| |yarn| Target is yarn.lock source |
| | | |
|--method:|<method_type>|CLI App Methods:|
| |auto|Collect Packages automatically |
| |manual|Collect Packages in interactive mode |
| | | |
|--format|<format_type>|CLI App Formats:|
| |system| System Format Packages (from package managers or OS) |
| |user| User defined Packages format <name>=<version>|
| | | |
|--file|<path_to_file_or_dir>| Path to file with Packages or Directory |
|--logo|<on_off>| Show logo when started or not |

# CLI App Config
### Create local config file
A local configuration file will be created in home directory (~/.surepatch.yaml).
After that, the authorization information will be read from this file each time the action is started.
You can change directly in file or with the help of save_config command.
```sh
@ surepatch.py --action=save_config --team=testers --user=user@gmail.com --password=test_password --logo=off
```
# Login variants
Note, that login operation call before every CLI App run to make your server information in actial state, so authirization parameters should be define in command line interface in CLI App or in config file.
### 1. With auth token from CLI App parameters
This variant usefull for quick authirization with auth token from surepatch server. This is first priority login way.
Note, that you should point your irganization with --team parameter.
For example we want look through our issues:
```sh
@ surepatch  --action=show_issues --platform=wintest --project=my_platform --auth_token=3a4953e5sdf1235df598b34e434fd0754e3 --team=my_team
```
### 2. With auth token from CLI App config file
This variand has second priority and usefull for more than one account. In this case, token will be take from config file, and no matter what is specified in the interface.
```sh
@ surepatch  --action=save_config --auth_token=3a4953e5sdf1235df598b34e434fd0754e3 --team=my_team
```
### 3. With username/password from CLI App parameters
For example there are two accounts, and the first organization "org1" login parameters store in config file, but you want look through projects from "org2" account. So, actual login parameters will be take from console parameters, not from config file.

For account # 1:

```sh
@ surepatch --action=save_config --team=org1 --user=user1@gmail.com --password=test_password --logo=off
```

And for account # 2:

```sh
@ surepatch --action=show_projects --platform=platform2 --team=org2 --user=user2@gmail.com --password=test_password_2
```
### 4. With username/password from CLI App config file
This is simple way to use CLI App - you save config file with team, username and password and than use those parameters without token automatically.
```sh
@ surepatch --action=save_config --team=org1 --user=user1@gmail.com --password=test_password --logo=off
```

And than:

```sh
@ surepatch --action=show_projects --platform=myplatform
```

# Important notes:
- If you do not explicitly specify the parameters, they will be set to the default values:

  --format=system and --method=auto, so you can use short command line notations.
- You can use group definitions for targets and files to call one operation for different targets.

  For example:

  This command will create project for OS, PIP, POM, GEM and Gemfile packages
```sh
@ surepatch --action=create_project --platform=newtest --project=multitest2 --target=[os,pip,pom,gem,gemfile] --file=[no,no,/home/user/pom2.xml,no,/home/user/Gemfile]
```

And this command will create set for YARN, PIP3 and Gemfile.lock
```sh
@ surepatch --action=create_set --platform=newtest --project=settest --target=[yarn,pip3,gemfile_lock] --file=[/home/user/yarn.lock,no,/home/user/Gemfile.lock]
```

- With actions like show platforms, show projects, show cset and show issues you can use --file=<path> parameter to save the results into defined file.

For example:
```sh
@ surepatch --action=show_issues --platform=newtest --project=settest --file=/home/user/issues_report.txt
```

- You can find complete set of examples of surepatch: demo_mac, demo_win, demo_ubuntu...
- Note, that some operation required root privileges, so use Administrator rights console or 'sudo' mode in your system.
- You can enable Two-factor authentication in SurePatch profile, but CLI App work without MFA in automatic mode.

# Operations with Platforms
### Create your first Platform
Note, thad Platform description should be wrote like "My Description".
If --description is empty, Platform will be named as "default platform".
```sh
@ surepatch --action=create_platform --platform=newtest --description="New Platform for Autotest"
```
### Archive Platform
If you want archive Platform, you may use web interface or CLI App command
```sh
@ surepatch --action=archive_platform --platform=newtest
```
### Restore Platform
If you want restore archived Platform, you may use web interface or CLI App command
```sh
@ surepatch --action=restore_platform --platform=newtest
```
### Delete Platform
If you want delete Platform, you may use web interface or CLI App command
```sh
@ surepatch --action=delete_platform --platform=newtest
```
# Operations with Projects
### Create Project from OS Packages, collected by shell command inside CLI App.
CLI App call shell command inside and process its output depending on the type of operating system.
Note, that this operation require root privileges.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_os_none --target=os --method=auto --format=system
```
### Create Project from OS Packages, pre-uploaded to an external file, for example /home/user/os_packages.txt
This way use already created file with OS Packages and pre-unloaded into some directory.
Note, that CLI App use OS format for this file, depending on OS type.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_os_path --target=os --method=auto --format=system --file=/home/user/os_packages.txt
```
### Create Project from Python PIP Packages, collected by shell command inside CLI App.
This example shows, how you can create Python packages set from pip.FrozenRequirement call.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_pip_none --target=pip --method=auto --format=system
```
If you want use pip3 packages - you should define pip3 target, like this:
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_pip3_none --target=pip3 --method=auto --format=system
```
### Create Project from Python PIP Packages, pre-unloaded to an external file from shell command (pip freeze > file_path), for example /home/user/pip_freeze_packages.txt
In this way, you can check security of your Python freeze files. Please, use command
```sh
@ pip freeze > file_path
```
Note, that CLI App use Python system format for this file.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_pip_path --target=pip --method=auto --format=system --file=/home/user/pip_freeze_packages.txt
```
If you want use pip3 packages - you should define pip3 target, like this:
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_pip3_path --target=pip3 --method=auto --format=system --file=/home/user/pip_freeze_packages.txt
```
### Create Project from Python Packages, collected in requirements.txt, for example /home/user/requirements.txt
Now you can check vulnerabilities for your requirements.txt files in different applications.
Note, that CLI App use Python system format for this file.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_req_path --target=req --method=auto --format=system --file=/home/user/requirements.txt
```
If you want use pip3 packages - you should define pip3 target, like this:
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_req3_path --target=req3 --method=auto --format=system --file=/home/user/requirements.txt
```
### Create Project from NPM Packages, collected by shell command inside CLI App
CLI App call shell globally from root path and done npm list --json command with postprocessing.
Note, that CLI App use NPM system format for those data.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_npm_none --target=npm --method=auto --format=system
```
### Create Project from NPM Packages, collected by shell command inside ALI App, for example /home/user/workspace/node_project
CLI App call shell locally from defined directory and done npm list --json command with postprocessing.
Note, that CLI App use NPM system format for those data.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_local_none --target=npm_local --method=auto --format=system --file=/home/user/workspace/node_project
```
### Create Project from NPM Packages, collected by shell command before and pre-unloaded to an external file, for example /home/user/npm.txt
Now CLI App process file, which was created by calling npm list --json command from root path or defined project directory.
Note, that CLI App use NPM system format for those data.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_npm_path --target=npm --method=auto --format=system --file=/home/user/npm.txt
```
### Create Project from NPM Packages, collected in package.json file, for example /home/user/package.json
This way, you can create project from packages, collected in package.json file.
Note, that CLI App use NPM system format for those data.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_npm_package_json --target=package_json --method=auto --format=system --file=/home/user/package.json
```
### Create Project from NPM Packages, collected in package-lock.json file, for example /home/user/package-lock.json
This way, you can create project from packages, collected in package-lock.json file.
Note, that CLI App use NPM system format for those data.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_npm_package_lock_path --target=package_lock_json --method=auto --format=system --file=/home/user/package-lock.json
```
### Create Project from Ruby Packages, collected by shell command
CLI App call gem list command from shell globally and process system result.
Note, that CLI App use Ruby gem system format for those data.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_gem_none --target=gem --method=auto --format=system
```
### Create Project from Ruby Packages, collected by shell command before and pre-unloaded to an external file, for example /home/user/gem.list
This way, CLI App process gem.list file, created by shell call of gem list command.
Note, that CLI App use Ruby gem system format for those data.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_gem_path --target=gem --method=auto --format=system --file=/home/user/gem.list
```
### Create Project from Ruby Packages, collected in Gemfile, for example /home/user/Gemfile
This way, CLI App process Gemfile file.
Note, that CLI App use Ruby gem system format for those data.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_gemfile_path --target=gemfile --method=auto --format=system --file=/home/user/Gemfile
```
### Create Project from Ruby Packages, collected in Gemfile.lock, for example /home/user/Gemfile.lock
This way, CLI App process Gemfile.lock file.
Note, that CLI App use Ruby gem system format for those data.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_gemfile_lock_path --target=gemfile_lock --method=auto --format=system --file=/home/user/Gemfile.lock
```
### Create project from PHP Composer file, for example /home/user/composer.json
This way, CLI App process PHP composer.json file.
Note, that CLI App use PHP composer system format for those data.
```sh
@ surepatch --action=create_project --platform=autotest2 --project=autotest_php_composer_json --target=php_composer_json --method=auto --format=system --file=/home/user/composer.json
```
### Create project from PHP Composer.lock file, for example /home.user/composer.lock
This way, CLI App process PHP composer.lock file.
Note, that CLI App use PHP composer system format for those data.
```sh
@ surepatch --action=create_project --platform=autotest2 --project=autotest_php_composer_lock --target=php_composer_lock --method=auto --format=system --file=/home/user/composer.lock
```
### Create project from Maven pom.xml file, for example /home/user/pom.xml
This way, CLI App process Maven pom.xml file with dependencies.
Note, that CLI App use Maven pom.xml system format for those data.
```sh
@ surepatch --action=create_project --platform=autotest2 --project=autotest_maven_pom --target=pom --method=auto --format=system --file=/home/user/pom.xml
```
### Create project from yarn.lock file, for example /home/user/yarn.lock
This way, CLI App process yarn.lock file with dependencies.
Note, that CLI App use yarn.lock system format for those data.
```sh
@ surepatch --action=create_project --platform=autotest2 --project=autotest_yarn --target=yarn --method=auto --format=system --file=/home/user/yarn.lock
```
### Create Project from User defined source file, for example /home/user/user_packages.txt, where packages defined as lines in <name>=<version> format
Now, you can create some file and fill it with different packages and versions.
The type of package and its ownership does not matter.
Note, that one package fill one line of file like this:
name1=version1
name2=version2
name3=version3
...
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_any_user_path  --method=auto --format=user --file=c:\user_packages.txt
```
### Create Project from User defined format in interactive mode
In this user mode, you have interactive console, when you can enter names and version of your components consistently,
component by component.
```sh
@ surepatch --action=create_project --platform=newtest --project=autotest_any_user_none --method=manual --format=user
```
### Archive Project
If you want archive Project in defined Platform, you may use web interface or CLI App command
```sh
@ surepatch --action=archive_project --platform=newtest --project=testproject
```
### Restore Project
If you want restore archived Project in defined Platform, you may use web interface or CLI App command
```sh
@ surepatch --action=restore_project --platform=newtest --project=testproject
```
### Delete Project
If you want delete Project in defined Platform, you may use web interface or CLI App command
```sh
@ surepatch --action=delete_project --platform=newtest --project=testproject
```
# Operations with Components sets
Now, you can create Component Sets for existing Platforms/Projects.
You can define set name by parameter --set=<set_name> of leave this field blank.
In the first case, we check uniqueness of set name and create one.
In the second case, we get your current set name, and than:
- if name like 0.0.1 - we increase number automatically like 0.0.2, 0.0.3, ...
- if name like branch_version_set - we call it testing_back_set.1 and than increase last digit automatically
### Create set from OS packages, collected by shell command inside CLI App
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=os_none.1 --target=os --method=auto --format=system
```
### Create set from OS packages, collected from shell command, unloaded to file, for example /home/user/os_packages.txt
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=os_path.1 --target=os --method=auto --format=system --file=/home/user/os_packages.txt
```
### Create set from PIP Packages, collected from shell command inside CLI App
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=pip_none.1 --target=pip --method=auto --format=system
```
And for pip3 packages:
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=pip3_none.1 --target=pip3 --method=auto --format=system
```
### Create set from Python PIP packages, collected from shell command (pip freeze > file_path), unloaded to file, for example /home/user/pip_freeze_packages.txt
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=pip_path.1 --target=pip --method=auto --format=system --file=/home/user/pip_freeze_packages.txt
```
And for pip3 packages:
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=pip3_path.1 --target=pip3 --method=auto --format=system --file=/home/user/pip_freeze_packages.txt
```
### Create set from Python packages from requirements.txt, for example /home/user/requirements.txt
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=req_path.1 --target=req --method=auto --format=system --file=/home/user/requirements.txt
```
And for pip3 packages:
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=req3_path.1 --target=req3 --method=auto --format=system --file=/home/user/requirements.txt
```
### Create set from NPM packages, collected from shell command (npm list --json) from root dir
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=npm_none.1 --target=npm --method=auto --format=system
```
### Create set from NPM packages, collected from shell command (npm list --json) from root dir, unloaded to file, for example /home/user/npm.txt
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=npm_path.1 --target=npm --method=auto --format=system --file=/home/user/npm.txt
```
### Create set from NPM packages, collected from shell command (npm list --json) from local dir, for example /home/user/workspace/node
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=npm_local_path.1 --target=npm_local --method=auto --format=system --file=/home/user/workspace/node
```
### Create set from NPM packages, collected from package-lock.json file, for example /home/user/package-lock.json
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=npm_package_json_lock_path.1 --target=package_lock_json --method=auto --format=system --file=/home/user/package-lock.json
```
### Create set from NPM packages, collected from package.json file, for example /home/user/package.json
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=npm_package_json_path.1 --target=package_json --method=auto --format=system --file=/home/user/package.json
```
### Create set from Ruby packages, collected from shell command inside CLI App
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test  --set=gem_none.1 --target=gem --method=auto --format=system
```
### Create set from Ruby packages, collected from shell commend, unloaded to file before, for example /home/user/gem.list
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=gem_path.1 --target=gem --method=auto --format=system --file=/home/user/gem.list
```
### Create set from Ruby packages, collected from Gemfile, for example /home/user/Gemfile
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=gem_gemfile_path.1 --target=gemfile --method=auto --format=system --file=/user/home/Gemfile
```
### Create set from Ruby packages, collected from Gemfile.lock file, for example /home/user/Gemfile.lock
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=gem_gemfile_lock_path.1 --target=gemfile_lock --method=auto --format=system --file=/home/user/Gemfile.lock
```
### Create set from PHP Composer file, for example /home/user/composer.json
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=php_composer_json.1 --target=php_composer_json --method=auto --format=system --file=/home/user/composer.json
```
### Create set from PHP Composer.lock file, for example /home/user/composer.lock
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=php_composer_lock.1 --target=php_composer_lock --method=auto --format=system --file=/home/user/composer.lock
```
### Create set from Maven pom.xml file, for example /home/user/pom.xml
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=pom.1 --target=pom --method=auto --format=system --file=/home/user/pom.xml
```
### Create set from yarn.lock file, for example /home/user/yarn.lock
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=yarn.1 --target=yarn --method=auto --format=system --file=/home/user/yarn.lock
```
### Create set from User packages, formatted as name=version
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=user_path.1  --method=auto --format=user --file=c:\user_packages.txt
```
### Create set from User packages, asked via console
```sh
@ surepatch --action=create_set --platform=newtest --project=autotest_set_test --set=user_manual.1 --method=manual --format=user
```
# Show information
### Show platforms
```sh
@ surepatch --action=show_platforms
```
or
```sh
@ surepatch --action=show_platforms --file=/home/user/platforms_report.txt
```
### Show projects
```sh
@ surepatch --action=show_projects --platform=newtest
```
or
```sh
@ surepatch --action=show_projects --platform=newtest --file=/home/user/projects_report.txt
```
### Show set
```sh
@ surepatch --action=show_set --platform=newtest --project=autotest_set_test
```
or
```sh
@ surepatch --action=show_set --platform=newtest --project=autotest_set_test --file=/home/user/set_report.txt
```
### Show issues
```sh
@ surepatch --action=show_issues --platform=newtest --project=autotest_set_test
```
or
```sh
@ surepatch --action=show_issues --platform=newtest --project=autotest_set_test --file=/home/user/issues_report.txt
```
# Sample scenarios
### Simple sequence
```sh
@ surepatch --action=create_platform --platform=newtest --description=NewTestPlatform
```
```sh
@ surepatch --platform=newtest --action=create_project --project=pyproject --target=[os,pip,req] --file=[no,no,/home/user/workspace/pythonproject/requirements.txt]
```
Now work with project and save project state like this
```sh
@ surepatch --platform=newtest --action=create_set --project=pyproject --target=[os,pip,req] --file=[no,no,/home/user/workspace/pythonproject/requirements.txt]
```
Fix vulnerabilities and than check changes like this
```sh
@ surepatch --platform=newtest --action=create_set --project=pyproject --target=[os,pip,req] --file=[no,no,/home/user/workspace/pythonproject/requirements.txt]
```
### Use CLI App with docker
#### Example.
Doing action via ./surepatch.py inside docker container
1. Make sure that Docker is running
2. Choose or create directory where will be placed SurePatch project
3. Go to the directory:
   ```sh
   cd <your_work_directory>
   ```
4. Clone SurePatch from github:
   ```sh
   git clone https://github.com/WorkSecure/SurePatch-CLI
   ```
5. Go to SurePatch directory:
   ```sh
   cd SurePatch-CLI
   ```
6. In this example we will use Dockerfile. You must fill the following parameters in the Dockerfile:
- team
- user
- password
   ```sh
    FROM ubuntu
    RUN apt-get update
    RUN apt-get install -y python3 python3-pip
    RUN pip3 install --upgrade pip
    COPY . /surepatch
    WORKDIR /surepatch
    RUN pip3 install -r requirements.txt
    RUN chmod +x surepatch.py
    RUN python3 surepatch.py --action=save_config --team=<team> --user=<email> --password=<password>
    CMD ["/bin/bash"]
   ```

If you do not have a Dockerfile, then create it and write in it the commands written above.
Save changes.

7. Create image via docker build command:
   ```sh
   docker build -t <image name> .
   ```
8. Run docker container:
   ```sh
   docker run -it <image name>
   ```
9. Run surepatch.py:
   ```sh
   ./surepatch.py --action=<action> --server=<server_name>
   ```
10. Exit from container:
   ```sh
   exit
   ```
### Use CLI App with Jenkins
If you want to use Jenkinsfile and Dockerfile from example, copy Jenkinsfile and Dockerfile from directory build_scripts/Linux Manjaro to root of project.

#### Example for Linux Manjaro
1. Install Jenkins from package manager Octopi:
2. Make sure that Docker is running:
   ```sh
   systemctl status docker
   ```
   If Docker in not running, start it:
   ```sh
   sudo systemctl start docker
   ```
3. Change permissions for docker.sock:
   ```sh
   sudo chmod 777 /var/run/docker.sock
   ```
4. Make sure that Jenkins is running:
   ```sh
   systemctl status jenkins
   ```
   If Jenkins in not running, start it:
   ```sh
   sudo systemctl start jenkins
   ```
5. After installation, open a browser and connect to the following URL:
   ```sh
   http://localhost:8090
   ```
6. You will need to copy the initial password from the file system of the server:
  ```sh
  sudo cat /var/lib/jenkins/secrets/initialAdminPassword
  ```
7. Copy password from output of command 'cat' and paste it in Jenkins in browser.
8. Install suggested plugins.
9. Create the first Administrator user and press Save and Finish.
10. Create Dockerfile as following:
   ```sh
   FROM ubuntu
   RUN apt-get update
   RUN apt-get install -y python3 python3-pip
   RUN pip3 install --upgrade pip
   COPY . /surepatch
   WORKDIR /surepatch
   RUN pip3 install -r requirements.txt
   WORKDIR /surepatch/build_scripts
   RUN bash build_ubuntu.sh
   WORKDIR /surepatch/dist
   # SUREPATCH COMMANDS
   RUN ./surepatch_deb --team=<your_team> --user=<your_user_email> --password=<your_password> --action=show_platforms
   ```
Save the Dockerfile in root of project.

11. Now create Jenkinsfile with next commands and save it in root of project:
   ```sh
   pipeline {
       agent { dockerfile true }
       stages {
           stage('Test') {
               steps {
                   echo "Complete work"
               }
           }
       }
   }
   ```
12. Go to Jenkins in browser and create job.
13. Input name of job and choose Pipeline type and press OK.
14. In section Pipeline in Definition select Pipeline script from SCM. In SCM field select git and specify Repository URL. After this press Save.
15. Now press button Build Now from left . You will see new build in Build History where you can look at Console Output of build.

Result of Jenkins work
   ```sh
   Started by user <your_username>
   Obtained Jenkinsfile from git <repository_url>
   ...
   [test surepatch] Running shell script
   + docker build -t 8821a26d25a6a51a13e94fe1fe068d93d4d5a59c -f Dockerfile .
   Sending build context to Docker daemon  37.44MB

   Step 1/12 : FROM ubuntu
   Step 2/12 : RUN apt-get update
   Step 3/12 : RUN apt-get install -y python3 python3-pip
   Step 4/12 : RUN pip3 install --upgrade pip
   Step 5/12 : COPY . /surepatch
   Step 6/12 : WORKDIR /surepatch
   Step 7/12 : RUN pip3 install -r requirements.txt
   # Installing requirements
   Step 8/12 : WORKDIR /surepatch/build_scripts
   Step 9/12 : RUN bash build_ubuntu.sh
   Start build...................
   Step 10/12 : WORKDIR /surepatch/dist
   Step 11/12 : RUN ./surepatch_deb --team=<your_team> --user=<your_user_email> --password=<your_password> --action=show_platforms
   Login success.
   Platforms:
  +Platforms----+------------------------+
  | Name        | Description            |
  +-------------+------------------------+
  | wintest     | wintestPlatform        |
  | mactest     | mactestPlatform        |
  | mactest2    | mactest2Platform       |
  | mfa         | mfa                    |
  | docker_test | Tests for Docker Usage |
  +-------------+------------------------+
  Complete successfully with targets ['']
  Process 0 components
  Step 12/12 : CMD ["/bin/bash"]
  ...
  [Pipeline] {
  [Pipeline] stage
  [Pipeline] { (Test)
  [Pipeline] echo
  Complete work
  [Pipeline] }
  [Pipeline] // stage
  [Pipeline] }
  ...
  Finished: SUCCESS
  ```
# License
...
# (c) BrainBankers, 2018.
