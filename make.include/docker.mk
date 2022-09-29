#
# docker makefile
#
 
$(if $(DOCKER_REGISTRY),,$(error DOCKER_REGISTRY is undefined))
registry=$(DOCKER_REGISTRY)

exec = chamber exec $(PROFILE) --

build_args := \
 VERSION=$(version)

image = $(registry)/$(PWD)

build_arg_list = $(foreach arg,$(build_args),--build-arg $(arg) )

build_opts := $(build_arg_list) --tag $(image):$(version)

build_env:
	@echo "registry=$(registry)"
	@echo "base_version=$(version)"
	@echo "version=$(version)"
	@echo "build_args=$(build_args)"
	@echo "build_arg_list=$(build_arg_list)"
	@echo "build_opts=$(build_opts)"
	@chamber env $(PROFILE)

### build image
build: release
	docker build $(build_opts) .
	docker tag $(image):$(version) $(image):latest

### rebuild image
rebuild:
	$(MAKE) build_opts="$(build_opts) --no-cache" build

### push image to docker registry
push: build
	docker push $(image):$(version)
	docker push $(image):latest

### run image
run: 
	$(exec) docker run $(image)

