# HA-OpenEI

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Home Assistant custom integration for retrieving utility rate structures from [OpenEI.org][openei]._

## Requirements

- **Home Assistant**: `2026.3.0` or newer (Python 3.14+)
- **OpenEI API Key**: Free API key from [OpenEI API Signup][openei-signup]

## Platforms & Entities

Platform | Description
-- | --
`sensor` | Utility rate, adjustment, sell rate, rate structure, and billing charge sensors.
`binary_sensor` | Plan approval status (`Approval`).

### Sensors

Sensor | Category | Description
-- | -- | --
`Current Energy Rate` | Primary | Active energy rate (`<currency>/kWh`). Includes `all_rates` and `all_adjustments` attributes.
`Current Energy Adjustment` | Primary | Active energy rate adjustment (`<currency>/kWh`).
`Current Energy Sell Rate` | Primary | Active energy sell-back rate (`<currency>/kWh`).
`Monthly Energy Rate` | Primary | Tiered monthly energy rate (`<currency>/kWh`) when a meter sensor is configured.
`Current Energy Rate Structure` | Primary | Current TOU / rate structure period name.
`Next Energy Rate Structure` | Primary | Upcoming rate structure period name.
`Next Energy Rate Structure Time` | Primary | Timestamp when the next rate structure begins.
`Plan Name` | Primary | Name of the selected utility rate plan.
`Minimum Charge` | Diagnostic | Minimum billing charge and unit of measurement.
`Fixed Charge (first meter)` | Diagnostic | Fixed monthly/daily charge for the first meter.
`Distributed Generation` | Diagnostic | Distributed generation / net metering details.
`Approval` (`binary_sensor`) | Diagnostic | Whether the OpenEI rate plan is approved.

## Installation

### Home Assistant Marketplace (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Marketplace.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=firstof9&repository=ha-openei&category=integration)

1. Open the **Home Assistant Marketplace** and search for **OpenEI** (or click the button above).
2. Download the integration and restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for **OpenEI Utility Rates**.

### Manual Installation

1. Open your Home Assistant configuration directory (where `configuration.yaml` is located).
2. Create a `custom_components/openei/` directory if it does not already exist.
3. Download all files from `custom_components/openei/` in this repository into that directory.
4. Restart Home Assistant.
5. Go to **Settings → Devices & Services → Add Integration** and search for **OpenEI Utility Rates**.

## Configuration

Configuration is handled entirely through the Home Assistant UI, and settings can be updated later via the **Reconfigure** option on the integration card.

### Step 1: API Key & Location

Enter your OpenEI API key, an optional address/ZIP code (leave blank to use Home Assistant's configured latitude/longitude), and a search radius (`0`–`200` miles):

![step1][step1img]

### Step 2: Select Utility Company

Choose your utility provider from the list returned for your location:

![step2][step2img]

### Step 3: Select Rate Plan & Meter Sensor

Choose your rate plan (or enter a **Manual Plan** ID to override the dropdown), and optionally select an energy meter sensor for tiered monthly rate calculations:

![step3.1][step3-1img]
![step3.2][step3-2img]

## Contributions are welcome!

If you want to contribute to this integration, please read the [Contribution guidelines](CONTRIBUTING.md).

***

[openei]: https://openei.org/
[openei-signup]: https://openei.org/services/api/signup/
[buymecoffee]: https://www.buymeacoffee.com/firstof9
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/firstof9/ha-openei.svg?style=for-the-badge
[commits]: https://github.com/firstof9/ha-openei/commits/master
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/Marketplace-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/firstof9/ha-openei.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Chris%20Nowak%20%40firstof9-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/firstof9/ha-openei.svg?style=for-the-badge
[releases]: https://github.com/firstof9/ha-openei/releases
[step1img]: images/step1.png
[step2img]: images/step2.png
[step3-1img]: images/step3-1.png
[step3-2img]: images/step3-2.png
