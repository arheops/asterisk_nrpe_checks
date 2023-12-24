Install

```
 mkdir -p /usr/lib/nagios/plugins/
 wget https://raw.githubusercontent.com/arheops/asterisk_nrpe_checks/master/check_astchannels.py \
    -O /usr/lib/nagios/plugins/check_astchannels.py
 chmod a+x /usr/lib/nagios/plugins/check_astchannels.py
 /usr/lib/nagios/plugins/check_astchannels.py -C install
```
 
 For vicidial only, for your OS check nrpe config file location
```
 echo 'command[check_asterisk_channels]=/usr/lib/nagios/plugins/check_astchannels.py -c 1000 -w 100 -C channels' \
   >>/etc/nrpe.cfg
 systemctl restart nrpe
```
 Test at nagios server:
```
 /usr/lib64/nagios/plugins/check_centreon_nrpe3 -H <IP_HERE> -c check_asterisk_channels
```
