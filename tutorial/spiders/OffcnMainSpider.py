#!/usr/bin/python
# -*- coding: UTF-8 -*-
#create by WayneLiu -- 17.2.28

import scrapy
from tutorial.items import CategoryItem
from tutorial.items import DetailClassItem


from lxml import etree
import lxml.html as HTML 

from scrapy.http import Request, FormRequest
from scrapy.contrib.spiders import CrawlSpider, Rule
import string  
import urlparse
import httplib, urllib2

from twisted.enterprise import adbapi
import MySQLdb	
import MySQLdb.cursors
from scrapy.crawler import Settings as settings

import json
import sys,re,time
reload(sys)
sys.setdefaultencoding('utf-8')


######################################
#######获得课程分类和课程信息############
######################################
class OffcnSpider(scrapy.Spider):
	name = "offcn"
	# allowed_domains = ["19.offcn.com"]
	start_urls = ["http://19.offcn.com/"]
	global_list = []
	dbpool = ''
	file = open('brief.json', 'wb')

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

##############默认回调##############
	def parse(self, response):
		items = CategoryDictItem()

		self.get_all_category(response,items)

		cateList = items['tempDict']
	  	for item in cateList:
			link = item['link']
			title = item['title']
			print 'the link is: ' , link
			link = link.decode("utf-8")
			yield Request(url=link, meta={'title': title}, callback=self.detail_next_list)		

		##############交给pipelines来处理这些实体信息##############
		cateItem = items['tempDict']
		for item in cateItem:
			yield item


		
##############递归查询是否存在下一页##############（这里遇见了scrapy的因为yield使用的坑，导致只能换种方式处理）
	def detail_next_list(self,response):
		category = response.meta['title']
		url = response.url
		print url.decode("utf-8"),'jjjjj'
		url = url.decode("utf-8")
		nextpageUrl = response.xpath('//div[@class="zg_page"]/a[last()-1]/@href').extract()
		nextpageDiv = response.xpath('//div[@class="zg_page"]/a[last()-1]/text()').extract()
		
		nextp = u'下一页'
		nextpageDiv = nextpageDiv[0]
		self.log('===============detail_chinese: |%s|  ' % nextpageDiv)
		self.detail_class_list(response)

		##如果有下一页，继续
		if nextpageDiv == u'\u4e0b\u4e00\u9875' and nextpageUrl:
			nextpageUrl = nextpageUrl[0]
			if nextpageUrl.startswith('http://19.offcn.com'):
				pass
			else: 
				nextpageUrl = "http://19.offcn.com"+nextpageUrl
			self.log('next_page_url: %s' % nextpageUrl)
			
			yield Request(nextpageUrl, meta={'title': category}, callback=self.detail_next_list)
			# yield Request(nextpageUrl, meta={'title': category}, callback=self.detail_class_list)



#############每一页的课程简介的解析#########
	def detail_class_list(self,response):
		category = response.meta['title']

		self.log('single_page_title %s' % category)
		
		
		categoryMainDivs = response.xpath('//div[@class="offcnkclbmain_right_3"]')
		aClass = categoryMainDivs.xpath('.//div[@class]/ul').extract()
		
		for p in aClass:
			p = etree.HTML(p)
			meta = {}
			# yield item
			link = p.xpath('.//li[@class = "bt"]/a/@href')[0]
			meta['title']= p.xpath('.//li[@class = "bt"]/a/text()')[0]
			meta['classhour'] = p.xpath('.//li/span[1]/text()')[0]
			meta['image'] = p.xpath('.//li/a/img/@src')[0]
			meta['price']= p.xpath('.//li/span[2]/text()')[0]
			meta['category'] = category
			
			if link.startswith('http://19.offcn.com'):
				pass
			else: 
				link = "http://19.offcn.com"+link
			meta['link'] = link
			# print title
			# conn = httplib.HTTPConnection('http://19.offcn.com:80')
			# conn.request("GET",link)
			# response = conn.getresponse()
			req = urllib2.Request(link) 
			resp = urllib2.urlopen(req)  
			self.get_detail_class_info(resp,meta)
			# print Request(url=link, meta={'title': title,'classhour':classhour}, callback=self.get_detail_class_info)

