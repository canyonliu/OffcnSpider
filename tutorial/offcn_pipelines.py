#!/usr/bin/python
# -*- coding: UTF-8 -*-
#create by WayneLiu -- 17.2.28

from twisted.enterprise import adbapi
import MySQLdb	
import MySQLdb.cursors
from scrapy.crawler import Settings as settings

import json
from scrapy.exceptions import DropItem

##########################
#######输出的实体对象#######
##########################
class CategoryPipeline(object):
	dbpool = ''

	def __init__(self):
		self.file = open('category.json', 'wb')
		####数据库连接池
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

	def process_item(self, item, spider):
		###存数据库
		res = self.dbpool.runInteraction(self.insert_into_table,item)
		###存json
		print '||||||||||||||||| CatagoryPipeline'
		line = json.dumps(dict(item)) + "\n"
		print line
		self.file.write(line)
		return item


	def insert_into_table(self,conn,item):

		conn.execute('insert into category(name,url,image) values(%s,%s,%s)',(self.trans(item['title']),self.trans(item['link']),self.trans(item['image'])))
		# print 'yes'

	def trans(self,item):
		if isinstance(item, unicode):
			return item.encode('utf-8')
		else:
			return item


# # class DetailClassInfoPipeline(object):
# 	"""docstring for ClassBrief"""
# 	dbpool = ''
# 	def __init__(self):
# 		self.file = open('detailclass.json', 'wb')
# 		dbargs = dict(
# 			host = 'localhost' ,
# 			db = 'education_system',
# 			user = 'root', #replace with you user name
# 			passwd = 'audi', # replace with you password
# 			charset = 'utf8',
# 			cursorclass = MySQLdb.cursors.DictCursor,
# 			use_unicode = True,
# 			)    
# 		dbpool = adbapi.ConnectionPool('MySQLdb',**dbargs)

# 	def process_item(self, item, spider):
# 		print'~~~~~~~~~~BriefInfoPipeline'

# 		###存数据库
# 		res = self.dbpool.runInteraction(self.insert_into_table,item)
# 		###存json

# 		line = json.dumps(dict(item)) + "\n"
# 		print line
# 		self.file.write(line)
# 		return item

# 	def insert_into_table(self,conn,item):
# 		categoryId = conn.execute('select id  from category where name = %s',self.trans(item['category']))
# 		print 'yes',categoryId
# 		conn.execute('insert into\
# 		 class_info(title,image,feature,validtime,classhour,price,category_id)\
# 		 values(%s,%s,%s,%s,%s,%s,%s)',\
# 		 (self.trans(item['title']),self.trans(item['image']),self.trans(item['feature']),self.trans(item['validtime']),\
# 		 	self.trans(item['classhour']),self.trans(item['price']),categoryId))
		

# 	def trans(self,item):
# 		if isinstance(item, unicode):
# 			return item.encode('utf-8')
# 		else:
# 			# return item

		
