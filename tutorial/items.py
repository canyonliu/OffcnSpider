# -*- coding: utf-8 -*-
#create by WaynneLiu -- 17.2.28
import scrapy


######################################
###########scrapy的实体文件############
######################################


####所有分类的实体#####
class CategoryItem(scrapy.Item):
	title = scrapy.Field()
	link = scrapy.Field()
	image = scrapy.Field()


####课程信息的实体#####
class DetailClassItem(scrapy.Item):
	# define the fields for your item here like:
	validtime = scrapy.Field()
	feature = scrapy.Field()
	title = scrapy.Field()
	suitable = scrapy.Field()
	image = scrapy.Field()
	classhour = scrapy.Field()
	price = scrapy.Field()
	category = scrapy.Field()
	learnUrl = scrapy.Field()
	link = scrapy.Field()


####报名后课程的每节课的实体#####
class RoundClassItem(scrapy.Item):
	# define the fields for your item here like:
	whichClass = scrapy.Field()
	classHref = scrapy.Field()
	roundTitle = scrapy.Field()
	className = scrapy.Field()

	
