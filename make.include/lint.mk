# source formatting

lint_src = $(module) tests docs scripts/generate-models

_fmt:
	isort $(lint_src)
	black $(lint_src)

_lint:
	@bash -c 'set -eo pipefail; (flake8 --config tox.ini $(lint_src) | tee .lint)'

### reformat python source with black; check style, lint with flake8
fmt: _fmt _lint

# alias for fmt
lint: fmt

fix:
	@$(MAKE) lint || true
	@fixlint

# vim:ft=make
