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

DevContainer (Recommended)

If you use VS Code with the DevContainer extension:

```bash
# Open the project in VS Code
# Accept the prompt to reopen in DevContainer
# Environment will be automatically configured
```

## Authors & contributors

The original setup of this repository is by [Wouter Coppens][woutercoppens].

For a full list of all authors and contributors, check [the contributor's page][contributors].

## License

This project is licensed under the AGPLv3 License - see the LICENSE.md file for details

[license-shield]: https://img.shields.io/badge/License-AGPL_v3-blue.svg
[build-shield]: https://github.com/rensongroup/pyhaopenmotics/actions/workflows/pyrefly.yaml/badge.svg
[build]: https://github.com/rensongroup/pyhaopenmotics/actions/workflows/pyrefly.yaml
[code-quality-shield]: https://img.shields.io/lgtm/grade/python/g/rensongroup/pyhaopenmotics.svg?logo=lgtm&logoWidth=18
[code-quality]: https://lgtm.com/projects/g/rensongroup/pyhaopenmotics/context:python
[contributors]: https://github.com/rensongroup/pyhaopenmotics/graphs/contributors
[woutercoppens]: https://github.com/woutercoppens
[keepchangelog]: http://keepachangelog.com/en/1.0.0/
[maintenance-shield]: https://img.shields.io/maintenance/yes/2026.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[releases]: https://github.com/rensongroup/pyhaopenmotics/releases
[semver]: http://semver.org/spec/v2.0.0.html
