#!/bin/bash -x

echo "----> Get the spamassasin package"
apt-get -y -qq install spamassassin
echo "----> Enable daemon"
sed -i '/ENABLED=0/c\ENABLED=1' /etc/default/spamassassin
service spamassassin restart

echo "----> Create spam pipe script"
cat >> /usr/bin/spamfilter.sh << EOF
#!/bin/bash
SENDMAIL=/usr/sbin/sendmail
SPAMASSASSIN=/usr/bin/spamc

logger <<<"Spam filter piping to SpamAssassin, then to: \${SENDMAIL} \$@"
\${SPAMASSASSIN} | \${SENDMAIL} "\$@"

exit \$?
EOF

chmod 755 /usr/bin/spamfilter.sh

echo "----> Set postfix rules"
sed -i '12s/.*/smtp      inet  n       -       -       -       -       smtpd -o content_filter=spamfilter/' /etc/postfix/master.cf
cat >> /etc/postfix/master.cf << EOF
spamfilter
          unix  -       n       n       -       -       pipe
   flags=Rq user=debian-spamd argv=/usr/bin/spamfilter.sh -oi -f ${sender} ${recipient}
EOF

/etc/init.d/postfix reload
service postfix restart
