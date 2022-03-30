# Prisma SD-WAN Health Checks (Preview)
The purpose of this script is to pull specifc alarm codes and also do some site health checks 

#### License
MIT

#### Requirements
* Active CloudGenix Account - Please generate your API token and add it to cloudgenix_settings.py
* Python >=3.6

#### Installation:
 Scripts directory. 
 - **Github:** Download files to a local directory, manually run the scripts. 
 - pip install -r requirements.txt

### Examples of usage:
 Please generate your API token and add it to cloudgenix_settings.py
 
 1. ./get_errors.py
      - Will produce a csv called errors_results.csv for the past 6 months with codes DEVICESW_CONCURRENT_FLOWLIMIT_EXCEEDED and DEVICESW_FPS_LIMIT_EXCEEDED
	  
 1. ./site_health_check.py
      - Will produce a csv called site_health_check.csv with information on concurrent flows, cpu, memory, code and platform

### Caveats and known issues:
 - This is a PREVIEW release, hiccups to be expected. Please file issues on Github for any problems.

#### Version
| Version | Build | Changes |
| ------- | ----- | ------- |
| **1.0.0** | **b1** | Initial Release. |


#### For more info
 * Get help and additional Prisma SD-WAN Documentation at <https://docs.paloaltonetworks.com/prisma/cloudgenix-sd-wan.html>
