# requirements - generate requirements.txt and friends
 
define MAKE_REQUIREMENTS_PYSCRIPT

import sys
import toml
from pathlib import Path
from box import Box

p = Box(toml.load(sys.stdin))
if 'project' in p:
    if 'dependencies' in p.project:
        with Path('requirements.txt').open('w') as ofp:
            for d in p.project.dependencies:
                ofp.write(d+'\n')

    if 'optional-dependencies' in p.project:
        for o in p.project.optional_dependencies:
            with Path(f'requirements-{o}.txt').open('w') as ofp:
                for d in p.project.optional_dependencies[o]:
                    ofp.write(d+'\n')

endef
export MAKE_REQUIREMENTS_PYSCRIPT

make_requirements := python -c "$$MAKE_REQUIREMENTS_PYSCRIPT"

### update requirements*.txt 
requirements.txt: pyproject.toml
	rm -f requirements*.txt
	$(call make_requirements) <$<

# clean up generated requirements files
#requirements-clean:
#3	rm requirements*.txt

