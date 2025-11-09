"""
Build script for BF6 Crash Monitor
Run this from your activated venv
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   BF6 Crash Monitor - Build Script                    ║
    ║   Run this from your activated venv                    ║
    ╚════════════════════════════════════════════════════════╝
    """)

    # Check if we're in a venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Virtual environment detected")
    else:
        print("⚠ Warning: Not running in a virtual environment")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version}")

    # Check if psutil is installed
    print("\n" + "="*60)
    print("Checking dependencies...")
    print("="*60)

    try:
        import psutil
        print(f"✓ psutil is installed (version {psutil.__version__})")
    except ImportError:
        print("✗ psutil not found, installing...")
        if not run_command(f'"{sys.executable}" -m pip install psutil', "Installing psutil"):
            print("\n✗ Failed to install psutil")
            return

    # Check/install PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller is installed")
    except ImportError:
        print("✗ PyInstaller not found, installing...")
        if not run_command(f'"{sys.executable}" -m pip install pyinstaller', "Installing PyInstaller"):
            print("\n✗ Failed to install PyInstaller")
            return

    # Build the executable
    print("\n" + "="*60)
    print("Building executable...")
    print("="*60)
    print("This may take a few minutes...\n")

    build_cmd = f'"{sys.executable}" -m PyInstaller --onefile --windowed --name "BF6CrashMonitor" --clean crash_monitor.py'

    if not run_command(build_cmd, "Running PyInstaller"):
        print("\n✗ Build failed!")
        return

    # Check if the executable was created
    exe_path = Path("dist") / "BF6CrashMonitor.exe"

    if exe_path.exists():
        print("\n" + "="*60)
        print("✓ BUILD SUCCESSFUL!")
        print("="*60)
        print(f"\nExecutable location: {exe_path.absolute()}")
        print(f"Size: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")
        print("\nFiles to send to your friend:")
        print(f"  1. {exe_path.absolute()}")
        print(f"  2. {Path('QUICK_START.txt').absolute()}")
        print("\n" + "="*60)
    else:
        print("\n✗ Build completed but executable not found!")
        print("Check the output above for errors.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user.")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
