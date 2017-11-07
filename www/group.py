#!/usr/bin/env python
#coding:utf-8

from ToyToolkit.myweb import ctx;
from models import Blog,User,Catelog;
from datetime import datetime;
from itertools import groupby;
from page import Page;
import time;

def utc2yymm( blog ):
	dt = datetime.fromtimestamp( blog.created_at );
	return dt.strftime('%Y-%m-%d');

def count_group_by_date( blogs ):
	return [(m,len(list(n))) for m,n in groupby(blogs, key=utc2yymm)];

def get_author_info( id ):
	author = User.get_one(id = id);
	blogs = Blog.select('where user_id=%s order by created_at desc',id);
	author.groups_date = count_group_by_date( blogs );
	author.groups_cate = Catelog.select('where user_id=%s and parent_id is NULL',id);
	return author;

def _getCataPath( cataid, cataset):
	for cata in cataset:
		if cata.id == cataid:
			catainfo = (cata.id, cata.name);
			if cata.parent_id != None:
				return _getCataPath( 
					cata.parent_id, cataset)+[catainfo];
			else:
				return [catainfo];
	return [];

def get_blogs( userid , cataid = None):
	if cataid != None:
		blogs = Blog.select(
			'where find_in_set(catalog_id, queryChild(%s))',cataid);
	else:
		blogs = Blog.select(
			'where user_id=%s order by created_at desc',userid);
	return blogs;

def get_blogs_cata( blogs ):
	catalogs = Catelog.get_all();
	
	for bg in blogs:
		bg.cata_path = _getCataPath(bg.catalog_id, catalogs);
	return blogs;


def get_blogs_info( blogs , date ):
	if date == None:
		return blogs;
	groups = groupby( blogs, key=utc2yymm );
	ret = [];
	for bgs in [list(n) for m,n in groups if m==date]:
		ret.extend( bgs );
	return ret;

def df1( t ):
	delta = int(time.time() - t)
	if delta < 60:
		return u'刚刚';
	if delta < 3600:
		return u'%s分钟前'%(delta // 60);
	if delta < 86400:
		return u'%s小时前'%(delta // 3600);
	if delta < 604800:
		return u'%s天前'%(delta // 86400);
	dt = datetime.fromtimestamp( t );
	return dt.strftime('%Y-%m-%d %H:%M');

def df2( t ):
	return datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M');	

def _get_page_args( field ):
	ret = ctx.request.get( field );
	if isinstance(ret, unicode):
		return int(ret);

def get_blogs_and_page( id=None , date=None, cata=None ,key=None):
	blogs = get_blogs( id , cata);
	blogs = get_blogs_cata( blogs );
	if date != None:
		blogs = get_blogs_info( blogs , date );
	total = len(blogs);
	index = _get_page_args('page_index');
	size = _get_page_args('page_size');
	page = Page(total, index, size);
	blogs = blogs[ page.offset : page.offset + page.limit ];
	return date_filter(blogs,key), page;

def date_filter( blogs, key = None):
	if key:
		for blog in blogs:
			blog.created_at = key(blog.created_at);
	return blogs;
