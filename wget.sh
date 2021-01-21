#!/bin/bash
# wget.sh: run wget
# usage: wget.sh url
# 20210118 erikt(at)xs4all.nl

URL="$1"
LOGFILE=logfile
BASEDIR="/home/erikt/projects/przona/data/"

if [ -z "$URL" ]
then
   echo "usage: wget.sh url" >&2
   exit 1
fi

cd $BASEDIR
wget -nc -r -e robots=off -o - "$URL" 2>&1 >> $LOGFILE
exit 0
