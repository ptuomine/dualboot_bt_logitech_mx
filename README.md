# Bluetooth Key Extraction and Info File Update

This repository contains a script to extract Bluetooth keys from a Windows registry and update corresponding info files on a Linux system.

This works atleast on Logitech MX Anywhere 2S mouse and Logitech K850 keyboard.

- put your info file(s) to info_files dir
- the updated info file is saved to generated dir
- update the directory paths in the main method

NOTE: You will have to change the bluetooth device mac address in your linux configuration to match with the windows one


## generate_info.py

The `generate_info.py` script performs the following tasks:

1. **Mounts the Filesystem**: Mounts the specified Windows filesystem if it is not already mounted.
2. **Navigates the Windows Registry**: Uses `chntpw` to navigate the Windows registry and extract Bluetooth keys.
3. **Extracts Bluetooth Keys**: Extracts the following Bluetooth keys from the registry:
    - Long Term Key (LTK)
    - Identity Resolving Key (IRK)
    - Connection Signature Resolving Key (CSRK)
    - Encryption Random Value (ERand)
    - Encryption Diversifier (EDIV)
    - Key Length
4. **Updates Info Files**: Updates the selected info file with the extracted keys.
5. **Saves the Updated File**: Saves the updated info file to a specified directory.

### Usage

1. Ensure the necessary dependencies are installed:
    - `pexpect`
    - `subprocess`
    - `os`
    - `re`

2. Run the script:
    ```bash
    python generate_info.py
    ```

3. Follow the prompts to navigate the registry and select the appropriate directories and info file.

### Example

```bash
$ python generate_info.py
Available directories:
0: <directory1>
1: <directory2>
Choose a directory to cd into: 0
Available directories:
0: <subdirectory1>
1: <subdirectory2>
Choose a directory to cd into: 1
Available info files:
0: info_file1
1: info_file2
Choose an info file: 0
Updated info file written to /media/pasi/Data/Git/home/ubuntu/bluetooth/generated/info_file1