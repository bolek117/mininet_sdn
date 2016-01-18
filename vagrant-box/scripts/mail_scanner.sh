#!/bin/bash -x

# Update sources
apt-get update
# Install lightweight antivirus scanner
apt-get -y install clamav-daemon
# Get malware list information
echo "----> Installing malware definition. This may take some time"
freshclam --quiet
# Setup socket for scanner
cat >> /etc/clamav/clamd.conf << EOF
TCPSocket 3310
TCPAddr localhost
EOF
# Restart service
service clamav-daemon restart