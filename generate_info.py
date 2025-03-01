import os
import subprocess
import pexpect
import re


def clean_string(s):
    """Removes leading/trailing spaces and the first/last character of the string."""
    s = s.strip()
    return s[1:-1] if len(s) > 1 else ''


def clean_hex_string(s):
    """Extracts and returns the hex string from a formatted input."""
    hex_values = re.findall(r'[0-9A-Fa-f]{2}', s.split('  ')[1])  # Extract hex values
    return ''.join(hex_values)


def mount_filesystem(mount_point, device):
    """Mount the filesystem if it is not already mounted."""
    if not os.path.ismount(mount_point):
        subprocess.run(["sudo", "mount", device, mount_point])


def change_directory(child, path):
    """Navigates to a specific directory in the child process."""
    child.sendline(f"cd {path}")
    child.expect(f"(.*)>")
    

def list_and_choose_directory(child, expected_prompt):
    """Lists directories and prompts the user to select one."""
    child.sendline("ls")
    child.expect(expected_prompt)
    output = child.before.decode().splitlines()
    filtered_dirs = [line.strip() for line in output[1:] if re.match(r"<.*>", line.strip())]
    
    print("Available directories:")
    for i, d in enumerate(filtered_dirs):
        print(f"{i}: {d}")
    
    choice = int(input("Choose a directory to cd into: "))
    return clean_string(filtered_dirs[choice])


def get_keys(child, bluetooth_dir, device_dir, keys):
    """Retrieves hex values for the given keys from the chntpw child process."""
    key_values = {}
    for key in keys:
        child.sendline(f"hex {key}")
        child.expect(fr"(...)\\Parameters\\Keys\\{bluetooth_dir}\\{device_dir}>")  # Expect the same prompt
        output = child.before.decode().splitlines()[2]
        key_values[key] = clean_hex_string(output)
    return key_values


def update_info_file(info_file_path, key_values):
    """Reads and updates the selected info file with the key values."""
    with open(info_file_path, "r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith("Key="):
            if "[IdentityResolvingKey]" in lines[i-1]:
                lines[i] = f"Key={key_values['IRK']}\n"
            elif "[LocalSignatureKey]" in lines[i-1]:
                lines[i] = f"Key={key_values['CSRK']}\n"
            elif "[LongTermKey]" in lines[i-1]:
                lines[i] = f"Key={key_values['LTK']}\n"
        elif line.startswith("EncSize="):
            lines[i] = f"EncSize={int(key_values['KeyLength'], 16)}\n"
        elif line.startswith("EDiv="):
            lines[i] = f"EDiv={int(key_values['EDIV'], 16)}\n"
        elif line.startswith("Rand="):
            erand_reversed = "".join(reversed([key_values['ERand'][i:i+2] for i in range(0, len(key_values['ERand']), 2)]))
            lines[i] = f"Rand={int(erand_reversed, 16)}\n"

    return lines


def save_updated_file(lines, original_file_path, generated_dir):
    """Saves the updated lines to a new file in the 'generated' directory."""
    os.makedirs(generated_dir, exist_ok=True)
    new_file_path = os.path.join(generated_dir, os.path.basename(original_file_path))
    with open(new_file_path, "w") as file:
        file.writelines(lines)
    
    print(f"Updated info file written to {new_file_path}")
    return new_file_path


def main():
    # Set up paths and parameters
    mount_point = "/media/pasi/windows-ssd/"
    device = "/dev/nvme0n1p3"
    info_files_dir = r"/media/pasi/Data/Git/home/ubuntu/bluetooth/info_files"
    generated_dir = "/media/pasi/Data/Git/home/ubuntu/bluetooth/generated"
    keys = ["LTK", "IRK", "CSRK", "ERand", "EDIV", "KeyLength"]
    
    # Mount the filesystem
    mount_filesystem(mount_point, device)
    
    os.chdir("/media/pasi/windows-ssd/Windows/System32/config")
    
    # Start chntpw process
    child = pexpect.spawn("chntpw -e SYSTEM")

    # Navigate to ControlSet001\Services\BTHPORT\Parameters\Keys
    child.expect(">")
    child.sendline("cd ControlSet001\\Services\\BTHPORT\\Parameters\\Keys")
    child.expect(r"(...)\\Services\\BTHPORT\\Parameters\\Keys>")
    
    # Navigate to BTHPORT\Parameters\Keys directory
    expected_prompt=r"(...)\\Services\\BTHPORT\\Parameters\\Keys>"
    bluetooth_dir = list_and_choose_directory(child, expected_prompt)
    change_directory(child, f"{bluetooth_dir}")
    
    # Select the device directory
    expected_prompt=r"(...)\\BTHPORT\\Parameters\\Keys\\"+bluetooth_dir+">"
    device_dir = list_and_choose_directory(child, expected_prompt)
    change_directory(child, f"{device_dir}")
    
    # Retrieve key values
    key_values = get_keys(child, bluetooth_dir, device_dir, keys)
    
    # Quit chntpw process
    child.sendline("q")
    child.expect(pexpect.EOF)
    
    # List files in the info_files directory and prompt for selection
    info_files = [f for f in os.listdir(info_files_dir) if os.path.isfile(os.path.join(info_files_dir, f))]
    print("Available info files:")
    for i, f in enumerate(info_files):
        print(f"{i}: {f}")
    choice = int(input("Choose an info file: "))
    info_file_path = os.path.join(info_files_dir, info_files[choice])
    
    # Update the info file
    updated_lines = update_info_file(info_file_path, key_values)
    
    # Save the updated file
    save_updated_file(updated_lines, info_file_path, generated_dir)


if __name__ == "__main__":
    main()
