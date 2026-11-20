# GitHub repository workflows

These workflows automate validation, release preparation, and package
publishing for the repository.

- [`ci.yml`](ci.yml) runs the test suite for pushes, pull requests, and manual dispatches.
- [`native-acceptance.yml`](native-acceptance.yml) validates native package acceptance.
- [`release-candidate.yml`](release-candidate.yml) verifies release candidates.
- [`release-approve.yml`](release-approve.yml) approves an exact release.
- [`tui-release.yml`](tui-release.yml) publishes the terminal UI package.

Release workflows are manually dispatched and should be run only after the
relevant validation workflow has passed.
