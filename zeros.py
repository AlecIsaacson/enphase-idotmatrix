#!/home/alec/enphase-idotmatrix/venv/bin/python3

import requests
import json
import time
import urllib3
from PIL import Image, ImageDraw, ImageFont
from dotenv import dotenv_values
import logging
import datetime

logging.Formatter.converter = time.gmtime
logging.basicConfig(filename='/home/alec/enphase-idotmatrix/zeros.log', level=logging.DEBUG, format='%(asctime)s.%(msecs)03dZ %(levelname)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

logger.info('Starting')

secrets = dotenv_values('/home/alec/enphase-idotmatrix/.env')

GREEN         = (70, 210, 70)
YELLOW        = (240, 190, 0)
RED           = (220, 55, 55)
ORANGE        = (255, 140, 0)
WHITE         = (255, 255, 255)
GREY          = (64, 64, 64)

def getGraphData(queryEndpoint, metric, startTime, endTime):
   logger.debug('In getGraphData')
   try:
      headers = {'Authorization' : 'Bearer ' + secrets['grafanaApiKey'], 'Accept' : 'application/json'}
      params = {'query' : metric, 'start' : startTime, 'end' : endTime, 'step' : '900'} 
      response = requests.get(secrets['baseURL'] + queryEndpoint, headers=headers, params=params)
      return(response.json())
   except Exception as err:
      logger.info(str(err))

def main():
   logger.info('In main')
   # End time is now.
   # We can only show 64 bars. We want 15 minute resolution, so we have room for 16 hours worth of samples (0 - 63).
   now = datetime.datetime.now(datetime.UTC)
   roundedMinute = now.minute // 15 * 15
   minuteDots = roundedMinute / 15
   roundedTime = now.replace(minute=roundedMinute, second=0, microsecond=0)
   logger.debug(str(now.timestamp()) + ' ' + str(roundedTime.timestamp()))
   endTime = roundedTime.timestamp()
   startTime = endTime - (60 * 960) 
   logger.info('End: ' + str(endTime) + ' ' + 'Start: ' + ' ' + str(startTime))

   graphProdResponse = getGraphData('/api/datasources/proxy/uid/grafanacloud-prom/api/v1/query_range', 'solar_prod_wnow or on() vector(0)', startTime, endTime)
   graphConsumeResponse = getGraphData('/api/datasources/proxy/uid/grafanacloud-prom/api/v1/query_range', 'solar_consume_wnow or on() vector(0)', startTime, endTime)
   graphDailyProdResponse = getGraphData('/api/datasources/proxy/uid/grafanacloud-prom/api/v1/query', 'last_over_time(solar_prod_whtoday[16h]) / 1000', startTime, endTime)

   print(graphProdResponse['data']['result'][0]['values'])
   print(graphProdResponse['data']['result'][1]['values'])

   dataDict = dict(graphProdResponse['data']['result'][0]['values'])
   dataDict2 = dict(graphProdResponse['data']['result'][1]['values'])
   finalDict = dict(sorted(dataDict.items() | dataDict2.items()))
  
   print(finalDict)


if __name__ == '__main__':
   main()
   logger.info('Done')
