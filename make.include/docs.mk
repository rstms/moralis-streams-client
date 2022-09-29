# make clean targets

# generate Sphinx HTML documentation, including API docs
#


### install documentation build dependencies
install-docs:
	pip install -U .[docs]

### rebuild documentation
docs: install-docs clean-docs docs/readme.rst
	sphinx-apidoc -o docs/ $(module)
	$(MAKE) -C docs html
	$(browser) docs/_build/html/index.html

# clean up documentation files
clean-docs:
	rm -f docs/$(project).rst
	rm -f docs/modules.rst
	$(MAKE) -C docs clean

# run a dev-mode docs webserver; recompiling on changes 
servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

docs/readme.rst: README.md
	m2r2 --overwrite $<
	mv README.rst $@

# add the cli help to the README

.PHONY: README.md
README.md:
	if [ $(module)/cli.py -nt $@ ]; then\
	  awk <$@ >README.new -v flag=0 '/^## CLI/{flag=1} /```/{if(flag) exit} {print $$0}';\
	  echo '```' >>README.new;\
	  $(cli) --help >>README.new;\
	  echo '```' >>README.new;\
	  mv README.new $@;\
	fi
