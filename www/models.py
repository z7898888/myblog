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

	def createAllTables():
		User.create();
		Blog.create();

	def insertTestData():
		user = User( id = uuid.uuid1(), name='dean', created_at = time.time(), passwd='888888', role='Admin');

		title = 'TestBlog';
		content = summary = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.";
		created_at = time.time();
		user_id = user.id;

		blog = Blog(id = uuid.uuid1(), title=title, summary=summary, content=content, created_at = created_at, user_id = user_id);

		user.insert();
		blog.insert();
		blog.title = 'Some Thing New';
		blog.id = uuid.uuid1();
		blog.insert();
		blog.id = uuid.uuid1();
		blog.title = '生命与和平相爱';
		blog.insert();

	dropAllTables();
	createAllTables();
	insertTestData();

if __name__ == '__main__':
	import logging, uuid, time;
	logging.basicConfig( level = logging.INFO );

	__ResetDataTable();
