# publish - build package and publish

# publish to pypi
publish: release
	$(call require_pypi_config)
	@set -e;\
	if [ "$(version)" != "$(pypi_version)" ]; then \
	  $(call verify_action,publish to PyPi) \
	  echo publishing $(dist_name) $(version) to PyPI...;\
	  flit publish;\
	else \
	  echo $(dist_name) $(version) is up-to-date on PyPI;\
	fi

# check current pypi version 
pypi-check:
	$(call require_pypi_config)
	@echo '$(dist_name) local=$(version) pypi=$(call check_pypi_version)'

# clean up publish generated files
publish-clean:
	rm -f .dist
	rm -rf .tox

# functions
define require_pypi_config =
$(if $(wildcard ~/.pypirc),,$(error publish failed; ~/.pypirc required))
endef

pypi_version := $(shell pip install $(dist_name)==fnord.plough.plover.xyzzy 2>&1 |\
  awk -F'[,() ]' '/^ERROR: Could not find a version .* \(from versions:.*\)/{print $$(NF-1)}')

define check_null =
$(if $(1),$(1),$(error $(2)))
endef

check_pypi_version = $(call check_null,$(pypi_version),PyPi version query failed)
