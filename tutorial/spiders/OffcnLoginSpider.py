#!/usr/bin/python
# -*- coding: utf-8 -*-
#create by WayneLiu -- 17.2.28


import scrapy
from tutorial.items import RoundClassItem
from lxml import etree
import lxml.html as HTML 
from lxml import html

from scrapy.http import Request, FormRequest
from scrapy.contrib.spiders import CrawlSpider, Rule
import string  
import urlparse
import httplib, urllib2,urllib,cookielib


from twisted.enterprise import adbapi
import MySQLdb	
import MySQLdb.cursors
from scrapy.crawler import Settings as settings
import chardet

import requests
import json
import sys,re,time
reload(sys)
sys.setdefaultencoding('utf-8')



######################################
#######登录获得每门课的具体课程链接#######
######################################
class OffcnLoginSpider(scrapy.Spider):
    name = "offcnlogin"    
    start_urls = ["http://19.offcn.com/"]
    sessions = requests.Session()
    cookiess = ''
    post_data = {
                        'isecode': '0',
                        'username': 'username',
                        'password': 'passwprd',
                        'secode':''
                    }
    global_login_url = "http://19.offcn.com/foreusertest/dologin/type/10/?callback=jQuery18003350482142741218_1488801165901"

###########报名课程的header#######
    headers = {
    'Accept':'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Content-Length':'13',
    'Cookie':'PHPSESSID=75jq7dco46hf0d6a2k8feuls47; LXB_REFER=www.google.com.sg; Hm_lvt_a6adf98bf5f7dd3d72872cf8b3535543=1488103070; Hm_lpvt_a6adf98bf5f7dd3d72872cf8b3535543=1488794513; WT_FPC=id=2f9ce88449b67825a231488103069449:lv=1488794513432:ss=1488794510010; Hm_lvt_de8aa024be8a8fbf01e3648863964000=1488103070; Hm_lpvt_de8aa024be8a8fbf01e3648863964000=1488794514',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest'
    }
########跳转到报名后的302之前的页面的header##########
    getHeaders = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cookie':'PHPSESSID=75jq7dco46hf0d6a2k8feuls47; LXB_REFER=www.google.com.sg; WT_FPC=id=2f9ce88449b67825a231488103069449:lv=1488804049543:ss=1488798990396; Hm_lvt_a6adf98bf5f7dd3d72872cf8b3535543=1488103070; Hm_lpvt_a6adf98bf5f7dd3d72872cf8b3535543=1488804050; Hm_lvt_de8aa024be8a8fbf01e3648863964000=1488103070; Hm_lpvt_de8aa024be8a8fbf01e3648863964000=1488804050',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }


    dbpool = ''
    #数据库
    dbargs = dict(
        host = 'localhost' ,
        db = 'education_system',
        user = 'root', #replace with you user name
        passwd = 'audi', # replace with you password
        charset = 'utf8',
        cursorclass = MySQLdb.cursors.DictCursor,
        use_unicode = True,
        )    
    dbpool = adbapi.ConnectionPool('MySQLdb',**dbargs)


########初始请求##########
    def start_requests(self):
        return [Request(self.global_login_url, callback = self.post_login)]  #添加了meta


    def post_login(self,response):
        data = self.postRequest(response.url,self.post_data)
        self.after_login(data)

########免费的课程才去报名##########
    def after_login(self,response):
        tweets = []
        for line in open('brief_info.json', 'r'):
            tweets.append(json.loads(line))
        for item in tweets:
            linkUrl = item['link']
            title = item['title']
            price = item['price']
            if price==u'免费':
                # self.getRequestWithCookie(linkUrl)
                url = self.do_baoming(linkUrl)
                print url,"122211122"
                data_baoming = self.getRequestWithCookie(url)
                self.doParse(data_baoming)

  

########报名----func，报名后强跳到报名后的页面##########
    def do_baoming(self,url):
        splitUrl = url
        courseid = splitUrl.split('/')[-2]
        ##先发送请求报名
        print courseid,'dddd'
        post_data={'courseId':str(courseid)}
        # return_data=requests.post(response.url,data=post_data)
        postUrl = 'http://19.offcn.com/shopcart/submitorderszero/'

        data = self.postRequestWithCookie(postUrl,post_data)
        # ##再到报名后的页面
        time.sleep(1)
        url = url.replace("courseinfo", "courseinfo2")
        return url

