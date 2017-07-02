#!/usr/bin/env python
#coding:utf-8

import logging;
from db import connectDB, DBError;

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
			attrs['__fields__'] = [
				(cfn,dfn.fieldName()) for cfn,dfn in mappings.items()];
			attrs['__pk__'] = [
				(cfn,dfn) for cfn,dfn in mappings.items() if dfn._pk];
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
		sql = 'create table %s(%s) engine=innodb default charset=utf8'%(cls.__table__,fields);
		return cls._execute(sql, False);

	@classmethod
	def drop( cls ):
		sql = 'drop table if exists %s;'%( cls.__table__ );
		return cls._execute(sql, False);

	def _get_pk_fields( self ):
		attr_list, pk_list = zip(*self.__pk__);
		pks =  ['%s=%s'%(fn.fieldName(),'%s') for fn in pk_list];
		args = [getattr(self,cfn,None) for cfn in attr_list];
		return pks,args;

	def _get_all_fields(self):
		attr_list, fields = zip(*self.__fields__);
		args = [getattr(self, fn, None) for fn in self.__mappings__.keys()];
		return fields,args;

	def insert( self ):
		flds,values = self._get_all_fields();
		fields = ','.join( flds );
		params = ','.join( (r'%s' for i in flds) );
		sql = 'insert into %s(%s) values(%s);'%(
				self.__table__, fields, params);
		return self._execute(sql, False, *values);
	
	def delete( self ):
		pks, args = self._get_pk_fields();
		sql = 'delete from %s where %s'%(self.__table__,','.join(pks));
		return self._execute(sql, False, *args);

	def update( self ):
		pks , args = self._get_pk_fields();
		fds, vals = self._get_all_fields();
		fields = ','.join( '%s=%s'%(fd,'%s') for fd in fds);
		sql = 'update %s set %s where %s'%(
				self.__table__, fields ,','.join(pks));
		params = vals+args;
		return self._execute(sql, False, *params);

	@classmethod
	def count_all( cls ):
		sql = 'select count(*) from %s;'%(cls.__table__);
		lines = cls._execute(sql, True);
		return lines[0][0];

	@classmethod
	def get_all( cls ):
		attrs, fields = zip(*cls.__fields__);

		sql = 'select %s from %s;'%(','.join(fields),cls.__table__);
		
		rcds = cls._execute(sql, True);

		return cls._generate_obj( attrs, rcds );

	@classmethod
	def get_one( cls , **kw):
		obj = cls( **kw );
		pks,args = obj._get_pk_fields();
		attrs, fds = zip(*cls.__fields__);
		sql = 'select %s from %s where %s;'%(
				','.join(fds), cls.__table__,' and '.join(pks));

		rcds = cls._execute(sql, True, *args);

		n = len(rcds);
		if n == 1: return cls._generate_obj( attrs, rcds )[0];
		elif n < 1: raise DBError('未查到相关记录');
		else: raise DBError('查到 %d 条记录'%n);

	@classmethod
	def select( cls, where, *args ):
		attrs, fds = zip(*cls.__fields__);
		sql = 'select %s from %s %s;'%(','.join(fds) ,cls.__table__, where);

		rcds = cls._execute(sql, True, *args);

		return cls._generate_obj(attrs, rcds);

	@classmethod
	def _generate_obj(cls, attrs, rcd_list):
		ret = [];
		for rcd in rcd_list:
			obj = cls();
			for field, value in zip(attrs, rcd):
				setattr(obj,field,value);
			ret.append(obj);
		return ret;

	@classmethod
	def _execute( cls, sql, flag = False, *args ):
		"""
		执行sql语句
		args:
			sql: sql语句模板
			flag: 返回的是行数还是查询结果, True为返回查询结果
			args: sql语句中的实参
		"""
		info = 'execute sql: %s '%sql;
		if args:
			info += str(args);
		logging.info(info);

		ret = None;
		with connectDB() as engine:
			ret = engine.execute(sql,args);
			if flag:
				ret = [ r for r in engine.fetch() ];
		return ret;

if __name__ == '__main__':
	class User( TableModel ):
		__table__ = 'users';
		id = FieldModel('id', 'varchar(50)', primaryKey=True);
		passwd = FieldModel('password', 'varchar(50)');

#	user = User(id='sammy',passwd='password4321');
#	n = user.insert();
#	print '受到影响的行数:', n;
	
	print User.count_all();
	users = User.get_all();
	for user in users:
		print user.id, user.passwd;

	print;
	user = User.get_one(id='sammy');
	print user;
	print user.id, user.passwd;

	print;
	users = User.select( 'where id=%s','sam' );
	for user in users:
		print user.id, user.passwd;
