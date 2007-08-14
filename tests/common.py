
Inter = None
def setup_module(self):
	import os
	try:
		module = os.environ['TEST_MODULE']
	except KeyError:
		raise Exception("You need to specify the TEST_MODULE environment varible!")

	import sys
	sys.path.append('..')

	try:
		exec("from schemepy.%s import %s as totest" % (module, module))
	except ImportError, e:
		print e
		raise Exception("Module named %s doesn't exist!" % module)

	global Inter
	Inter = totest.Inter