########解析报名成功后的页面的数据##########
    def doParse(self,data):

        # body > div.newStudy > div.newS_center > p.newS_a > span
        # htree = HTML.fromstring(data)
        htree = html.fromstring(data)
        className = htree.xpath('//span[@class="newS_tit"]/text()')
        if className:
            className = className[0]

        hostDiv = htree.xpath('//div[@class="kcjs_kejian"]/dl')
        item = RoundClassItem()
        for single in hostDiv:
            # print single[0]
            singleDiv = single.xpath('./dd')[0]
            item['whichClass'] = singleDiv.xpath('.//em/text()')[0]
            pageUrl = singleDiv.xpath('.//a/@href')[0]
            if pageUrl.startswith('http://19.offcn.com'):
                pass
            else: 
                pageUrl = "http://19.offcn.com"+pageUrl
            item['classHref'] = pageUrl
            item['roundTitle'] = (singleDiv.xpath('.//a/text()')[0]).strip()
            item['className'] = className
            ###存数据库
            self.dbpool.runInteraction(self.insert__into_table,item)





#######插入数据库#########   
    def insert__into_table(self,conn,item):
        
        wclass = item['whichClass']
        chref = item['classHref']
        rtitle = item['roundTitle']
        # print 'yes',wclass
        conn.execute('select id from class_info where title="%s"' %(item['className']))
        if conn.fetchone().has_key('id'):
            categoryId = conn.fetchone()['id'] 
        else:
            categoryId = -1
        # print 'no',categoryId
        
        # conn.execute("SET NAMES utf8");
        # conn.commit();
        conn.execute('insert into class_detail(round_name,round_url,title,detail_info_id) values("%s","%s","%s","%s")' %(wclass,chref,rtitle,categoryId))

        # conn.execute('insert into class_detail(detail_info_id) values("%s")' %(12))
        print 'wywyw'


    def trans(self,item):
        if isinstance(item, str):
            return 'str'#item.decode('utf-8')

        if isinstance(item, unicode):
            # return 'zhongwen'
            return item.encode("utf-8")
        # else:
        





########post方法##########
    def postRequest(self,url,data):
        # request = requests.post("url", data=data)
        r = self.sessions.post(url, data=data)   #cookie保留在s中
        # r = s.get("http://httpbin.org/cookies") #再次访问时会保留cookie
        print r.text,'kkkk'


########报名后带cookie的方法##########
    def getRequestWithCookie(self,url):
        # x = requests.Session()
        # t = x.post(self.global_login_url,data=self.post_data)
        # print t.text
        r = self.sessions.get(url=url,cookies=self.cookiess,headers=self.getHeaders) 
        print url,'gggggg',r.url
        return r.content

########报名的post##########
    def postRequestWithCookie(self,url, data):
        # self.sessions = requests.Session()
              
        r = self.sessions.post(url, data=data,headers=self.headers)   #cookie保留在s中
        self.cookiess = r.cookies
        # print r.text,'ppppppp'
        return r.text



######使用Python原生urllib2做的带cookie请求######
    def post(self,url,data):  
        req = urllib2.Request(url)  
        data = urllib.urlencode(data) 
        #enable cookie  
        cookiefile = "cookiefile.txt"  
        cookieJar = cookielib.MozillaCookieJar(cookiefile)  
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
        # response = opener.open(req, data)  
           
        # #enable cookie  
        # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor()) 
        response = opener.open(url, data)  
        cookieJar.save(ignore_discard=True, ignore_expires=True)
        return response.read()  
    def getWithCookie(self,url):
        req = urllib2.Request(url)  
        # data = urllib.urlencode(data)  
        #second http request use cookie  
        cookieJar = cookielib.MozillaCookieJar()  
        cookieJar.load("cookiefile.txt")  
        # url = "http://www.xiami.com"  
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))  
        response = opener.open(req)
        return response.read()
        # print response.read()  
    def postWithCookie(self,url, data):  
        req = urllib2.Request(url)  
        data = urllib.urlencode(data)  
        #second http request use cookie  
        cookieJar = cookielib.MozillaCookieJar()  
        cookieJar.load("cookiefile.txt")   
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))  


        response = opener.open(url,data)
        # cookieJar.save(ignore_discard=True, ignore_expires=True)
        # print response.read()  
        return response.read()   




