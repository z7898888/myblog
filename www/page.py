#!/usr/bin/env python
#coding:utf-8

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

