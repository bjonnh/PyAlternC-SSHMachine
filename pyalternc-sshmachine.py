# A small script to open machines on an AlternC platform

import mechanize
import argparse
import cookielib
import re
import sys
import getpass

class AlternC:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        # Adapt these to your platform
        self.url_login = 'https://admin.lautre.net/admin/'
        self.url_vm_start = 'https://admin.lautre.net/admin/vm.php?action=start'
        self.url_vm_stop = 'https://admin.lautre.net/admin/vm.php?action=stop'
        self.url_logout = 'https://admin.lautre.net/admin/mem_logout.php'
        self.pattern_machine = re.compile('.*\>(.*vds\.lautre\.net).*')

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
            print ('The following error occured: \n"%s"' % e)
            print ('A good idea is to open a browser and see if you can log in from there.')
            print ('URL:', self.url)
            raw_input()
            exit()
        self.browser.submit()

    def logout(self):
        self.browser.open(self.url_logout)

    def open_machine(self):
        self.login()

        self.browser.open(self.url_vm_start)
        self.page = self.browser.response().read()

        print ("Machine : %s" % self.pattern_machine.findall(self.page))
        AC.logout()

    def close_machine(self):
        self.login()
        self.browser.open(self.url_vm_stop)
        AC.logout()

parser = argparse.ArgumentParser(description='Open and close virtual machines on AlternC platforms')

parser.add_argument('-u','--user',dest="user",required=True)
parser.add_argument('-m','--mode',help="open or close",choices=['open','close'],dest="mode",required=True)
parser.add_argument('-p','--password',dest="password")
args = parser.parse_args()

if (args.password is None):
    password = getpass.getpass()
else:
    password = args.password

AC = AlternC(args.user, password)
if args.mode == "open":
    AC.open_machine()
elif args.mode == "close":
    AC.close_machine()
