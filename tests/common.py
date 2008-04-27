
VM = None
compile = None
types = None
def setup_module(self):
	import os
	try:
		module = os.environ['TEST_MODULE']
	except KeyError:
		raise Exception("You need to specify the TEST_MODULE environment varible!")

	import sys
	import os
	sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

	try:
		exec("from schemepy.%s import %s as totest" % (module, module))
		exec("import schemepy.types")
	except ImportError, e:
		print e
		raise Exception("Module named %s doesn't exist!" % module)

	global VM
	global compile
	VM = totest.VM
	compile = totest.Compiler()

	global types
	types = schemepy.types
