# Shelly Plus 1PM Relay Controller (Stabile with firmware 1.0.3)

Controller system for Shelly Plus 1PM relay.

Relay controls hot water reserve, and is meant to warm it up at nights cheapest hours.
Script runs from different laptop 3 times a day to make sure new prices are loaded to relay. So this application needs seperate server or old laptop to control the relay.

To run properly, you need relayUpdate.py, getDataLib.py, logger.py, properties.conf and data.temp at the same folder. After first run, app will create log.txt file. Settings can be adjusted in properties.conf. There you can applay between which hours price will be checked and how many hours relay should be active.

I'm using crontab to run script. I recomend using this format for cron: 34 19 * * * cd /home/[username]/scripts && python3 relayUpdate.py

Usage of code at users own risk. CODE IS NOT READY YET, but still working at the moment.

Code last updated 13.10.2023