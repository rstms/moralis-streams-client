# top-level Makefile 

usage: short-help

### local install in editable mode for development
dev: uninstall 
	pip install --upgrade -e .[dev]

### install to the local environment from the source directory
install: 
	pip install --upgrade .

### remove module from the local python environment
uninstall: 
	pip install -U pip setuptools wheel flit
	pip uninstall -yqq $(module)


generate-models:
	curl -s https://api.moralis-streams.com/api-docs/swagger.json | jq . >openapi.json
	rm -rf model_import
	rm -rf moralis_streams_client/models
	ipdb3 -c continue scripts/generate-models --output models --input openapi.json --backup-dir model_import
	#postprocess-model


### remove all build, test, coverage and Python artifacts
clean: 
	for clean in $(call included,clean); do ${MAKE} $$clean; done

include $(wildcard make.include/*.mk)
