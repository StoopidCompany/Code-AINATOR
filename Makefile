help: ## show help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

sec-scan: ## security scanning
	@checkov -d . --soft-fail

commit: ## commits all code to git
	@git add -A && pre-commit run -a && cz c && git push

test: ## runs unit tests
	@python -m unittest tests/test_cli.py
