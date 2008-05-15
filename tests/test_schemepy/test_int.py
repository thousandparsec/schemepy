import common

class TestInt(object):
	def check_eval(self, value):
		"""
		Checks that the eval returns int for small integers.
		"""
		print "eval", str(value)

		m1 = common.VM()
		a = m1.eval(m1.compile(str(value)))

		assert m1.type(a) in (int, long)
		assert m1.fromscheme(a) == value

	def check_passthru(self, value):
		print "passthru", repr(value)

		m1 = common.VM()
		scm = m1.toscheme(value)
	
		assert m1.type(scm) in (int, long)
		assert m1.fromscheme(scm) == value

	def test_ints(self):
		ints = [1, 5, 1000, int(2**31-1), int(-2**31)]
		for value in ints:
			yield self.check_eval, value
			yield self.check_passthru, value
