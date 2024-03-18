import subprocess

# List of packages to be installed
required_packages = [
    "unittest",
    "requests",
    "threading",
    "time",
    "pymongo",
    "pyyaml",
    "langdetect",
    "python-Levenshtein",
    "fuzzywuzzy"
]

def install_pip():
    try:
        subprocess.check_call(['python', '-m', 'pip', '--version'])
        print("All good, bombs away!")
    except subprocess.CalledProcessError:
        print("Missing pip, making it better now...")
        subprocess.check_call(['python', '-m', 'ensurepip', '--default-pip'])

def install_packages(package_list):
    installed_packages = []
    for package in package_list:
        try:
            subprocess.check_call(['pip', 'install', package])
            installed_packages.append(package)
        except subprocess.CalledProcessError:
            print(f"Error installing {package}.")
    
    return installed_packages

def check_install_imports():
    installed_packages = []
    missing_packages = [package for package in required_packages if not package_exists(package)]
    
    if missing_packages:
        print("The following packages are missing and will be installed:")
        print(missing_packages)
        installed_packages = install_packages(missing_packages)
    
    if installed_packages:
        print("The following packages were installed:")
        print(installed_packages)
    else:
        print("All required packages were already installed.")

def package_exists(package):
    try:
        __import__(package)
        return True
    except ImportError:
        return False

if __name__ == "__main__":
    install_pip()
    check_install_imports()
