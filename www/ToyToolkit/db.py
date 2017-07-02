#!/usr/bin/env python
#coding:utf-8

import MySQLdb as db;
import threading;

class DBError(StandardError):
	pass;

class DBEngine:
	def __init__(self, user, passwd, dbname, host, port):
		self.is_connect = False;
		self._config = dict(user=user, passwd=passwd,db=dbname,
				host=host, port = port);

	def connect(self):
		try:
			if not self.is_connect:
				self.db = db.connect( **self._config );
				self.cur = self.db.cursor();
				self.is_connect = True;
		except Exception,e:
			raise DBError(e);
	
	def close(self):
		if hasattr(self,'cur'):
			self.cur.close();
			self.db.close();
			del self.cur;
			del self.db;
			self.is_connect = False;
	
	def execute(self, cmd_str, *args):
		if hasattr(self,'cur'):
			try:
				return self.cur.execute(cmd_str, *args);
			except Exception, e:
				raise DBError(e);

	def fetch(self):
		if hasattr(self,'cur'):
			try:
				ret = self.cur.fetchone();
				while ret:
					yield ret;
					ret = self.cur.fetchone();
			except Exception,e:
				raise DBError(e);

class _DBCtx(threading.local):
	def __init__(self, **config):
		super(_DBCtx, self).__init__();
		self._config = config;

	def __enter__(self):
		self.db = DBEngine(**self._config);
		self.db.connect();
		return self.db;

	def __exit__(self, excyte, excvalue, traceback):
		self.db.execute('commit');
		self.db.close();

_db_ctx = None;

def connectDB():
	"""
	返回数据库上下文信息

	>>> connectDB();
	Traceback (most recent call last):
		...
	DBError: 请先调用 createDBEngine 配置上下文
	"""
	if _db_ctx is None:
		raise DBError('请先调用 createDBEngine 配置上下文');
	return _db_ctx;

def createDBEngine(user, passwd, database, host, port=3306, **kw):
	"""
	根据配置文件产生数据库上下文

	>>> createDBEngine(user='admin', passwd='123abc', database='myblog', host='localhost');
	>>> n = None; rcds = None;
	>>> with connectDB() as db:
	...		n = db.execute('select * from users');
	...		rcds = [r for r in db.fetch()];
	>>> print n;
	2
	"""
	global _db_ctx;
	config = dict(user=user, passwd=passwd, dbname=database,
			host=host, port=port);
	_db_ctx = _DBCtx( **config );

if __name__ == '__main__':
	import doctest;
	doctest.testmod();
