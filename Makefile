# Default action
default: test

########################################
# Documentation
########################################
DOCC = doc/src/compile-doc.py
doc/html/%.html: doc/src/%.rst doc/src/template.txt doc/src/compile-doc.py
	$(DOCC) doc/src/$*.rst > doc/html/$*.html

doc: $(patsubst doc/src/%.rst,doc/html/%.html,$(wildcard doc/src/*.rst))



########################################
# Test
########################################
PYTEST = py.test --tb=short tests

test_guile:
	TEST_MODULE=guile $(PYTEST)

test: test_guile