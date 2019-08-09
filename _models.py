import sqlite3
import copy
from _Fields import *
import _config

class ModelMetaClass(type):
	def __new__(cls, name, base, attr):
		parent = [e for e in base if isinstance(e, ModelMetaClass)]
		if not parent:
			return super().__new__(cls, name, base, attr)
		_attr = {}
		__mapping__ = {}
		
		pk_count = 0
		for k, v in attr.items():
			if isinstance(v, Field):
				__mapping__[k] = v
				if v.primary_key is True:
					pk_count = pk_count + 1
			else:
				_attr[k] = v
		if pk_count == 0:
			__mapping__['pk'] = AutoField(primary_key=True)
		_attr['__mapping__'] = __mapping__
		if '__table_name__' not in _attr.keys():
			_attr['__table_name__'] = _attr['__qualname__']
		_attr['dbv'] = False
		_attr['objects'] = Manager(__mapping__, _attr['__table_name__'])
		newcls = super().__new__(cls, name, base, _attr)
		newcls.objects.model = newcls
		return newcls

class Manager:
	def __init__(self, __mapping__, __table_name__):
		self.__mapping__ = __mapping__
		self.__table_name__ = __table_name__
		self.model = None

	def get(self, **kwargs):
		res = self.filter(**kwargs)
		sz = len(res)
		if sz == 0:
			return None
		if sz > 1:
			raise Exception('not one result')
		param = {}
		key_list = self.__mapping__.keys()
		value_list = list(res[0])
		k_v = zip(key_list, value_list)
		for e in k_v:
			param[e[0]] = e[1]
		model_obj = self.model(**param)
		model_obj.dbv = True
		return model_obj

	def delete(self, **kwargs):
		w_cond = self.kw(**kwargs)
		try:
			conn = sqlite3.connect(_config._dbname)
			cursor = conn.cursor()
			sql = "delete from %s where %s" % (self.__table_name__, w_cond)
			print(sql)
			cursor.execute(sql)
			cursor.close()
			conn.commit()
			conn.close()
			# print('delete success!')
		except Exception as e:
			print("Error when delete:", e)
			conn.close()

	def all(self):
		return self.filter()

	def kw(self, **kwargs):
		result = []
		for k, v in kwargs.items():
			if k not in self.__mapping__.keys():
				raise KeyError('Error query keys')
			if v is None:
				continue
			if not isinstance(v, self.__mapping__[k].cls):
				raise TypeError('Error value type')
			if self.__mapping__[k].cls == str:
				result.append('%s=\'%s\'' % (k, v))
			else:
				result.append('%s=%s' % (k, str(v)))
		return " and ".join(result)

	def filter(self, **kwargs):
		try:
			conn = sqlite3.connect(_config._dbname)
			cursor = conn.cursor()
			sql = 'select * from %s' % self.__table_name__
			w_cond = self.kw(**kwargs)
			if w_cond:
				sql = sql + ' where %s' % w_cond
			print(sql)
			cursor.execute(sql)
			values = cursor.fetchall()
			cursor.close()
			conn.close()
			return values
		except Exception as e:
			print('filter:', e)
			conn.close()
			return None

