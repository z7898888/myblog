use myblog;

drop function if exists queryChild;
delimiter //
create function queryChild( cataid varchar(100))
	returns text
	begin
		declare sRet text;
		declare sTmp text;

		set sRet = '$';
		set sTmp = cataid;

		while sTmp is not null do
			set sRet = concat(sRet,',',sTmp);
			select group_concat(id) into sTmp from catalogs where find_in_set(parent_id,sTmp);
		end while;
		return sRet;
	end //
delimiter ;

select group_concat(parent_id) into @a from catalogs where parent_id is not null;
select id,parent_id from catalogs;
select @a;
select queryChild(@a);
select * from blogs where find_in_set(catalog_id, queryChild(@a));
