#!/bin/bash
# automatic earthquake data fetcher for birlikteyiz module
# add to crontab: */5 * * * * /Users/berkhatirli/Desktop/unibos/backend/fetch_earthquakes_cron.sh

cd "$(dirname "$0")"
source venv/bin/activate

# run fetch command
python manage.py fetch_earthquakes >> logs/earthquake_fetch.log 2>&1

# keep only last 1000 lines of log
tail -1000 logs/earthquake_fetch.log > logs/earthquake_fetch.log.tmp
mv logs/earthquake_fetch.log.tmp logs/earthquake_fetch.log
