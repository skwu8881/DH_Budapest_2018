import pymysql

class ctbcfxSQL:
	def __init__(self, _db='ctbcfx'):
		self.db = _db
	
	def getConfig(self):
		_conn = pymysql.connect(host='10.33.41.120',
						port=3306,
						user='ctbcfx',
						passwd='sap@ssw0rd',
						db=self.db,
						charset='UTF8',
						cursorclass=pymysql.cursors.DictCursor)
		return _conn
	
	def insert(self, table, cols, vals):
		conn = self.getConfig()
		sql_string = "INSERT INTO %s ("%(table)
		
		for i in range(len(cols)):
			if i > 0:
				sql_string += ','
			sql_string += "`%s`"%(str(cols[i]))
		sql_string += ") VALUES ("
		for i in range(len(vals)):
			if i > 0:
				sql_string += ','
			sql_string += "%s%s"%('%','s')
		sql_string += ");"
		
		try:
			with conn.cursor() as cur:
				cur.execute(sql_string, tuple(vals))
			
			conn.commit()
		except pymysql.MySQLError as e:
			print('Got error {!r}, errno is {}'.format(e, e.args[0]))
			return False
			
		finally:
			conn.close()
			return True
			
	def update(self, table, change_str, condition_str):
		conn = self.getConfig()

		try:
			with conn.cursor() as cur:
				cur.execute("UPDATE `%s` SET %s WHERE %s"%(table, change_str, condition_str))
			
			conn.commit()
		except pymysql.MySQLError as e:
			print('Got error {!r}, errno is {}'.format(e, e.args[0]))
			return False
			
		finally:
			conn.close()
			return True
			
	def query(self, table, cols="*", condition_str="1"):
		conn = self.getConfig()
		output = None
		
		cols_string = ""
		if cols == "*":
			cols_string = "*"
		else:			
			for i in range(len(cols)):
				if i > 0:
					cols_string += ','
				cols_string += ("`" + str(cols[i]) + "`")
		
		try:
			with conn.cursor() as cur:
				sql = "SELECT %s FROM `%s` WHERE %s"%(cols_string, table, condition_str)
				print("SQL:",sql)
				cur.execute(sql)
				output=cur.fetchall()

			conn.commit()
		except pymysql.MySQLError as e:
			print('Got error {!r}, errno is {}'.format(e, e.args[0]))
			return False
			
		finally:
			conn.close()
			return output
			
	def delete(self, table, condition_str="1"):
		conn = self.getConfig()
						
		try:
			with conn.cursor() as cur:
				cur.execute("DELETE FROM %s WHERE %s"%(table, condition_str))

			conn.commit()
		except pymysql.MySQLError as e:
			print('Got error {!r}, errno is {}'.format(e, e.args[0]))
			return False
			
		finally:
			conn.close()
			return True
	
	def crawler_DelDup(self, table):
		conn = self.getConfig()
		
		try:
			with conn.cursor() as cur:
				sql = "delete "+table+" from "+table+" join "
				sql += "( select `time`,`title`,min(`id`) as theMin,count(*) as theCount "
				sql += "from "+table+" group by `time`,`title` having theCount>1 ) "
				sql += "xxx on "+table+".title=xxx.title and "+table+".time=xxx.time and "+table+".id>xxx.theMin"
				#sql = "DELETE FROM "+table+" a LEFT JOIN "+table+" b ON a.time = b.time WHERE a.id > b.id"
				
				cur.execute(sql)

			conn.commit()
		except pymysql.MySQLError as e:
			print('Got error {!r}, errno is {}'.format(e, e.args[0]))
			return False
			
		finally:
			conn.close()
			return True
			
	def crawler_countDup(self, table):
		conn = self.getConfig()
		output = None
		
		try:
			with conn.cursor() as cur:
				sql = "SELECT `time`, `title`, COUNT(`title`) AS cnt FROM "+table+" GROUP BY `time`, `title` HAVING (cnt > 1)"
				cur.execute(sql)
				output=cur.fetchall()
				
			conn.commit()
		except pymysql.MySQLError as e:
			print('Got error {!r}, errno is {}'.format(e, e.args[0]))
			return -1
			
		finally:
			conn.close()
			return len(output)
	
	def rawSQL(self, cmd):
		conn = self.getConfig()
		output = None
		
		try:
			with conn.cursor() as cur:
				cur.execute(cmd)
				output=cur.fetchall()

			conn.commit()
		except pymysql.MySQLError as e:
			print('Got error {!r}, errno is {}'.format(e, e.args[0]))
			return False
			
		finally:
			conn.close()
			return output