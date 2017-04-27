#!/usr/bin/env python
#coding:utf-8

import MySQLdb as db;

class DBError(StandardError):
	pass;

class DBEngine:
	def connect(self):
		self.db = db.connect(
				host='localhost',user='admin',passwd='123abc',db='myblog');
		self.cur = self.db.cursor();
	
	def close(self):
		if hasattr(self,'cur'):
			self.cur.close();
			del self.cur;
	
	def execute(self, cmd_str):
		if hasattr(self,'cur'):
			try:
				return self.cur.execute(cmd_str);
			except Exception, e:
				raise DBError(e);

	def fetch(self):
		if hasattr(self,'cur'):
			try:
				ret = self.cur.fetchone();
				if ret!=None: yield ret;
			except Exception,e:
				raise DBError(e);

if __name__ == '__main__':
	engine = DBEngine();
	engine.connect();
	n = engine.execute('select * from users');
	print '受影响的行数:%d'%n;
	for u in engine.fetch():
		print u;
	engine.close();
