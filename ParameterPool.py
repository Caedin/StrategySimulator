import hashlib
import copy
import json

class ParameterPool(object):
	def add_value(self, value, axis):
		if len(self.data) == 0:
			self.__insert__({ axis : value })
		else:
			for d in self.data.values():
				if axis not in d:
					d[axis] = value
				else:
					c = copy.deepcopy(d)
					c[axis] = value
					self.__insert__(c)


	def __insert__(self, obj):
		self.data[hashlib.sha256(json.dumps(obj)).digest()] = obj

	def __init__(self):
		# A set of dictionary, with number as key
		self.data = {}

