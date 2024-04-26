# gve_devnet_enterprise_pyats_functions
This application uses PYATS in python to automate the transfer of VLANs and trunking ports on routers and switches. 


## Contacts
* Charles Llewellyn

## Solution Components
* ISR
*  Catalyst
*  Flask
*  Python

## Installation/Configuration

1. Update/replace the testbed.yaml file in the res/directory with device information from your enivronment. The "role" variable is used to differentiate switches and routers. This is not required, but you will need to create your own logic to interact with your testbed devices.
2. Create Python Virtual Environment ```python3 -m venv venv```
3. Use the virtual environment ```source venv/bin/activate```
4. Install requirements ```pip install -r requirements.txt```



## Usage

    $ python main.py



# Screenshots

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
