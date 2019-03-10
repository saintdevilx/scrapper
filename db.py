#!/usr/bin/python

import sqlite3
import os

class Model:
	def __init__(self,*args,**kwargs):
		pass
		#supert(Model,self).__init__(*args,**kwargs)

	def filter(self,table):
		pass
		
class LinkedInData(Model):

	field_list=[{'field_name':'id','primary_key':True},{'field_name':'url'},{'field_name':'expert_id'},
	{'field_name':'created','type':'datetime'},{'field_name':'last_accessed_at','type':'datetime'},
	{'field_name':'payload','type':'text'}]

	def __init__():
		pass

	class Meta:
		table_name='linkedin_data'


class DB:

	def __init__(self, *args, **kwargs):
		print('initializing DB.....')
		DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')
		self.db_path = DEFAULT_PATH
		self.conn=None
		self.cursor=None
		if not os.path.exists(DEFAULT_PATH):
			print('creating DB.....')
			self.__create_db()
		else:
			self.conn = sqlite3.connect(DEFAULT_PATH)

		self.cursor= self.conn.cursor()

	def __create_db(self):
		query="""CREATE TABLE {table_name} ({field_list});"""

		field_list=[]
		for field in LinkedInData.field_list:
			field_list += ["{field_name} {data_type} {key_type}".format(field_name=field.get('field_name'),
			data_type=field.get('type','INTEGER' if field.get('primary_key') else 'varchar(1000)'), key_type="PRIMARY KEY" if field.get('primary_key','') else '' )]
		field_list = ",".join(field_list)

		query=query.format(table_name=LinkedInData.Meta.table_name, field_list=field_list)
		print('creating table.....', query, field_list)
		self.conn = sqlite3.connect(self.db_path)
		self.conn.execute(query)

	def filter(self, table, **kwargs):
		query ="SELECT {fields_list} from {table} where {condition}".format(table=table, 
			fields_list=kwargs.get('fields_list','*'), condition=kwargs.get('condition'));
		return self.cursor.execute(query).fetchmany(kwargs.get('limit',10))

	def update(self, table , **kwargs):
		query = 'UPDATE {table} set '.format(table=table)
		for key,value  in kwargs.get('set_data').item():
			query += '%s=%s'%(key,value)
		if kwargs.get('condition'):			
			query +=' where %s'%kwargs.get('condition')
		return self.cursor.execute(query)

	def delete(self,table,**kwargs):
		return self.cursor.execute('delete from %s where %s'%(table,kwargs.get('where')))

	def insert(self, table, **kwargs):
		query = 'INSERT INTO {table}({columns})  values({values})'.format(table=table, 
			columns=','.join(kwargs.keys()), values="'"+"','".join(kwargs.values())+"'")				
		self.cursor.execute(query)
		print query
		return self.cursor.lastrowid




db = DB()
for r in db.filter(LinkedInData.Meta.table_name,**{'condition':'1=1'}):
	print r,'=='
db.insert(LinkedInData.Meta.table_name, **{'url':'demo','payload':"{}",'expert_id':'420'})