#!/bin/bash -x
export DEBIAN_FRONTEND=noninteractive

echo "----> Install SMTP server"
apt-get -y -qq --force-yes install mailutils
echo "----> Set server on localhost"
sed -i -e 's/inet_interfaces = all/inet_interfaces = localhost/g' /etc/postfix/main.cf
echo "----> Reload configuration"
/etc/init.d/postfix reload
service postfix restart