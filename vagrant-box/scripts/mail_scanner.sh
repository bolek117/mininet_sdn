#!/bin/bash -x

echo "----> Update sources"
apt-get -q update
echo "----> Install lightweight antivirus scanner"
apt-get -y -q install clamav-daemon
echo "----> Installing malware definition. This may take some time"
freshclam --quiet
echo "----> Setup socket for scanner (3310)"
cat >> /etc/clamav/clamd.conf << EOF
TCPSocket 3310
TCPAddr localhost
EOF
echo "----> Restart scanner service"
service clamav-daemon restart
