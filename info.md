
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Component to integrate with [OpenEI.org][openei]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Show info from OpenEI's API.


{% if not installed %}
## Installation

1. Click install.
2. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "OpenEI Utility Rates"

{% endif %}


## Configuration is done in the UI


Step 1: Enter your API Key:

![step1][step1img]

Step 2: Select your utility company:

![step2][step2img]

Step 3.1: Select your rate plan:

![step3.1][step3-1img]
![step3.2][step3-2img]

<!---->

***

[openei]: https://openei.org/
[buymecoffee]: https://www.buymeacoffee.com/firstof9
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/firstof9/ha-openei.svg?style=for-the-badge
[commits]: https://github.com/firstof9/ha-openei/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
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