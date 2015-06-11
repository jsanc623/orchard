
When doing pip install -r requirements.txt, you might get an error as 
described in http://stackoverflow.com/questions/5178292/pip-install-m
ysql-python-fails-with-environmenterror-mysql-config-not-found

The below helps to fix that error: 
	easy_install mysql-python (mix os)
	pip install mysql-python (mix os)
	apt-get install python-mysqldb (Linux Ubuntu, ...)
	cd /usr/ports/databases/py-MySQLdb && make install clean (FreeBSD)
	yum install MySQL-python (Linux Fedora, CentOS ...)

The requirements in the requirements.txt file are required for the project. 

To run:

Modify the conf/development.conf file to match your MySQL parameters. The other
config you shouldn't need to modify. After that, you should be able to just run
the run.sh file to get an instance running on 0.0.0.0 (modify run.sh or 
run TheOrchard.py with the needed flags. 

If you don't have MySQL, the program is coded to run with sqlite as well if 
its able to create an in-memory instance of such. 
