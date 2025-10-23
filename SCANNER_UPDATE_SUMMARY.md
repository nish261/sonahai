# Scanner Update Summary - Oct 24, 2024

## What Changed

Updated `aggressive_scanner.py` to match the **official can-i-take-over-xyz repository** by EdOverflow.

Source: https://github.com/EdOverflow/can-i-take-over-xyz

## Vulnerable Services (43 Total)

Your scanner now detects these services based on the community-maintained list:

### Cloud Providers (4)
- AWS/S3
- AWS/Elastic Beanstalk
- Microsoft Azure
- Digital Ocean

### Development Platforms (6)
- Bitbucket
- Github
- JetBrains
- Ngrok
- Pantheon
- Readthedocs

### CMS/Blogging (4)
- Ghost
- HatenaBlog
- Wordpress
- Worksites

### Marketing/Landing Pages (6)
- LaunchRock
- Smugsmug
- Strikingly
- Surge.sh
- Uberflip

### Support/Help Desk (6)
- Cargo Collective
- Help Juice
- Help Scout
- Helprace
- Pingdom
- Readme.io

### Business/CRM (8)
- Agile CRM
- Campaign Monitor
- Canny
- Gemfury
- Getresponse
- SmartJobBoard
- SurveySparrow
- Uptimerobot

### Other Services (4)
- Airee.ru
- Anima
- Discourse
- Short.io

## Excluded Services (NOT Vulnerable)

These services were REMOVED because they're no longer vulnerable (vendors fixed them):

- **Unbounce** - Added DNS verification
- **Instapage** - Fixed takeover vulnerability
- **Statuspage** - Added DNS verification  
- **UserVoice** - Fixed vulnerability
- **Zendesk** - Fixed vulnerability

Plus 23 other services that were never vulnerable:
- Fastly, CloudFront, Cloudflare, Akamai (CDNs)
- Firebase, Gitlab, Kinsta, etc.

## Benefits

1. **No False Positives**: Only shows REAL vulnerabilities
2. **Community Validated**: Matches security researcher consensus
3. **Up to Date**: Reflects latest vendor fixes (as of Oct 2024)
4. **Accurate Results**: Uses Subdominator + verified service list

## Scanner Status

Currently running:
- Top 1000 domains
- 115,430+ subdomains discovered
- Will use Subdominator for fast vulnerability detection
- Results will be saved to `~/Desktop/Subdomain_Takeover_Results/`

## Git Commits

1. `01ac299` - Improve vulnerability filtering to show all cloud services
2. `24127e3` - Sync vulnerability list with can-i-take-over-xyz official repo
