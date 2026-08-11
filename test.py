#!/home/alec/GitHub/enphase-idotmatrix/venv/bin/python3

import requests
import json
import time
import urllib3
from PIL import Image, ImageDraw, ImageFont
from dotenv import dotenv_values
import logging
import datetime

secrets = dotenv_values('/home/alec/GitHub/enphase-idotmatrix/.env')

def getGraphData(queryEndpoint, metric, startTime, endTime):
      headers = {'Authorization' : 'Bearer ' + secrets['grafanaApiKey'], 'Accept' : 'application/json'}
      params = {'query' : metric, 'start' : startTime, 'end' : endTime, 'step' : '900'}
      response = requests.get(secrets['baseURL'] + queryEndpoint, headers=headers, params=params)
      return(response.json())

def main():
   # End time is now.
   # We can only show 64 bars. We want 15 minute resolution, so we have room for 15:45 hours worth of samples (0 - 63).
   now = datetime.datetime.now(datetime.UTC)
   nowLocal = now.astimezone() 
   midnightLocal = nowLocal.replace(hour=0, minute=1, second=0, microsecond=0)
   print(str(now) + ' ' + str(now.timestamp()))
   print(str(nowLocal) + ' ' + str(nowLocal.timestamp()))
   print(str(midnightLocal.isoformat()))
   roundedMinute = now.minute // 15 * 15
   minuteDots = roundedMinute / 15
   roundedTime = now.replace(minute=roundedMinute, second=0, microsecond=0)
   endTime = roundedTime.timestamp()
   # 945 minutes = 15.75 hours = 64 fifteen minute buckets
   startTime = endTime - (60 * 945)

   # graphProdBaselineResponse = getGraphData('/api/datasources/proxy/uid/grafanacloud-prom/api/v1/query_range', 'solar_prod_wnow{}', startTime, endTime)
   graphProdBaselineResponse = getGraphData('/api/datasources/proxy/uid/grafanacloud-prom/api/v1/query_range', 'solar_prod_whtoday{}', midnightLocal.isoformat(), midnightLocal.isoformat())
   print("Baseline response: " + str(graphProdBaselineResponse['data']['result'][0]['values'][0][1]))

   dailyProdResponse = getGraphData('/api/datasources/proxy/uid/grafanacloud-prom/api/v1/query', 'solar_prod_whtoday{}', startTime, endTime)
   print('Daily prod response: ' + str(dailyProdResponse['data']['result'][0]['value'][1]))

if __name__ == '__main__':
   main()
