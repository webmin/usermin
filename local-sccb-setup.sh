#!/bin/sh
noperlpath=1
nouninstall=1
atboot=0
nochown=1
config_dir=/etc/sccb-usermin
var_dir=/var/sccb-usermin
perl=/usr/local/bin/perl
session=1
export noperlpath nouninstall atboot nochown config_dir var_dir perl session
./setup.sh
