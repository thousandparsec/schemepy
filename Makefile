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
TRUNNER = nosetests
SCHEMEPY = tests/schemepy

test_guile:
	BACKEND=guile $(TRUNNER) $(SCHEMEPY)
test_oldguile:
	BACKEND=oldguile $(TRUNNER) $(SCHEMEPY)

test: test_guile
