#!/bin/bash -x

echo "----> Install lightweight antivirus scanner"
apt-get -y -qq install clamav-daemon
echo "----> Setup socket for scanner (3310)"
cat >> /etc/clamav/clamd.conf << EOF
TCPSocket 3310
TCPAddr localhost
EOF
echo "----> Installing malware definition. This may take some time"
freshclam --quiet
echo "----> Restart scanner service"
service clamav-daemon restart
