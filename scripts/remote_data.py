# Currently Not a working module!! DO NOT USE

import os
import platform
import subprocess

# Check for google colab
try:
    import google.colab
    in_colab = True
except ImportError:
    in_colab = False

def mount_remote_data(local_mount, remote_user, remote_host, remote_path, password):
    """
    Mounts a remote dataset directory using SSHFS.

    Args:
        local_mount (str): Local directory to mount the remote dataset.
        remote_user (str): SSH username for the remote server.
        remote_host (str): Remote server hostname.
        remote_path (str): Path to the dataset on the remote server.

    Usage:
        mount_remote_data("data", "student123", "gpu3.slu.edu", "/datasets/projectX")
    """
    
    system = platform.system()

    # Ensure the local mount directory exists
    os.makedirs(local_mount, exist_ok=True)

    if in_colab:  # Running in Google Colab
        print("🔹 Detected Google Colab. Installing SSHFS...")
        
        # Install SSHFS in Colab if not already installed
        if subprocess.run(["which", "sshfs"], capture_output=True).returncode != 0:
            subprocess.run("apt-get update && apt-get install -y sshfs sshpass", shell=True, check=True)
        
        print("✅ SSHFS installed. Attempting to mount remote dataset...")

        # Mount the remote directory
        sshfs_cmd = f"sshpass -p '{password}' sshfs {remote_user}@{remote_host}:{remote_path} {local_mount} -o reconnect,allow_other -vvv"
        
    elif system == "Darwin":  # macOS
        print("🔹 Detected macOS. Checking for SSHFS...")

        # Check if SSHFS is installed
        if subprocess.run(["which", "sshfs"], capture_output=True).returncode != 0:
            print("❌ SSHFS is not installed. Install it using:")
            print("   brew install macfuse && brew install gromgit/fuse/sshfs-mac")
            return

        # Mount the remote directory
        sshfs_cmd = f"sshfs {remote_user}@{remote_host}:{remote_path} {local_mount} -o reconnect,allow_other"
    
    elif system == "Windows":  # Windows (WinFSP + SSHFS-Win)
        print("🔹 Detected Windows. Checking for SSHFS...")

        # Check if SSHFS-Win is installed
        sshfs_path = subprocess.run(["where", "sshfs"], capture_output=True, text=True)
        if "Could not find files" in sshfs_path.stdout:
            print("❌ SSHFS-Win is not installed. Install it from:")
            print("   https://github.com/billziss-gh/sshfs-win/releases")
            return

        # Windows requires `net use` command to mount network drives
        sshfs_cmd = f'net use {local_mount} \\\\sshfs\\{remote_user}@{remote_host} /persistent:yes'

    elif system == "Linux":  # Linux (Ubuntu)
        print("🔹 Detected Linux. Checking for SSHFS...")

        # Check if SSHFS is installed
        if subprocess.run(["which", "sshfs"], capture_output=True).returncode != 0:
            print("❌ SSHFS is not installed. Install it using:")
            print("   sudo apt install sshfs")
            return

        # Mount the remote directory
        sshfs_cmd = f"sshfs {remote_user}@{remote_host}:{remote_path} {local_mount} -o reconnect,allow_other"

    else:
        print(f"❌ Unsupported OS: {system}. Cannot mount remote data.")
        return

    # Execute SSHFS mount command
    try:
        print(sshfs_cmd)
        subprocess.run(sshfs_cmd, shell=True, check=True)
        print(f"✅ Successfully mounted {remote_host}:{remote_path} to {local_mount}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to mount remote dataset!")
        print(f"📄 STDOUT: {e.stdout}")
        print(f"📄 STDERR: {e.stderr}")
        print(f"🔍 Exit Code: {e.returncode}")
