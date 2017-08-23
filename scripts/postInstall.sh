#!/bin/bash

USERNAME=cloner
GROUP=cloner
GOR=/usr/local/bin/goreplay

chgrp $GROUP $GOR
chmod 0750 $GOR
setcap "cap_net_raw,cap_net_admin+eip" $GOR
