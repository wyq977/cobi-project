## Renew Access

See https://wiki-bsse.ethz.ch/display/DBSSEPUBLIC/Managing+Kerberos+tickets

```
# create keytab and give only user rwx permission
usr/local/bsse/bin/user-keytab --user wangyong
chmod 700 wangyongo@d.ethz.ch.keytab
```

edit renew policy and paste the script below

```
# renew ticket every 30 min
30 * * * * /usr/bin/krenew >/dev/null 2>&1

# renew ticket automatically at 4:15 AM and PM
15 4,16 * * *   /usr/bin/kinit -k -t /home/wangyong/wangyongo@d.ethz.ch.keytab wangyong >/dev/null 2>&1
30 * * * * /usr/bin/krenew >/dev/null 2>&1 ### this command is described in 3.2
```