class Model(metaclass=ModelMetaClass):
	def __init__(self, **kwargs):
		self.__mapping__ = copy.deepcopy(self.__mapping__)
		# self.dbv = False
		for k, v in kwargs.items():
			if k not in self.__mapping__.keys():
				raise KeyError('illegal key attribute', k)
			if v is None:
				continue
			if not isinstance(v, self.__mapping__[k].cls):
				raise TypeError('illegal value type', type(v))
			self.__mapping__[k].setValue(v)
		self.pks = []
		for k, v in self.__mapping__.items():
			if v.null is False and v.value is None:
				raise Exception(k + ' should not be null')
			if v.primary_key is True:
				self.pks.append(k)

	def __getattr__(self, k):
		if k not in self.__mapping__.keys():
			raise AttributeError("%s has not this attribute '%s'" % (self.__class__, k))
		return self.__mapping__[k].value

	def __setattr__(self, k, v):
		if k in ['__mapping__', 'pks', 'dbv'] :
			super().__setattr__(k, v)
			return
		if k not in self.__mapping__.keys():
			raise KeyError("%s has not this attribute '%s'" % (self.__class__, k))
		if not isinstance(v, self.__mapping__[k].cls):
			raise TypeError('illegal value type %s' % type(v))
		if k in self.pks:
			self.dbv = False
		self.__mapping__[k].setValue(v)

	def delete(self):
		d_v = self.values()
		cond_d = {}
		for k in self.pks:
			cond_d[k] = self.__mapping__[k].value
		# print(d_v)
		self.objects.delete(**cond_d)

	def insert(self):
		sql = 'insert into %s (%s) values(%s)' % (self.__table_name__, *self.__k_v__(contains_pk = True))
		return sql

	def update(self):
		res = ''
		for k, v in self.__mapping__.items():
			if v.primary_key is True:
				continue
			res += k + '='
			val = 'NULL' if v.value is None else v.value
			if v.cls == str and v.value is not None:
				res += "'%s'" % val + ','
			else:
				res += str(val) + ','
		cond_res = ''
		for k in self.pks:
			cond_res += k + '='
			val = 'NULL' if v.value is None else v.value
			if v.cls == str and v.value is None:
				cond_res += "'%s'" % val + ','
			else:
				cond_res += str(val) + ','

		sql = 'update %s set %s where %s' % (self.__table_name__, res[:-1], cond_res[:-1])
		return sql

	def __k_v__(self, contains_pk = True):
		ks = ''
		vs = ''
		for k, v in self.__mapping__.items():
			if v.primary_key is True and contains_pk is False:
				continue
			ks += k + ','
			val = 'NULL' if v.value is None else v.value
			if v.cls == str and v.value is not None:
				vs += "'%s'" % val + ','
			else:
				vs += str(val) + ','
		return ks[:-1], vs[:-1]

	def values(self, contains_none = True):
		d_v = {}
		for k, v in self.__mapping__.items():
			if contains_none == False and v.value == None:
				continue
			d_v[k] = v.value
		return d_v

	def save(self):
		if self.dbv == True:
			sql = self.update()
		else:
			sql = self.insert()
		print(sql)
		try:
			conn = sqlite3.connect(_config._dbname)
			cursor = conn.cursor()
			cursor.execute(sql)
			if self.dbv == False:
				cursor.execute('select last_insert_rowid()')
				last_insert_rowid, = cursor.fetchone() #pk
				lir_sql = "select * from %s where rowid = %d" % (self.__table_name__, last_insert_rowid)
				cursor.execute(lir_sql)
				line = cursor.fetchone()
				# print(line)
				idx = 0
				# print("8888", last_insert_rowid, line)
				for k, v in self.__mapping__.items():
					if k in self.pks:
						v.setValue(line[idx])
					idx = idx + 1
				self.dbv = True
			cursor.close()
			conn.commit()
			conn.close()
		except Exception as e:
			print('save:', e)
			conn.close()

def generate_mkTbsql(obj):
	column_types = ''
	pk_count = 0
	in_count = 0
	pks = ''
	for k, v in obj.__mapping__.items():
		column_types +=  k + v.get_dbtype() + ','
		if v.primary_key is True:
			pk_count = pk_count + 1
			pks += k + ','
	if pk_count > 1:
		column_types = column_types.replace(' primary key', '')
		column_types += 'primary key(%s)' % pks[:-1]
		sql = 'create table %s(%s);' % (obj.__table_name__, column_types)
		return sql
	sql = 'create table %s(%s);' % (obj.__table_name__, column_types[:-1])
	return sql

def init(obj, dbname=_config._dbname, drop = False):
	sql = generate_mkTbsql(obj)
	print(sql)
	try:
		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			if drop is True:
				cursor.execute('drop table if exists %s' % obj.__table_name__)
			cursor.execute(sql)
			cursor.close()
			conn.commit()
		return True
	except Exception as e:
		print("Error:", e)
		return False

