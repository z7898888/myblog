#!/usr/bin/env python
#coding:utf-8

from ToyToolkit.myweb import ctx;
from models import Blog,User;
from datetime import datetime;
from itertools import groupby;

def utc2yymm( blog ):
	dt = datetime.fromtimestamp( blog.created_at );
	return dt.strftime('%Y.%m.%d');

def count_group_by_date( blogs ):
	return [m+' (%d)'%len(list(n)) for m,n in groupby(blogs, key=utc2yymm)];
