#!/usr/bin/env python
#coding:utf-8

import MySQLdb as db;
import threading;

class DBError(StandardError):
	pass;

class DBEngine:
	def __init__(self):
		self.is_connect = False;

	def connect(self):
		try:
			if not self.is_connect:
				self.db = db.connect(
				host='localhost',user='admin',passwd='123abc',db='myblog');
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
	def __enter__(self):
		self.db = DBEngine();
		self.db.connect();
		return self.db;

	def __exit__(self, excyte, excvalue, traceback):
		self.db.execute('commit');
		self.db.close();

_db_ctx = _DBCtx();

def connectDB():
	return _db_ctx;

if __name__ == '__main__':
	engine = DBEngine();
	engine.connect();

	n = engine.execute('select * from users;');
	print '影响 %d'%n;
	for u in engine.fetch():
		print u;
	
	n = engine.execute('show databases;');
	print '影响 %d'%n;
	for u in engine.fetch():
		print u;

	engine.close();

	with connectDB() as db:
		n = db.execute('show tables;');
		print '影响 %d'%n;
		for u in db.fetch():
			print u;
		raw_input();

