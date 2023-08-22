MDDJ_VERSION=$(shell grep '^version = ' pyproject.toml | cut -d '"' -f2)

.PHONY: release
release:
	git tag -s "$(MDDJ_VERSION)" -m "v$(MDDJ_VERSION)"
	-git push $(shell git rev-parse --abbrev-ref @{push} | cut -d '/' -f1) refs/tags/$(MDDJ_VERSION)
