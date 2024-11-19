# JUDO Connectivity Module Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

Integration to control and monitor JUDO water treatment devices with connectivity module.

**This integration will set up the following platforms.**

| Platform | Description                                    |
| -------- | ---------------------------------------------- |
| `sensor` | Show information from JUDO Connectivity Module |
| `button` | Control JUDO device functions                  |

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `judo_connectivity_module`.
4. Download _all_ the files from the `custom_components/judo_connectivity_module/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "JUDO Connectivity Module"

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

---

[judo_connectivity_module]: https://github.com/christoefle/judo_connectivity_module
[commits-shield]: https://img.shields.io/github/commit-activity/y/christoefle/judo_connectivity_module.svg?style=for-the-badge
[commits]: https://github.com/christoefle/judo_connectivity_module/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/christoefle/judo_connectivity_module.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40christoefle-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/christoefle/judo_connectivity_module.svg?style=for-the-badge
[releases]: https://github.com/christoefle/judo_connectivity_module/releases
[user_profile]: https://github.com/christoefle
