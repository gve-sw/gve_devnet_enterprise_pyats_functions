from prettyprinter import pprint
from genie.testbed import load
from unicon.eal.dialogs import Dialog, Statement


# Function to handle the prompt
def handle_destination_prompt(spawn, session, context):
    spawn.sendline('')  # Sending an empty line as response to accept the default


class PYATSConnection:
    def __init__(self):
        self.__testbed = load("./res/testbeds/testbed.yaml")

    def get_device_by_role(self, role):
        """
        Retrieves a list of devices that match a specific role from the testbed. 
        This function filters devices based on their assigned role attribute, useful for targeting specific types of devices in network scripts.
        """
        return [device for device in self.__testbed.devices.values() if device.role == role]

    def __find_device_by_ip(self, ip):
        """
        Searches for and returns a device object based on its IP address. 
        This function iterates through all devices in the testbed, checking each one's SSH connection IP address against the provided IP.
        """
        for device_name, device in self.__testbed.devices.items():
            if ip == str(device.connections['ssh']['ip']):
                return device

        return None

    def get_device_running_config(self, device):
        """
        Connects to a specified device and retrieves its running configuration using the learn('config') method from PyATS, 
        which abstracts and structures the device's configuration.
        """
        if device is not None:
            pprint(type(device))
            device.connect(init_config_commands=[])
            return device.learn('config')
        else:
            return None

    def search_and_replace_device_running_config(self, device, search="ip tacacs source-interface Vlan1"):
        """
        Searches for a specific configuration line within a device's running configuration and replaces it if found. 
        It demonstrates modifying device configurations programmatically, such as changing TACACS source interface settings.
        """
        if device is not None:
            device.connect(init_config_commands=[])
            output = device.execute(f'show run | include {search}')
            print(f"output of {search}: {output}")
            if search in output:
                # Unconfigure the old source interface and configure the new one
                device.configure('no ip tacacs source-interface Vlan1')
                device.configure('ip tacacs source-interface Vlan128')
        else:
            return None

    def search_device_trunk_interfaces(self, device):
        """
        Examines a device for trunk interfaces and adjusts VLAN settings on those trunks. 
        It also provides an example of how to parse and modify interface configurations based on operational and administrative criteria.
        """
        if device is not None:
            device.connect(init_config_commands=[])
            interfaces = device.parse('show interfaces switchport')
            for interface_name, interface_data in interfaces.items():
                operational_mode = interface_data.get("operational_mode", "")
                administrative_mode = interface_data.get("switchport_mode", "")
                if operational_mode == "trunk" and administrative_mode == "trunk":
                    vlan_list = []
                    trunk_vlans = interface_data.get('trunk_vlans', '')
                    # Handle VLAN ranges like "800-900"
                    for vlan_range in trunk_vlans.split(','):
                        if '-' in vlan_range:
                            start_vlan, end_vlan = vlan_range.split('-')
                            vlan_list.extend(range(int(start_vlan), int(end_vlan) + 1))
                        else:
                            if vlan_range:
                                if vlan_range != "all":
                                    vlan_list.append(int(vlan_range))

                    config_commands = [f"interface {interface_name}"]

                    # Check if VLAN 128 is in the list
                    print(f"{interface_name} VLAN LIST: {vlan_list}")

                    if 128 not in vlan_list:
                        config_commands += [
                            "switchport trunk allowed vlan add 128"
                        ]
                    if 1 in vlan_list:
                        config_commands += [
                            "switchport trunk allowed vlan remove 1"
                        ]
                    if len(config_commands) > 1:
                        print(config_commands)
                        device.configure(config_commands)
        else:
            return None

    def change_trunking_encapsulation_vlan(self, device, current_vlan: int, updated_vlan: int):
        """
        Examines a device for trunk interfaces and adjusts VLAN settings on those trunks. 
        It also provides an example of how to parse and modify interface configurations based on operational and administrative criteria.
        """
        if device is not None:
            device.connect(init_config_commands=[])
            interfaces = device.parse('show ip interface brief')
            for interface_name, interface_data in interfaces["interface"].items():
                print(interface_name)
                if "." in interface_name:
                    interface_details = device.parse(f'show interface {interface_name}')
                    if interface_details[interface_name]['encapsulations']['encapsulation'] == "dot1q" and int(
                            interface_details[interface_name]['encapsulations']['first_dot1q']) == current_vlan:
                        config_commands = [f"interface {interface_name}", f"encapsulation dot1Q {updated_vlan} native"]
                        device.configure(config_commands)

    def update_device_access_vlans_on_interfaces(self, device, current_access_vlan: int, updated_access_vlan: int):
        """
        Updates the access VLANs on all interfaces of a device that are set to a specific VLAN. 
        This function can be crucial in network migrations or reconfigurations where VLAN changes are common.
        """
        if device is not None:
            device.connect(init_config_commands=[])
            interfaces = device.parse('show interfaces switchport')
            for interface_name, interface_data in interfaces.items():
                operational_mode = interface_data.get("operational_mode", "")
                administrative_mode = interface_data.get("switchport_mode", "")
                print(interface_data)
                input()
                if operational_mode == "static access" or operational_mode == "down":  # ACCESS, DOWN, TRUNK
                    if administrative_mode == "static access":  # TRUNK OR ACCESS
                        access_vlan = interface_data['access_vlan']
                        if current_access_vlan == int(access_vlan):
                            config_commands = [f'interface {interface_name}',
                                               f"switchport access vlan {updated_access_vlan}",
                                               f"authentication event server dead action reinitialize vlan {updated_access_vlan}"]
                            device.configure(config_commands)

    def save_current_config(self, device, date):
        """
        Saves the current configuration of the device to its local storage. 
        This function includes handling for prompts that may appear during the save process, 
        making it robust for automated scripts.
        """
        if device is not None:
            # Create the dialog
            dialog = Dialog([
                Statement(pattern=r'Destination filename \[(.*)\]\?',
                          action=handle_destination_prompt,
                          loop_continue=True,
                          continue_timer=False)
            ])

            device.connect(init_config_commands=[])
            device.execute(f"copy run flash:sh-run-{date}.txt", reply=dialog)


    def update_svi(self, device, svi_interface, updated_svi_interface):
        """
        Copies the configuration from one switched virtual interface (SVI) to another and shuts down the original SVI. 
        This function demonstrates advanced manipulation of interface configurations, 
        useful for significant network restructurings or consolidations.
        """
        if device is not None:
            device.connect(init_config_commands=[])
            # Execute command to get the configuration for the specified SVI interface
            output = device.execute(f'show run interface {svi_interface}')

            # Initialize a list to hold the configuration commands
            config_commands = []
            capturing = False

            # Process each line in the output to capture the relevant configuration
            for line in output.splitlines():
                # Check if the current line is the start of the interface configuration
                if line.strip().startswith(f"interface {svi_interface}"):
                    capturing = True
                    continue  # Skip adding the interface declaration line itself

                # Check if we are currently capturing and if the line is not a sub-interface or another main interface
                if capturing and line.startswith(' interface'):
                    break  # Stop capturing on encountering a new interface definition

                # If capturing, add the line to our commands list
                if capturing:
                    config_commands.append(line.strip())

            #Default the old interface
            shutdown_interface_commands = [f"default interface {svi_interface}",f"interface {svi_interface}", f"shut"]
            device.configure(shutdown_interface_commands)
            # Prepare the new interface configuration commands
            new_interface_commands = [f"interface {updated_svi_interface}"] + config_commands

            # Apply configuration to the new interface
            try:
                device.configure(new_interface_commands)
                print(f"Configuration successfully applied to {updated_svi_interface}")
            except Exception as e:
                print(f"Error during configuration transfer: {str(e)}")



