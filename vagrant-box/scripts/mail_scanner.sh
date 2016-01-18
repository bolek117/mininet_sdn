#!/bin/bash -x

# Update sources
apt-get update
# Install lightweight antivirus scanner
apt-get -y install clamav-daemon
# Setup socket for scanner
echo "TCPSocket 3310\nTCPAddr localhost" | tee -a /etc/clamav/clamd.conf
# Get malware list information
echo "----> Installing malware definition. This may take some time"
freshclam --quiet
# Restart service
service clamav-daemon restart