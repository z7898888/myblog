#!/usr/bin/env python
#coding:utf-8

from db import DBEngine;

class ModelMetaclass( type ):
	def __new__(cls, name, bases, attrs):
		if name != 'TableModel':
			
			mappings = dict();
			for k,v in attrs.items():
				if isinstance(v, FieldModel):
					mappings[k] = v;
			for k in mappings.keys():
				attrs.pop(k);

			if '__table__' not in attrs.keys():
				attrs['__table__'] = name;
			attrs['__mappings__'] = mappings;
		return type.__new__(cls, name, bases, attrs);

class FieldModel:
	def __init__(self, 
			fieldName, fieldType, 
			primaryKey = False,
			notNull = False,
			unique = False,
			**kargs):
		self._name = fieldName;
		self._type = fieldType;
		self._pk = primaryKey;
		self._nn = notNull;
		self._uq = unique;
		constrain = '%s %s %s'%(
				'primary key' if self._pk else '',
				'not null' if self._nn else '',
				'unique' if self._uq else '');
		self._constrain = constrain.strip();

	def fieldString(self):
		return "%s %s %s"%(self._name, self._type, self._constrain);

	def fieldName(self):
		return self._name;

class TableModel( dict ):
	__metaclass__ = ModelMetaclass;

	def __init__(self, **kw):
		super(TableModel, self).__init__(**kw);

	def __getattr__(self, key):
		try:
			return self[key];
		except KeyError:
			raise AttributeError(r"不存在 %s 属性"%key);
	
	def __setattr__(self, key, value):
		self[key] = value;

	@classmethod
	def create( cls ):
		fields = ','.join(
				(fd.fieldString() for fd in cls.__mappings__.values()));
		sql = 'create table %s(%s));'%(cls.__table__,fields);
		return sql;

	@classmethod
	def drop( cls ):
		sql = 'drop table %s if exsits table %s;'%(
				cls.__table__, cls.__table__);
		return sql;

	def insert( self ):
		field_list = [fd.fieldName() for fd in self.__mappings__.values()];
		fields = ','.join( field_list );
		params = ','.join( ('?' for i in field_list) );
		values = [ getattr(self, field, None) for field in field_list];
		sql = 'insert into %s(%s) values(%s);'%(
				self.__table__, fields, params);
		print values;
		return sql;
	
	def delete( self ):
		pass;

	def update( self ):
		pass;

	def select( self ):
		pass;

if __name__ == '__main__':
	class User( TableModel ):
		__table__ = 'UserInfo';
		id = FieldModel('id', 'char(50)', primaryKey=True);
		passwd = FieldModel('passwd', 'char(100)');
	print User.create();
	print User.drop();
	user = User();
	user.id = 123;
	print user.insert();
