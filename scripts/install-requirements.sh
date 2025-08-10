#!/bin/bash

# Automated Dependency Installation Script for Enhanced Prompt Template System
# This script ensures all required dependencies are installed before starting the backend

echo "🚀 Starting Enhanced Prompt Template System - Dependency Installation..."
echo "📁 Project: Enhanced Prompt Template System (Phase 1.1-2.2)"
echo "⏰ Timestamp: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log with timestamp
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌ $1${NC}"
}

# Change to backend directory
cd /app/backend || {
    log_error "Failed to change to /app/backend directory"
    exit 1
}

log "📂 Working directory: $(pwd)"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    log_error "requirements.txt not found in /app/backend"
    exit 1
fi

log_success "Found requirements.txt"

# Create a lock file to prevent multiple simultaneous installations
LOCK_FILE="/tmp/install_requirements.lock"
if [ -f "$LOCK_FILE" ]; then
    log_warning "Another installation is in progress. Waiting..."
    while [ -f "$LOCK_FILE" ]; do
        sleep 2
    done
    log_success "Previous installation completed"
    exit 0
fi

# Create lock file
touch "$LOCK_FILE"

# Cleanup function
cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT

# Update pip to latest version
log "📦 Updating pip to latest version..."
python -m pip install --upgrade pip > /dev/null 2>&1
if [ $? -eq 0 ]; then
    log_success "Pip updated successfully"
else
    log_warning "Pip update failed, continuing with current version"
fi

# Install standard requirements
log "📋 Installing packages from requirements.txt..."
pip install -r requirements.txt > /tmp/install_log.txt 2>&1
if [ $? -eq 0 ]; then
    log_success "Standard requirements installed successfully"
else
    log_error "Failed to install some standard requirements"
    echo "📄 Installation log:"
    cat /tmp/install_log.txt
fi

# Install emergentintegrations with special index
log "🔧 Installing emergentintegrations with special index..."
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ > /tmp/emergent_install.txt 2>&1
if [ $? -eq 0 ]; then
    log_success "emergentintegrations installed successfully"
else
    log_warning "emergentintegrations installation had issues, checking if already installed..."
    python -c "import emergentintegrations; print('emergentintegrations is available')" 2>/dev/null
    if [ $? -eq 0 ]; then
        log_success "emergentintegrations is already available"
    else
        log_error "emergentintegrations installation failed"
        echo "📄 Installation log:"
        cat /tmp/emergent_install.txt
    fi
fi

# Install specific packages that commonly cause issues
CRITICAL_PACKAGES=(
    "edge-tts>=7.2.0"
    "deep-translator>=1.11.4"
    "opencv-python>=4.8.0"
    "scikit-learn>=1.7.0"
    "lxml[html_clean]>=6.0.0"
    "newspaper3k>=0.2.8"
    "serpapi>=0.1.5"
    "google-search-results>=2.4.2"
    "pydub>=0.25.1"
    "textstat>=0.7.8"
)

log "🎯 Installing critical packages individually..."
for package in "${CRITICAL_PACKAGES[@]}"; do
    package_name=$(echo "$package" | cut -d'>' -f1 | cut -d'=' -f1)
    log "   Installing $package_name..."
    pip install "$package" > /tmp/individual_install.txt 2>&1
    if [ $? -eq 0 ]; then
        log_success "   $package_name installed"
    else
        # Check if package is already available
        python -c "import $package_name" 2>/dev/null
        if [ $? -eq 0 ]; then
            log_success "   $package_name already available"
        else
            log_warning "   $package_name installation failed, but continuing..."
        fi
    fi
done

# Verify critical imports
log "🔍 Verifying critical package imports..."
CRITICAL_IMPORTS=(
    "emergentintegrations"
    "edge_tts"
    "deep_translator"
    "cv2"
    "sklearn"
    "lxml"
    "newspaper"
    "serpapi"
    "pydub"
    "textstat"
)

failed_imports=()
for import_name in "${CRITICAL_IMPORTS[@]}"; do
    python -c "import $import_name" 2>/dev/null
    if [ $? -eq 0 ]; then
        log_success "   ✅ $import_name"
    else
        log_error "   ❌ $import_name"
        failed_imports+=("$import_name")
    fi
done

# Summary
echo ""
log "📊 Installation Summary:"
log "   📦 Standard packages: Installed from requirements.txt"
log "   🔧 Special packages: emergentintegrations with custom index"
log "   🎯 Critical packages: ${#CRITICAL_PACKAGES[@]} packages processed"

if [ ${#failed_imports[@]} -eq 0 ]; then
    log_success "🎉 All critical packages are available!"
    log_success "✅ Backend should start without dependency errors"
else
    log_warning "⚠️  Some packages failed to import:"
    for failed in "${failed_imports[@]}"; do
        log_warning "     - $failed"
    done
    log_warning "🔄 Backend may still work, but some features might be limited"
fi

# Create installation status file
cat > /tmp/installation_status.json << EOF
{
    "installation_completed": true,
    "timestamp": "$(date -Iseconds)",
    "failed_imports": [$(printf '"%s",' "${failed_imports[@]}" | sed 's/,$//')],
    "total_packages": ${#CRITICAL_PACKAGES[@]},
    "success_rate": "$(echo "scale=2; (${#CRITICAL_PACKAGES[@]} - ${#failed_imports[@]}) * 100 / ${#CRITICAL_PACKAGES[@]}" | bc)%"
}
EOF

log_success "📄 Installation status saved to /tmp/installation_status.json"

echo ""
log_success "🏁 Dependency installation completed!"
log "🚀 Backend is ready to start..."
echo ""

exit 0