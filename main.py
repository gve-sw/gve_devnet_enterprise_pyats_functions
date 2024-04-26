from Connection import PYATSConnection
from datetime import datetime


device_testbed = PYATSConnection()
# Format as 'year-month-day'
date = datetime.now()
formatted_date = date.strftime('%Y-%m-%d')
"""
ROUTERS
"""
for device in device_testbed.get_device_by_role(role="router"):
    print(f"Router: {device}")
    # device_testbed.change_trunking_encapsulation_vlan(device=device, current_vlan=1, updated_vlan=128)


"""
SWITCHES
"""
for device in device_testbed.get_device_by_role(role="switch"):
    # device_testbed.save_current_config(device=device, date=formatted_date)
    # device_testbed.search_device_trunk_interfaces(device=device)
    # device_testbed.search_device_access_interfaces(device=device)
    # device_testbed.update_device_access_vlans_on_interfaces(device=device, current_access_vlan=1, updated_access_vlan=128)
    # print(device_testbed.search_and_replace_device_running_config(device=device, search="service timestamps debug datetime msec"))
    device_testbed.update_svi(device=device, svi_interface="Vlan1", updated_svi_interface="Vlan128")


