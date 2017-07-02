#!/usr/bin/env python
#coding:utf-8

from ToyToolkit.myweb import ctx;
from models import Blog;
import datetime,time;

class Page( object ):
	def __init__(self, item_count, page_index=1, page_size=10):
		if not isinstance(page_index, (long,int)): page_index = 1;
		if not isinstance(page_size, (long,int)): page_size = 3;
		self.item_count = item_count;
		self.page_size = page_size;
		self.page_count = item_count // page_size + (
			1 if item_count % page_size > 0 else 0);
		if (item_count == 0) or (page_index < 1) or (page_index > self.page_count):
			self.offset = 0;
			self.limit = self.page_size;
			self.page_index = 1;
		else:
			self.page_index = page_index;
			self.offset = self.page_size * (page_index - 1);
			self.limit = self.page_size;
		self.has_next = self.page_index < self.page_count;
		self.has_previous = self.page_index > 1;

	def obj2dict(self):
		return {
			'has_next': self.has_next,
			'page_index': self.page_index,
			'page_count': self.page_count,
			'has_previous': self.has_previous,
			'item_count': self.item_count
		};

def datetime_filter( t ):
	delta = int(time.time() - t)
	if delta < 60:
		return u'刚刚';
	if delta < 3600:
		return u'%s分钟前'%(delta // 60);
	if delta < 86400:
		return u'%s小时前'%(delta //3600);
	if delta < 604800:
		return u'%s天前'%(delta // 86400);
	dt = datetime.datetime.fromtimestamp( t );
	return dt.strftime('%Y-%m-%d %H:%M');

def _get_page_args( field ):
	ret = ctx.request.get( field );
	if isinstance(ret, unicode):
		return int(ret);

def get_blogs_by_page():
	total = Blog.count_all();
	index = _get_page_args('page_index');
	size = _get_page_args('page_size');
	page = Page(total, index, size);
	blogs = Blog.select('order by created_at desc limit %s,%s',page.offset,page.limit);
	return blogs, page;
