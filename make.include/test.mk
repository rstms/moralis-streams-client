# test - testing with pytest and tox

options ?= -x $(if $(USE_GAS),,-m "not uses_gas")
testfiles ?= $(wildcard tests/test_*.py)
options := $(if $(test),$(options) -k $(test),$(options))



### run tests;  example: make options=-svvx test=cli test 
test: fmt
	env TESTING=1 pytest $(options) --log-cli-level=ERROR $(testfiles)

### run tests; drop into pdb on exceptions or breakpoints
debug:
	env TESTING=1 pytest $(options) -vvvs --log-cli-level=INFO --pdb $(testfiles)

### check code coverage quickly with the default Python
coverage:
	env TESTING=1 coverage run --source $(module) -m pytest
	coverage report -m
	coverage html
	$(browser) htmlcov/index.html

### list test cases
testls:
	@grep -h -R '^def test_' tests/test_*.py | awk -F'[ (]' '{print $$2}' | sort | uniq


.PHONY: tox
### test with tox if sources have changed
tox: .tox 
.tox: $(src) tox.ini
	$(call gitclean)
	env PYTEST_OPTIONS='$(options)' tox
	@touch $@

# run tox in debug mode
toxdebug:
	$(MAKE) --no-print-directory tox_options="-o log_cli_level=INFO -xvvvs --pdb" tox

toxclean:
	rm -rf .tox

test-clean: toxclean
