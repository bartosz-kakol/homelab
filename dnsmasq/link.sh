#!/bin/bash

set -e

F="$HOME/dnsmasq"
T="/etc/dnsmasq.d"

sudo ln "$F/home.conf" "$T/home.conf"
