
########################################################################################################################
# Project setup : environment
########################################################################################################################

if pyenv virtualenvs | grep -q 'balance_intelligente'; then \
		echo "Virtualenv 'titanic' already exists"; \
	else \
		echo "Creating virtualenv 'balance_intelligente' ..."; \
		pyenv virtualenv 3.10.12 balance_intelligente; \
		pyenv virtualenv allow
		pyenv local balance_intelligente \
	fi

precommit_install:
	@echo "Installing pre-commit hooks ..."
	@pip install pre-commit
	@pre-commit install
	@echo "✅ Pre-commit hooks installed"





########################################################################################################################
# Project setup :  pip requirements
########################################################################################################################
python -m pip install --upgrade pip
python -m pip install -r requirements.txt






########################################################################################################################
#training on request
########################################################################################################################
