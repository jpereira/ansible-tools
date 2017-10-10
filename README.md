

Example

```
# ./ansible-inventory-ini2yaml.py -i hosts -d inventory/production
Generating inventory/production/ungrouped.yml
Generating inventory/production/web-sa-br.yml
Generating inventory/production/web-jp-pe.yml
# ls -l inventory/production/
total 12
-rw-r--r-- 1 jpereira jpereira  257 Oct  6 02:12 ungrouped.yml
-rw-r--r-- 1 jpereira jpereira 1400 Oct  6 02:12 web-jp-pe.yml
-rw-r--r-- 1 jpereira jpereira 1396 Oct  6 02:12 web-sa-br.yml
# cat inventory/production/web-jp-pe.yml 
###################################################################################################
# Converted from 'hosts[web-jp-pe]'
###################################################################################################
web-jp-pe:
  hosts:
    192.168.4.10:
      vips: "['7.2.3.4', '4.5.6.7', '66.66.66.66']"
      custom_ports: "[('1.2.3.64', '2156', '2156', '18.17.2.4'), ('4.5.6.7', '2156', '2156', '9.9.82.214')]"
      gateway_ip: "44.44.44.1"
      var_test: "true"
    192.168.4.11:
      vips: "['7.2.3.5', '4.5.6.8', '66.66.66.67']"
      custom_ports: "[('1.2.3.69', '2156', '2156', '18.17.2.4'), ('4.5.6.7', '2156', '2156', '9.9.82.214')]"
      gateway_ip: "33.44.44.1"
      var_test: "true"
    192.168.4.12:
      vips: "['7.2.3.6', '4.5.6.9', '66.66.66.68']"
      custom_ports: "[('1.2.3.64', '2156', '2156', '18.17.2.4'), ('4.5.6.7', '2156', '2156', '9.9.82.214')]"
      gateway_ip: "22.44.44.1"
      var_test: "false"

  vars:
    mgmt_subnets: "[u'44.11.5.0/16', u'44.12.5.0/16', u'44.13.5.0/24']"
    ip_affinity_config: "{u'append_to_routing_routes': [{u'ipv4': u'172.16.44.1/32', u'desc': u'Customer XYZ'}, {u'ipv4': u'172.16.44.2/32', u'desc': u'Customer XYZ'}], u'addrs': [{u'ipv4': u'172.16.44.6/32', u'desc': u'Customer Caipirinha'}, {u'ipv4': u'172.16.44.7/32', u'desc': u'Customer Caipirinha'}]}"
    dns_ip_master: 8.8.8.8
    redis_ip: 192.168.77.9

#
```

TODO

* The dump of list/dict should be formatted. (spaces and newlines as `cat group_vars/web-jp-pe`)
