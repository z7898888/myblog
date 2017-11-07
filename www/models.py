#!/usr/bin/env python
#coding:utf-8

from ToyToolkit.myorm import TableModel, FieldModel;
from ToyToolkit.db import createDBEngine;

class User( TableModel ):
	__table__ = 'users';
	id = FieldModel('id', 'varchar(100)', primaryKey = True);
	name = FieldModel('name', 'varchar(100)',notNull=True, unique=True);
	passwd = FieldModel('password', 'varchar(100)');
	role = FieldModel('role', 'varchar(10)');

	created_at = FieldModel('created_at', 'double', notNull=True);

class Catelog( TableModel ):
	__table__ = 'catalogs';
	id = FieldModel('id', 'varchar(100)', primaryKey = True );
	name = FieldModel('name', 'varchar(100)', notNull = True );

	user_id = FieldModel('user_id', 'varchar(100)', foregionKey = True);
	parent_id = FieldModel('parent_id','varchar(100)');


class Blog( TableModel ):
	__table__ = 'blogs';
	id = FieldModel('id', 'varchar(100)', primaryKey = True);
	title = FieldModel('title', 'varchar(100)', notNull = True);
	summary = FieldModel('summary', 'varchar(200)', notNull = True);
	content = FieldModel('content', 'mediumtext', notNull = True);
	created_at = FieldModel('created_at', 'double', notNull = True);

	user_id = FieldModel('user_id', 'varchar(100)', foregionKey = True);
	catalog_id = FieldModel('catalog_id', 'varchar(100)',foregionKey=True);

def __ResetDataTable():
	createDBEngine(user='ppc', passwd='123456', database='myblog',host='localhost');

	def dropAllTables():
		User.drop();
		Blog.drop();
		Catelog.drop();

	def createAllTables():
		User.create();
		Blog.create();
		Catelog.create();

	def insertTestData():
		user = User( id = uuid.uuid1(), name='dean', created_at = time.time(), passwd='888888', role='Admin');

		user.insert();

		title = '白夜行';
		content = summary = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.";
		created_at = time.time();
		user_id = user.id;

		blog = Blog(id = uuid.uuid1(), title=title, summary=summary, content=content, created_at = created_at, user_id = user_id);
		
		catalog = Catelog(id = uuid.uuid1(), user_id = user_id);
		
		cpid = catalog.id;
		catalog.name = '读书';
		catalog.insert();
		catalog.id = uuid.uuid1();
		catalog.name = '东野圭吾';
		catalog.parent_id = cpid;
		catalog.insert();
		blog.catalog_id = catalog.id;
		blog.insert();
		
		blog.title = '嫌疑人x的献身';
		blog.id = uuid.uuid1();
		blog.catalog_id = catalog.id;
		blog.insert();
		
		catalog.id = uuid.uuid1();
		catalog.name = '阿加莎克里斯蒂';
		catalog.insert();
		catalog.parent_id = None;
		blog.id = uuid.uuid1();
		blog.title = '东方快车谋杀案';
		blog.catalog_id = catalog.id;
		blog.insert();

		catalog.id = uuid.uuid1();
		catalog.name = '感悟';
		catalog.insert();
		blog.id = uuid.uuid1();
		blog.title = '生命与和平相爱';
		blog.catalog_id = catalog.id;
		blog.insert();
		blog.catalog_id = None;


		user = User( id = uuid.uuid1(), name='sammy', created_at = time.time(), passwd='666666', role='Admin');
		blog.user_id = user.id;
		blog.id = uuid.uuid1();
		user.insert();
		blog.insert();

	dropAllTables();
	createAllTables();
	insertTestData();

if __name__ == '__main__':
	import logging, uuid, time;
	logging.basicConfig( level = logging.INFO );

	__ResetDataTable();
