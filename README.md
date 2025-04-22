# WiFi Handshake Capture and Hash Generation for Auditing with Hashcat

This procedure describes a security auditing approach for protected WiFi networks (WPA/WPA2/WPA3) by capturing packets and generating hash files compatible with Hashcat for further analysis.

> ⚠️ **Ethical Use**: This process should only be used on your own networks or with explicit authorization. Unauthorized access to networks is illegal.  
> ⚠️ **Important**: This **is not the most efficient method** for cracking WiFi passwords, as it requires significant computational power, especially for brute-force attacks on complex passwords. However, **it is useful for learning how to capture packets, understanding the WPA/WPA2 authentication process, and practicing security analysis**.  
> It can also be effective on networks with weak passwords, especially when combined with dictionaries or optimized brute-force patterns.

---

## ✅ System Requirements

To carry out this procedure, ensure the following tools are installed at the operating system level:

### 🛠️ Required Programs

- `aircrack-ng`
- `tcpdump`
- `hcxpcapngtool`
- `hashcat`
- `iw`, `iwconfig`, `systemctl` (basic network management commands in Linux)

### 🐍 Required Python Version

- Python **3.11** or higher is required to run the automation scripts.

### 🧪 Tested Operating Systems

- ✅ **Kali Linux**
- ✅ **Parrot OS**

These systems already include most of these tools pre-installed or easily installable from their repositories.

---

## 🧭 General Process Flow

### 1. Identifying WiFi Interfaces

Available wireless interfaces are inspected using tools like `iw` to verify compatibility and status.

### 2. Environment Preparation

Services like `NetworkManager` and `wpa_supplicant` are stopped to avoid conflicts with enabling monitor mode.

### 3. Enabling Monitor Mode

Monitor mode allows the network card to capture WiFi traffic packets without being connected to a network.

### 4. Packet Capture

A general scan of the wireless spectrum is performed, selecting a specific network to focus on a target.

### 5. Sending Deauthentication Packets

Reconnections of devices connected to a target network are forced to facilitate handshake capture.

### 6. Handshake Capture

Once the target is identified and a connected client is deauthenticated, **`airodump-ng`** is used to capture the **WPA/WPA2 handshake**.  
This handshake is the key exchange that occurs when a device connects to the WiFi network and can be analyzed later to attempt password cracking.

The tool saves the packets in a file that will serve as the basis for extracting the hash and performing the brute-force attack.

### 7. Conversion to Hashcat-Compatible Format

Once the handshake is captured, the generated `.cap` file is converted to the `.hc22000` format using tools like `hcxpcapngtool`.

This file is the one **that can later be used with Hashcat** to perform a brute-force or dictionary attack.

> ⚠️ **Important**: At this step, **the password is not decrypted**, only the necessary file is prepared for Hashcat to use.  
> The actual cracking stage (decryption) requires running Hashcat on a system with sufficient processing power (preferably with a GPU).

### 8. Restoring the Environment

Once the audit is complete, network services are restarted to return the system to its original state.

---

## ⚡ Advantages of Using `asyncio` to Run Subprocesses

Using `asyncio` in Python automation scripts is especially convenient for this type of audit because:

- **It’s native to Python**  
  `asyncio` has been part of Python’s standard library since version 3.4, so **no external packages are needed** to leverage asynchronous programming and concurrency.

- **Non-blocking execution**  
  It allows launching multiple system commands without blocking the script’s execution, significantly improving efficiency.

- **Optimized performance**  
  By running multiple tasks in parallel (such as capturing packets while monitoring other interfaces), the total execution time is reduced.

- **Better process and error handling**  
  It provides full control over each subprocess: you can read its output, detect errors, or cleanly cancel tasks.

- **Perfect for integration with other apps**  
  Ideal when automating this flow within an API, desktop tool, or web application with real-time responses.

- **Simple scalability**  
  Being asynchronous, it’s easy to scale the script to work with multiple interfaces or perform tests in parallel.

In summary, `asyncio` allows creating faster, lighter, and more robust scripts without relying on external libraries, making it perfect for controlled environments like Kali or Parrot.
