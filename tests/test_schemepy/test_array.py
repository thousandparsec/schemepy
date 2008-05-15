
#
# Array effectively share the same memory. A change in one side causes a change
# in the other side. See the example below
#

import array

a = array.array('f', [x*0.5 for x in range(0, 20)])
print a
# Outputs: array('f', [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5])

a[4] = 99
print a
# Outputs : array('f', [0.0, 0.5, 1.0, 1.5, 99.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5])

# s = vm.toscheme(a)
# vm.call("array-set!", s, 44, 0)
# print a 
# Outputs : array('f', [0.0, 0.5, 1.0, 1.5, 99.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5])

