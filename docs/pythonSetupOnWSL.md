# Python Setup for Backend Development in Windows using WSL

### Project Setup - Contents
0. [Mandatory Must-TODO](#mandatory-must-todo)
1. [Laptop Setup](#laptop-setup)
2. [Getting the Repository](#getting-the-repository)


NOTE - The '>' symbol at the start of a line specified that it is a terminal command for easy readability.

### Mandatory Must-TODO
You will understand this point after completing the laptop setup, and backend setup of the repo.

```
1. Xserver MUST ALWAYS be running before starting any GUI-based app from WSL terminal.
2. All these things will happen only from the wsl/ubuntu terminals. Do not confuse it with the windows terminal.
```
## Laptop Setup

These sub-projects can be run on either a Linux based VMware or Ubuntu or WSL on Windows.
In case of WSL, the base operating system required here is Linux, which can be accessed via the Windows Subsystem for Linux on a Windows Machine.

#### Linux subsystem for Windows (WSL)

```
Enable feature in windows settings
    Refer - https://www.windowscentral.com/install-windows-subsystem-linux-windows-10
Go to Windows store and get Ubuntu.
Install and set up local user + password – NOTE IT DOWN
To open the ubuntu. Either search for “ubuntu” or “wsl” in start menu.
Wsl – Windows Subsytem For Linux (Ubuntu)

To verify installed version:
    > lsb_release -a

## Update Linux
Open the wsl terminal from start menu. NOW ONWARDS ALWAYS THE WSL TERMINAL WILL BE USED.
> sudo apt update
> sudo apt upgrade
> sudo apt-get install -y build-essential libsasl2-dev python3-dev libldap2-dev libssl-dev libffi-dev libpq-dev python3-pip
> sudo apt-get install -y libmysqlclient-dev default-libmysqlclient-dev
OPTIONAL > sudo apt-get install -y redis-server
```

#### Python, Pip & Virtualenv

```
Check if python is installed
    > python3 –-version (should be 3.6 or greater)

# Install venv, python global dependencies.
> sudo pip3 install --upgrade virtualenv && \
	pip3 install --upgrade setuptools && \
	pip3 install --upgrade Cython

Refer to https://stackoverflow.com/questions/49943410/pip-ssl-error-on-windows
in case of errors.
USE THIS IN CASE OF ERROR > pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org <PACKAGE>
```

#### Export DISPLAY to your local machine

```
> sudo apt install xterm

# Configure wsl/ubuntu to use the local X server
# In bash run:
    > echo "export DISPLAY=localhost:0.0" >> ~/.bashrc
# To have the configuration changes take effect, restart bash, or run:
    > . ~/.bashrc

LINK - https://seanthegeek.net/234/graphical-linux-applications-bash-ubuntu-windows/

# Install and launch Xserver.
1. On Windows desktop, download and install VcXsrv server
2. Launch it and choose preferences – use multiple windows as we are not installing a Linux Desktop environment (a very time consuming and failure prone operation)
```

#### MYSQL 

```
> sudo apt install python3-dev libmysqlclient-dev default-libmysqlclient-dev
> sudo apt install python3-dev
> sudo apt-get install build-essential
> sudo apt-get install libssl-dev
> sudo apt-get install mysql-server
```

```
STARTING MYSQL

> sudo service mysql restart
> sudo /etc/init.d/mysql start

Create Database
1. Install MySQL-Workbench - Refer - https://dev.mysql.com/downloads/workbench/
2. Create new Database by an appropriate name example - 'main_db'

Connection Check
> mysql -h 127.0.0.1 -P 3306 -u root -p main_db
```

#### Pycharm

```
Download pycharm using the windows browser (download using the browser on the Linux subsystem is unlikely to succeed). 
This is available at: https://www.jetbrains.com/pycharm/download/?#section=linux
From your Ubuntu prompt, copy the downloaded file to the home directory

> cp /mnt/c/Users/<user-name>/Downloads/pycharm-community-2019.2.3.tar.gz /home/<user-name/
Hint - format of cp is – “cp source-file destination-file”

NOTE – this is now copied to the home/username folder
Unzip pycharm:
tar –xvf pycharm-community-2019.2.3.tar.gz
/home/username/pycharm-community-2019.2.3/bin/pycharm.sh &
```

## Getting the Repository

#### Install dependencies On the Pycharm/ubuntu Terminal console

```
It is recommended to create a directory by the name of project in your Windows Drive like E: or C: somewhere.

1. Navigate to the projectName directory
> git clone git-repo-url
> cd projectName
> mkdir venv && cd venv
> virtualenv –-python=python3 .
 If Error use this command -> python3 -m virtualenv
> source bin/activate
> cd ./../ (get back to projectName home directory)
> pip install prompt-toolkit==1.0.15
> pip install –r requirements.txt
```

#### Open Pycharm

```
/home/username/pycharm-community-2019.2.3/bin/pycharm.sh &
File> Open> choose folder projectName

Go to 'File'
	> Settings
	> Python Interpreter
	> Click on Hexagon Symbol
	> Show All
	> Click on + sign on the right vertical toolbar
	> Under Virtualenv Environment
	> Existing Environment
	> Choose Interpreter by selecting the path
	/mnt/……../projectName/venv/bin/python3.6

Rename the venv – Give it an appropriate name like project-name-venv.
Apply, Save etc.
pycharm will begin indexing the folders.
```

### Run these commands, with the venv activated.

```
> python3 manage.py migrate
> python3 manage.py createadmin
```