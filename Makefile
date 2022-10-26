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
	pip install --upgrade pip setuptools wheel flit
	pip uninstall -yqq $(module)


generate-models:
	which datamodel-codegen || pipx install datamodel-code-generator
	curl -s https://api.moralis-streams.com/api-docs/swagger.json | jq . >openapi.json
	rm -rf model_import
	rm -rf moralis_streams_client/models
	scripts/generate-models --output models --input openapi.json --backup-dir model_import


### remove all build, test, coverage and Python artifacts
clean: 
	for clean in $(call included,clean); do ${MAKE} $$clean; done

include $(wildcard make.include/*.mk)
