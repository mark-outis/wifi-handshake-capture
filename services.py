"""
This class help to finish system services
"""
from execute_process import Process


class Service:
    """
    This class manipulates the status of the service with systemctl
    """

    def __init__(self):
        pass

    async def network_manager_service(self, status):
        """
        stops the NetworkManager.service
        """
        stop_network_manager_params = [
            'systemctl',
            status,
            'NetworkManager.service'
        ]

        stop_network_manager_process = Process(stop_network_manager_params)
        result, _ = await stop_network_manager_process.see_end_result_process(
            f'{status} NetworkManager.service')

        return result

    async def wpa_supplicant(self, status):
        """
        stops the wpa_supplicant.service
        """
        stop_wpa_supplicant_params = [
            'systemctl',
            status,
            'wpa_supplicant.service'
        ]

        stop_wpa_supplicant_process = Process(stop_wpa_supplicant_params)
        return await stop_wpa_supplicant_process.see_end_result_process(
            f'{status} wpa_supplicant.service')

    async def reset_interface(self, interface="wlan0"):
        """
        Reset system interface
        """
        reset_interface_params = [
            'airmon-ng',
            'stop', interface,
        ]

        reset_interface_process = Process(reset_interface_params)
        await reset_interface_process.see_end_result_process(
            description="Reset interfaces")
        return

    async def reset_wifi_interface(self, interface):
        """
        Reset wifi interface
        """
        wifi_dow_params = [
            'ip',
            'link',
            'set',
            str(interface),
            'down'
        ]
        wifi_dow_process = Process(wifi_dow_params)
        await wifi_dow_process.see_end_result_process(
            description="Dow wifi interface")

        wifi_up_params = [
            'ip',
            'link',
            'set',
            str(interface),
            'up'
        ]
        wifi_up_process = Process(wifi_up_params)
        await wifi_up_process.see_end_result_process(
            description="Up wifi interface")

        return

    async def set_channel(self, interface, channel):
        """
        set channel to interface
        """

        set_channel_params = [
            'iwconfig',
            interface,
            'channel',
            str(channel)
        ]

        set_channel_process = Process(set_channel_params)

        return await set_channel_process.see_end_result_process(
            f'Setting interface {interface} on channel {channel}'
        )

    async def convert_cap_to_hc22000(
        self,
            output_file_name='output',
            file_cap_path=None):
        """
        Convert file .cap to format hc22000
        """
        if not file_cap_path:
            print("File path is required")
            return

        print(f"File to convert {file_cap_path}")

        convert_file_params = [
            'hcxpcapngtool',
            '-o', f"{output_file_name}.hc22000",
            file_cap_path
        ]

        convert_file_process = Process(convert_file_params)

        return await convert_file_process.see_end_result_process(
            "Convert cap file")
