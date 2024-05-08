import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Check if package is installed
def check_package(package):
    try:
        pkg = __import__(package)
        return True, pkg.__version__
    except ImportError:
        return False, None

# Install package
def install_package(package, manager='pip'):
    if manager == 'conda':
        command = ['conda', 'install', '-c', 'conda-forge', '-y', package]
    else:
        command = [sys.executable, '-m', manager, 'install', package]

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        logging.info(f"Successfully installed {package} using {manager}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install {package} using {manager}. Error: {e.stderr}")
        user_input = input("Would you like to retry the installation? (y/n): ")
        if user_input.lower() == 'y':
            install_package(package, manager)
        else:
            logging.info(f"Skipping installation of {package}. Please install it manually if needed.")

# Main function
def check_and_install_packages(required_packages):
    # Print Python version, manager, and environment name
    manager = 'conda' if 'conda' in sys.version else 'pip'
    env_name = sys.prefix.split('/')[-1] if manager == 'conda' else 'not applicable'
    print(f"Python {sys.version.split()[0]}, Pkg manager: {manager}\nEnv: {env_name}\n")

    for package in required_packages:
        installed, version = check_package(package)
        if not installed:
            user_input = input(f"Package '{package}' is not installed. \U0001F915 Would you like to install it? (y/n): ")
            if user_input.lower() == 'y':
                install_package(package, manager)
                _, new_version = check_package(package)
                print(f"{package} installed, version: {new_version}")
            else:
                print(f"Skipping installation of '{package}'. Please install it manually if needed.")
        else:
            print(f"{package} ✔, version: {version}")
    print("\nAll packages are installed.\U0001F607")

if __name__ == "__main__":
    default_packages = ['numpy', 'pandas', 'netCDF4', 'matplotlib', 'cartopy']
    check_and_install_packages(default_packages)