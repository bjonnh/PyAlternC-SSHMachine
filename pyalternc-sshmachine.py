#!/usr/bin/python
# A small script to open machines on an AlternC platform

import mechanize
import argparse
import cookielib
import re
import sys
import getpass

INTERACTIVE = False # Set to False to set password,user and server inside the script
Configuration_server = {'login':"https://admin.lautre.net/admin/", 'vm_start':"https://admin.lautre.net/admin/vm.php?action=start", 'vm_stop':"https://admin.lautre.net/admin/vm.php?action=stop", 'logout':"https://admin.lautre.net/admin/mem_logout.php", 'pattern_machine':".*\>(.*vds\.lautre\.net).*"}
Configuration_user = {'login':"foo",'password':"bar"}

class Connect_AlternC:
    def __init__(self, configuration,username, password,verbose):
        self.username = username
        self.password = password

        # Adapt these to your platform
        self.url_login = configuration['login']
        self.url_vm_start = configuration['vm_start']
        self.url_vm_stop = configuration['vm_stop']
        self.url_logout = configuration['logout']
        self.pattern_machine = re.compile(configuration['pattern_machine'])

        self.verbose = verbose
        self.browser = mechanize.Browser(factory=mechanize.RobustFactory())
        cj = cookielib.LWPCookieJar()
        self.browser.set_cookiejar(cj)

        self.browser.set_handle_equiv(True)

        self.browser.set_handle_redirect(True)
        self.browser.set_handle_referer(True)
        self.browser.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0
        self.browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    def login(self):
        self.browser.open(self.url_login)

        forms = self.browser.forms()

        self.browser.select_form(nr=0)
        
        try:
            self.browser.form['username'] = self.username
            self.browser.form['password'] = self.password
        except Exception as e:
            sys.stderr.write ('Error: \n"%s"' % e)
            sys.stderr.write ('Check if you can login from URL: %s' % self.url_login)
            exit(1)
        if self.verbose:
            print ("Login to %s" % self.url_login)
        self.browser.submit()
        login_error = re.search("User or password incorrect", self.browser.response().read())
        if login_error:
            sys.stderr.write ('Error: Login incorrect')
            exit(2)
    def logout(self):
        if self.verbose:
            print ("Logout")
        self.browser.open(self.url_logout)

    def open_machine(self):
        self.login()
        if self.verbose:
            print ("Opening machine")
        self.browser.open(self.url_vm_start)
        
        self.page = self.browser.response().read()
        Machine = self.pattern_machine.findall(self.page)
        if len(Machine)>0:
            print("%s\n" % Machine[0])
        AC.logout()

    def close_machine(self):
        self.login()
        if self.verbose:
            print ("Closing machine")
        self.browser.open(self.url_vm_stop)
        AC.logout()


parser = argparse.ArgumentParser(description='Open and close virtual machines on AlternC platforms')
parser.add_argument('-m','--mode',help="open or close",choices=['open','close'],dest="mode",required=True)
parser.add_argument('-v','--verbose',help="be more verbose",dest="verbose",action="store_true")
if INTERACTIVE == True:
    parser.add_argument('-u','--user',dest="user",required=True)   
    parser.add_argument('-p','--password',dest="password")
else:
    user = Configuration_user['login']
    password = Configuration_user['password']

args = parser.parse_args()

if INTERACTIVE == True:
    user = args.user
    if (args.password is None):
        password = getpass.getpass()
    else:
        password = args.password

AC = Connect_AlternC(Configuration_server,user, password,verbose=args.verbose)
if args.mode == "open":
    AC.open_machine()
elif args.mode == "close":
    AC.close_machine()
