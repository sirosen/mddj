# Releasing

- Update the version with `mddj write version ...`
- Update the changelog to add a version header
- Add and commit changes,
  `git add -p; git commit -m 'Bump version for release'`
- Tag and wait for test-pypi publication
- Create a GitHub release and wait for pypi publication
