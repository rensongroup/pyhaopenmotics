# Python: Asynchronous Python client for the Openmotics API

[![GitHub Release][releases-shield]][releases] [![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield] ![Project Maintenance][maintenance-shield]
[![License AGPL v3][license-shield]](LICENSE.md)

[![Build Status][build-shield]][build]

Asynchronous Python client for the OpenMotics API.

## About

An asynchronous python client for the OpenMotics API to control the outputs and other modules.

This library is created to support the integration in [Home Assistant](https://www.home-assistant.io).

## Installation

```bash
cd pyhaopenmotics
pip install .
```

## Usage

See examples folder.

## Changelog & Releases

This repository keeps a change log using [GitHub's releases][releases] functionality. The format of the log is based on
[Keep a Changelog][keepchangelog].

Releases are based on [Semantic Versioning][semver], and use the format of `MAJOR.MINOR.PATCH`. In a nutshell, the
version will be incremented based on the following:

- `MAJOR`: Incompatible or major changes.
- `MINOR`: Backwards-compatible new features and enhancements.
- `PATCH`: Backwards-compatible bugfixes and package updates.

## Contributing

This is an active open-source project. We are always open to people who want to use the code or contribute to it.

We've set up a separate document for our [contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

This Python project is fully managed using the [Poetry][poetry] dependency manager. But also relies on the use of NodeJS
for certain checks during development.

You need at least:

- Python 3.9+
- [Poetry][poetry-install]
- NodeJS 12+ (including NPM)

To install all packages, including all development requirements:

```bash
npm install
poetry install
```

As this repository uses the [pre-commit][pre-commit] framework, all changes are linted and tested with each commit. You
can run all checks and tests manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

## Authors & contributors

The original setup of this repository is by [Wouter Coppens][woutercoppens].

For a full list of all authors and contributors, check [the contributor's page][contributors].

## License

This project is licensed under the AGPLv3 License - see the LICENSE.md file for details

[license-shield]: https://img.shields.io/badge/License-AGPL_v3-blue.svg
[build-shield]: https://github.com/openmotics/pyhaopenmotics/actions/workflows/tests.yaml/badge.svg
[build]: https://github.com/openmotics/pyhaopenmotics/actions/workflows/tests.yaml
[code-quality-shield]: https://img.shields.io/lgtm/grade/python/g/openmotics/pyhaopenmotics.svg?logo=lgtm&logoWidth=18
[code-quality]: https://lgtm.com/projects/g/openmotics/pyhaopenmotics/context:python
[contributors]: https://github.com/openmotics/pyhaopenmotics/graphs/contributors
[woutercoppens]: https://github.com/woutercoppens
[keepchangelog]: http://keepachangelog.com/en/1.0.0/
[maintenance-shield]: https://img.shields.io/maintenance/yes/2022.svg
[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com/
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/pyhaopenmotics/
[releases]: https://github.com/openmotics/pyhaopenmotics/releases
[semver]: http://semver.org/spec/v2.0.0.html