##############进入获取每个课程的详细页面，以便存数据库#############
	def get_detail_class_info(self,response,meta):
		data = response.read()
		# htree = HTML.fromstring(data) 
		htree = etree.HTML(data)
			
		item = DetailClassItem()
		item['image'] = meta['image']
		item['link'] = meta['link']
		item['title'] = meta['title']
		item['classhour'] = meta['classhour']
		item['price']= meta['price']
		item['category'] = meta['category']
		item['validtime'] = htree.xpath('//div[@class="zbCz"]/dl[@class="zbCz_left"]/dd/span[last()]/text()')[0]
		item['suitable'] = htree.xpath('//div[@class="zbCz"]/dl[@class="zbCz_right"]/dd/font/text()')
		# print item['suitable']
		features = htree.xpath('//div[@class="zbCz"]/div[@class="zbCz_box"]/span/text()')
		# print features,'aasswwdddcccfvfdfsfsdsv'
		result = []
		a = '###'
		for feature in features:
			result.append(feature)
		# print a.join(result)
		# print a
		item['feature'] = a.join(result)

		###存数据库
		self.dbpool.runInteraction(self.insert_into_tables,item)
		###存json
		line = json.dumps(dict(item)) + "\n"
		# print line
		self.file.write(line)
		




########### 获取需要的课程的类别 ###########
	def get_all_category(self,response,cateDictItem):
		categoryList = []

		categoryMainDivs = response.xpath('//div[re:test(@class, "zg17_kclb fl")]')
		
		fl = categoryMainDivs.xpath('.//dl[@class="fl"]').extract()
		fr = categoryMainDivs.xpath('.//dl[@class="fr"]').extract()
		# print fl  , "llll"
		#####主要的类别
		for l in fl:
			# print l
			l = etree.HTML(l)
			# print l,"ddd"
			item = CategoryItem()
			item['image'] = l.xpath('.//dt/img/@src')[0]
			item['title'] = l.xpath('.//dd/text()')[0]
			item['link'] = l.xpath('.//dd[@*]/a/@href')[0]

			categoryList.append(item)
			
		for r in fr:
			r = etree.HTML(r)
			item = CategoryItem()
			item['image'] = r.xpath('.//dt/img/@src')[0]
			item['title'] = r.xpath('.//dd/text()')[0]
			item['link'] = r.xpath('.//dd[@*]/a/@href')[0]
			categoryList.append(item)
			

		categoryOtherDivs = response.xpath('//div[re:test(@class, "zg17_kclb_link01 back")]')
		aClass = categoryOtherDivs.xpath('./a').extract()
		for p in aClass:
			
			p = etree.HTML(p)
			# print p.xpath('..//text()')
			item = CategoryItem()
			item['image'] = ['null'][0]
			item['title'] = p.xpath('..//text()')[0]
			item['link'] = p.xpath('.//@href')[0]
			categoryList.append(item)

			
################单独提出"免费公开课"这个分类#########
		item = CategoryItem()
		item['image'] = ['null'][0]
		item['title'] = [u'免费公开课'][0]
		item['link'] = ['http://19.offcn.com/list/?price=2'][0]
		categoryList.append(item)
		cateDictItem['tempDict'] = categoryList
		# for category in categoryList:
		# 	item = CategoryItem()
		# 	item = category
		# 	return item

		# itemDict = CategoryDictItem()
		# itemDict['tempDict'] = categoryList
		# print itemDict,'dgdgdgdg'


########想尝试在spider关闭的时候进行数据存储，以失败告终#######
	# def closed(self,reason):
	# 	# print self.global_list
	# 	for briefItem in self.global_list:
	# 		yield briefItem


################插入数据库############	
	def insert_into_tables(self,conn,item):
		print 'no1',self.trans(item['category'])
		conn.execute('select id from category where name="%s"' %(item['category']))
		# categoryd = conn.execute('select id from class_info where id = 55 ')


		#########这里由于查询成功后,sql本应该直接返回数据，但是这里是始终返回1
		#########折腾后才发现python的mysqldb库需要添加如下代码才能成功返回
		categoryId = conn.fetchone()['id']
		print 'no2',categoryId

		# conn.execute('insert into class_info(title,category_id) values("%s","%d")' %(item['title'],categoryId))
		conn.execute('insert into class_info(title,image,feature,validtime,classhour,price,category_id) values("%s","%s","%s","%s","%s","%s","%d")' %(item['title'],item['image'],item['feature'],item['validtime'],item['classhour'],item['price'],categoryId))
		# conn.execute('insert into class_detail(round_name) values("%s")' %('中文'))
		print 'yes'

#################转换编码###################
	def trans(self,item):
		if isinstance(item, unicode):
			return item.encode('utf-8')
		else:
			return item




