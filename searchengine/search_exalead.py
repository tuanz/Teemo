# !/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bit4'
__github__ = 'https://github.com/bit4woo'

import requests
from lib import myparser
from lib.log import logger
import re
import time


class search_exalead:

    def __init__(self, word, limit,useragent,proxy=None):
        self.engine_name = "Exalead"
        self.word = word
        self.files = "pdf"
        self.results = ""
        self.totalresults = ""
        self.server = "www.exalead.com"
        self.userAgent = useragent
        self.headers = {'User-agent':useragent,'Referer':"http://{0}/search/web/results/?q={1}".format(self.server,self.word)}
        self.limit = int(limit)
        self.counter = 0
        self.proxies = proxy
        self.print_banner()
        return

    def print_banner(self):
        logger.info("Searching now in {0}..".format(self.engine_name))
        return

    def do_search(self):
        try:
            url = "http://{0}/search/web/results/?q={1}&elements_per_page=50&start_index={2}".format(self.server,self.word,self.counter)# 这里的pn参数是条目数
        except Exception, e:
            logger.error(e)
        try:
            r = requests.get(url, headers = self.headers, proxies = self.proxies)
            self.results = r.content
            self.totalresults += self.results
        except Exception,e:
            logger.error(e)

    def do_search_files(self):
        try:
            url = "http://{0}/search/web/results/?q={1}filetype:{2}&elements_per_page=50&start_index={3}".format(self.server,self.word,self.files,self.counter)# 这里的pn参数是条目数
        except Exception, e:
            logger.error(e)
        try:
            r = requests.get(url, headers = self.headers, proxies = self.proxies)
            self.results = r.content
            self.totalresults += self.results
        except Exception,e:
            logger.error(e)

    def check_next(self): #for search file
        renext = re.compile('topNextUrl')
        nextres = renext.findall(self.results)
        if nextres != []:
            nexty = "1"
            #print str(self.counter)
        else:
            nexty = "0"
        return nexty

    def get_emails(self):
        rawres = myparser.parser(self.totalresults, self.word)
        return rawres.emails()

    def get_hostnames(self):
        rawres = myparser.parser(self.totalresults, self.word)
        return rawres.hostnames()

    def get_files(self):
        rawres = myparser.parser(self.totalresults, self.word)
        return rawres.fileurls(self.files)

    def process(self):
        while self.counter <= self.limit:
            self.do_search()
            self.counter += 50
            #print "\tSearching " + str(self.counter) + " results..."

    def process_files(self):
        while self.counter < self.limit:
            self.do_search_files(self.files)
            time.sleep(1)
            more = self.check_next()
            if more == "1":
                self.counter += 50
            else:
                break
    def run(self): # define this function,use for threading, define here or define in child-class both should be OK
        self.process()
        self.d = self.get_hostnames()
        self.e = self.get_emails()
        logger.info("{0} found {1} domain(s) and {2} email(s)".format(self.engine_name,len(self.d),len(self.e)))
        return self.d, self.e

if __name__ == "__main__":
        print "[-] Searching in exalead:"
        useragent = "Mozilla/5.0 (Windows; U; Windows NT 6.0;en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6" #他会检查useragent，之前多了一个( 导致504
        proxy = {"http": "http://127.0.0.1:8080"}
        search = search_exalead("meizu.com", 100, useragent)
        search.process()
        all_emails = search.get_emails()
        all_hosts = search.get_hostnames()
        print all_emails
        print all_hosts  # blocked