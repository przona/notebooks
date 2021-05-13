#!/bin/bash
# wget.sh: run wget
# usage: wget.sh url
# 20210118 erikt(at)xs4all.nl

URL=https://richtlijnendatabase.nl
LOGFILE=logfile.`date '+%Y%m%d'`
BASEDIR="/home/erikt/projects/przona/data/"

if [ -n "$1" ]
then
   URL=$1
fi

cd $BASEDIR
wget -nc -r -o - -R "*.pdf" -X /contact,/info,/pdf,/assets,/gerelateerde_documenten,/en/contact,/en/info,/en/pdf,/en/assets,/en/gerelateerde_documenten "$URL" 2>&1 | tee $LOGFILE

exit 0
