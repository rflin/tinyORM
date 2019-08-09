class Field(object):
	def __init__(self, cls):
		self.value = None
		self.cls = cls

	def setValue(self, value):
		self.value = value

	def __str__(self):
		return str(self.value)

	# def __repr__(self):
	# 	return str(self.value)

class CharField(Field):
	def __init__(self, max_length=20, null=False, primary_key=False):
		self.max_length = max_length
		self.null = null
		self.primary_key = primary_key
		super().__init__(str)

	def get_dbtype(self):
		dbtype = ' char(%d)' % int(self.max_length)
		if self.primary_key is True:
			dbtype += ' primary key'
		if self.null is False:
			dbtype += ' not null'
		return dbtype

class TextField(Field):
	def __init__(self, null=False, primary_key=False):
		self.null = null
		self.primary_key = primary_key
		super().__init__(str)

	def get_dbtype(self):
		dbtype = ' text'
		if self.primary_key is True:
			dbtype += ' primary key'
		if self.null is False:
			dbtype += ' not null'
		return dbtype

class IntegerField(Field):
	def __init__(self, null=False, primary_key = False):
		self.null = null
		self.primary_key = primary_key
		super().__init__(int)

	def get_dbtype(self):
		dbtype = ' integer'
		if self.primary_key is True:
			dbtype += ' primary key'
		if self.null is False:
			dbtype += ' not null'
		return dbtype

class AutoField(Field):
	def __init__(self, primary_key=False):
		if primary_key == False:
			raise Exception('primary_key must be True on AutoField Type')
		self.null = True
		self.primary_key = primary_key
		super().__init__(int)

	def get_dbtype(self):
		dbtype = ' integer'
		if self.primary_key is True:
			dbtype += ' primary key autoincrement'
		return dbtype
