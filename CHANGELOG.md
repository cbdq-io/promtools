# Changelog


## 1.0.2 (2026-08-12)

### Fix

* Acknowledge vulnerabilities in the base image. [Ben Dalling]

* Hadolint prefers UID over user name in Dockerfile. [Ben Dalling]

* Add basic instructions for creating a release. [Ben Dalling]

### Build

* Prometheus 3.14.0 is pre-release, using 3.13.2 instead. [Ben Dalling]

* Bump Prometheus image from 3.13.1 to 3.14.0. [Ben Dalling]


## 1.0.1 (2026-07-21)

### Build

* Bump Prometheus version from 3.12.0 to 3.13.1. [Ben Dalling]


## 1.0.0 (2026-06-30)

### Fix

* Bump Prometheus version from 3.11.3 to 3.12.0. [Ben Dalling]

* Update the version of the Git Flow workflow. [Ben Dalling]

### Build

* Bump actions/checkout from 6 to 7. [dependabot[bot]]

  Bumps [actions/checkout](https://github.com/actions/checkout) from 6 to 7.
  - [Release notes](https://github.com/actions/checkout/releases)
  - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/actions/checkout/compare/v6...v7)

  ---
  updated-dependencies:
  - dependency-name: actions/checkout
    dependency-version: '7'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...

* Bump ghcr.io/devcontainers/features/docker-in-docker. [dependabot[bot]]

  Bumps ghcr.io/devcontainers/features/docker-in-docker from 3.0.1 to 3.1.0.

  ---
  updated-dependencies:
  - dependency-name: ghcr.io/devcontainers/features/docker-in-docker
    dependency-version: 3.1.0
    dependency-type: direct:production
    update-type: version-update:semver-minor
  ...


## 0.1.1 (2026-05-27)

### Fix

* Stop custom Prometheus config being overwritten. [Ben Dalling]


## 0.1.0 (2026-05-21)

### Features

* Minimum viable product. [Jim Loughlin]

### Fix

* Qualify container images to enable CD. [Ben Dalling]

### Build

* Bump ghcr.io/devcontainers/features/docker-in-docker. [dependabot[bot]]

  Bumps ghcr.io/devcontainers/features/docker-in-docker from 2.17.0 to 3.0.1.

  ---
  updated-dependencies:
  - dependency-name: ghcr.io/devcontainers/features/docker-in-docker
    dependency-version: 3.0.1
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...

* Add dev container. [Jim Loughlin]

### Continuous Integration

* Fix Git Flow GitHub workflow. [Ben Dalling]


