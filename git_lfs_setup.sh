#!/bin/bash
# Git LFS Setup for OpenClaw
# Run as: sudo bash git_lfs_setup.sh

echo "Installing Git LFS..."

# Install git-lfs
apt-get update
apt-get install -y git-lfs

# Initialize git-lfs
cd /home/clawbot/.openclaw/workspace
git lfs install
git lfs track "*.tar.gz"
git lfs track "*.zip"
git lfs track "*.mp4"
git lfs track "*.mp3"
git lfs track "*.wav"

# Add .gitattributes
git add .gitattributes
git commit -m "Add Git LFS tracking"

echo "✅ Git LFS configured!"
echo "Large files will now be stored in LFS."
