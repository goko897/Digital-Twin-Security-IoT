import subprocess
import sys

# List of required packages
packages = [
    "openvino-dev",
    "openvino-telemetry",
    "nncf",
    "tensorflow",
    "onnx",
    "torch",
    "torchvision",
    "transformers",
    "jupyterlab",
    "ipywidgets",
    "ipykernel",
    "ipython",
    "numpy",
    "opencv-python",
    "Pillow",
    "matplotlib",
    "scipy",
    "scikit-image",
    "setuptools"
]

# Install each package using pip
def install_packages():
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")

if __name__ == "__main__":
    install_packages()
    print("\nAll packages installed successfully!")