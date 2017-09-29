drop database if exists myblog;
drop user if exists admin;

create user admin@'%' identified by '123abc';
grant select,insert,update,delete on myblog.* to admin;
create database myblog;

use myblog; # 使用数据库

create table users(
		id varchar(50)  primary key,
		password varchar(50),
		role enum('Admin','User') default 'User',
		email varchar(50)
);

insert into users(id,password) values('dean', 'password1234');
