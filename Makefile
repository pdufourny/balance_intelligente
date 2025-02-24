########################################################################################################################
# Project setup : environment
########################################################################################################################
setup:
	if pyenv virtualenvs | grep -q 'balance_intelligente'; then \
		echo "Virtualenv 'balance_intelligente' already exists"; \
	else \
		echo "Creating virtualenv 'balance_intelligente' ..."; \
		pyenv virtualenv 3.10.12 balance_intelligente; \
		pyenv virtualenv allow; \
		pyenv local balance_intelligente; \
	fi

precommit_install:
	@echo "Installing pre-commit hooks ..."
	@pip install pre-commit
	@pre-commit install
	@echo "✅ Pre-commit hooks installed"

########################################################################################################################
# Project setup : pip requirements
########################################################################################################################
pip_requirements:
	@echo "Installing pip requirements..."
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

########################################################################################################################
# training on request
########################################################################################################################

########################################################################################################################
# test sending POST request with an image
########################################################################################################################
test_POST:
	@echo "sending image using post"
	@rm kiwi_test.jpg
	@curl -X POST http://127.0.0.1:5000/prediction -F "file=@data/kiwi_test.jpg"
	@if [ -f kiwi_test.jpg ]; then \
		echo "POST request OK"; \
	else \
		echo "POST request failed"; \
	fi
