# create distributable files if sources have changed

current_wheel != ls 2>/dev/null dist/$(module)-$(version)-*.whl
current_release = dist/$(module)-$(version)-release.json

$(if $(GITHUB_ORG),,$(error GITHUB_ORG is undefined))
$(if $(GITHUB_TOKEN),,$(error GITHUB_TOKEN is undefined))

RELEASE = release \
  --organization $(GITHUB_ORG)\
  --repository $(project)\
  --token $(GITHUB_TOKEN)\
  --module-dir ./$(module)\
  --wheel-dir ./dist\
  --version $(version) 

check_wheel = $(if $(shell [ -s $(current_wheel) ] && echo y),,$(error wheel file null or nonexistent))

latest_release_version != $(RELEASE) -J latest 2>/dev/null

# query github and output the latest release version
latest-github-release:
	@echo $(latest_release_version)

.dist: $(module)/version.py
	$(call gitclean)
	mkdir -p dist
	flit build

.PHONY: dist 
### build a wheel file for distribution
dist: $(if $(DISABLE_TOX),,tox)
	@[ -s "$(current_wheel)" ] && echo "$(current_wheel) is up to date." || $(MAKE) --no-print-directory .dist 


$(current_release): dist
	$(call check_wheel)
	@set -e;\
	if [ "$(latest_release_version)" = "$(version)" ]; then \
	  echo "Version $(version) is already released"; \
	else \
	  echo "Creating $(project) release v$(version)..."; \
	  $(RELEASE) create --force >$@; \
	  $(RELEASE) upload --force >>$@; \
	fi

.PHONY: release
### create a github release and upload assets
release: $(current_release)

# clean up the release temp files
release-clean:
	rm -f .dist
