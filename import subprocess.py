import subprocess
import sys

def get_package_metadata(package_name):
    result = subprocess.run([sys.executable, "-m", "pip", "show", package_name], capture_output=True, text=True)
    print(result.stdout)

# Example usage
get_package_metadata("pywin32")