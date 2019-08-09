import _models
from _Fields import *
import _config


class User(_models.Model):
	name = CharField(max_length = 40)
	age = IntegerField()
	gender = CharField(max_length = 12)
	descriptions = TextField(null=True)

	def __str__(self):
		res = ''
		for k, v in self.__mapping__.items():
			res += '\t' + str(k) + ': ' + str(v) + '\n'
		return "{\n%s}" % res



#generate table, the previous table will be droped if you set the 'drop' tag as True
#usually, it should be execute once at the begining
# _models.init(User, drop=True) 

#create a user object
u = User(name = 'Alicex', age = 17, gender = 'famale')
#this will not be writed into database before you call save method
#save method will write record into database
u.save() #equals "insert into User (name,age,gender,descriptions,pk) values('Alice',17,'famale',NULL,NULL)"
#after that, you can modify some other infomation
u.descriptions = "just for test"
#and you can call 'save' method
u.save() #equals "update User set name='Alice',age=17,gender='famale',descriptions='just for test' where pk=1"
#you can get a object from database
#notice the record must be unique, otherwise, it will raise Exception
p = User.objects.get(name='Alicex')
#if the record is not exist, it will return None
#the best way is that you need check the p is not None before you use this object
if p is not None:
	p.descriptions = 'objects.get'
	p.save() #equals "update User set name='Alice',age=17,gender='famale',descriptions='objects.get' where pk=1"

#delete one record
p.delete()
#you can also use 
User.objects.delete(age=17) 

r = User.objects.filter(age=19) #get records where age equals 19, the result is a list
