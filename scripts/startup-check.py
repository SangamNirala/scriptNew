#!/usr/bin/env python3
"""
Startup Check Script for Enhanced Prompt Template System
This script runs before the backend starts to ensure all dependencies are installed
"""

import subprocess
import sys
import os
import json
import importlib
from datetime import datetime
from pathlib import Path

# Critical packages that must be available
CRITICAL_PACKAGES = {
    'emergentintegrations': 'emergentintegrations',
    'edge_tts': 'edge-tts',
    'deep_translator': 'deep-translator', 
    'cv2': 'opencv-python',
    'sklearn': 'scikit-learn',
    'lxml': 'lxml[html_clean]',
    'newspaper': 'newspaper3k',
    'serpapi': 'serpapi',
    'pydub': 'pydub',
    'textstat': 'textstat',
    'motor': 'motor',
    'pymongo': 'pymongo'
}

def log(message, level="INFO"):
    """Log with timestamp and level"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    levels = {
        "INFO": "🔵",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌"
    }
    icon = levels.get(level, "📝")
    print(f"[{timestamp}] {icon} {message}")

def check_package_available(import_name):
    """Check if a package can be imported"""
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def install_package(package_name, pip_name=None):
    """Install a package using pip"""
    pip_name = pip_name or package_name
    try:
        log(f"Installing {pip_name}...", "INFO")
        
        # Special handling for emergentintegrations
        if pip_name == 'emergentintegrations':
            cmd = [
                sys.executable, '-m', 'pip', 'install', 'emergentintegrations',
                '--extra-index-url', 'https://d33sy5i8bnduwe.cloudfront.net/simple/'
            ]
        else:
            cmd = [sys.executable, '-m', 'pip', 'install', pip_name]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            log(f"Successfully installed {pip_name}", "SUCCESS")
            return True
        else:
            log(f"Failed to install {pip_name}: {result.stderr}", "WARNING")
            return False
            
    except subprocess.TimeoutExpired:
        log(f"Timeout installing {pip_name}", "ERROR")
        return False
    except Exception as e:
        log(f"Error installing {pip_name}: {str(e)}", "ERROR")
        return False

def run_installation_script():
    """Run the main installation script"""
    try:
        script_path = "/app/scripts/install-requirements.sh"
        if os.path.exists(script_path):
            log("Running comprehensive installation script...", "INFO")
            result = subprocess.run(["/bin/bash", script_path], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                log("Installation script completed successfully", "SUCCESS")
                return True
            else:
                log(f"Installation script failed: {result.stderr}", "WARNING")
                return False
        else:
            log(f"Installation script not found: {script_path}", "WARNING")
            return False
    except Exception as e:
        log(f"Error running installation script: {str(e)}", "ERROR")
        return False

def main():
    """Main startup check function"""
    log("🚀 Enhanced Prompt Template System - Startup Check", "INFO")
    log("📋 Checking critical dependencies...", "INFO")
    
    # Check if installation status file exists (from previous run)
    status_file = "/tmp/installation_status.json"
    if os.path.exists(status_file):
        try:
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            # If installation was completed recently (within 1 hour), skip
            install_time = datetime.fromisoformat(status['timestamp'].replace('Z', '+00:00'))
            time_diff = (datetime.now().astimezone() - install_time).total_seconds()
            
            if time_diff < 3600 and status.get('installation_completed', False):
                log("Recent installation found, skipping dependency check", "SUCCESS")
                # Still do a quick check of critical packages
                missing_packages = []
                for import_name in CRITICAL_PACKAGES.keys():
                    if not check_package_available(import_name):
                        missing_packages.append(import_name)
                
                if not missing_packages:
                    log("All critical packages available", "SUCCESS")
                    return True
                else:
                    log(f"Some packages missing: {missing_packages}", "WARNING")
        except Exception as e:
            log(f"Error reading installation status: {str(e)}", "WARNING")
    
    # Check current package availability
    missing_packages = []
    available_packages = []
    
    for import_name, pip_name in CRITICAL_PACKAGES.items():
        if check_package_available(import_name):
            available_packages.append(import_name)
            log(f"✅ {import_name}", "SUCCESS")
        else:
            missing_packages.append((import_name, pip_name))
            log(f"❌ {import_name}", "ERROR")
    
    # If some packages are missing, run installation
    if missing_packages:
        log(f"Missing {len(missing_packages)} critical packages", "WARNING")
        log("Starting automatic installation...", "INFO")
        
        # Run comprehensive installation script first
        run_installation_script()
        
        # Then try individual package installation for any still missing
        for import_name, pip_name in missing_packages:
            if not check_package_available(import_name):
                install_package(import_name, pip_name)
        
        # Final verification
        final_missing = []
        for import_name, pip_name in missing_packages:
            if not check_package_available(import_name):
                final_missing.append(import_name)
        
        if final_missing:
            log(f"⚠️  Still missing packages: {final_missing}", "WARNING")
            log("Backend may have limited functionality", "WARNING")
        else:
            log("🎉 All packages now available!", "SUCCESS")
    
    else:
        log("🎉 All critical packages are available!", "SUCCESS")
    
    # Create success status file
    status = {
        "startup_check_completed": True,
        "timestamp": datetime.now().isoformat(),
        "available_packages": available_packages,
        "missing_packages": [pkg[0] for pkg in missing_packages if not check_package_available(pkg[0])],
        "total_checked": len(CRITICAL_PACKAGES),
        "success_rate": f"{len(available_packages) / len(CRITICAL_PACKAGES) * 100:.1f}%"
    }
    
    with open("/tmp/startup_check_status.json", 'w') as f:
        json.dump(status, f, indent=2)
    
    log("✅ Startup check completed - Backend ready to start", "SUCCESS")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("Startup check interrupted", "WARNING")
        sys.exit(1)
    except Exception as e:
        log(f"Unexpected error during startup check: {str(e)}", "ERROR")
        sys.exit(1)