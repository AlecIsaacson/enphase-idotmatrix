#!/home/alec/GitHub/enphase-idotmatrix/venv/bin/python3

import requests
import json
import time
import urllib3
from PIL import Image, ImageDraw, ImageFont
from dotenv import dotenv_values
import logging
import datetime

logging.Formatter.converter = time.gmtime
logging.basicConfig(filename='/home/alec/GitHub/enphase-idotmatrix/enphase-idotmatrix.log', level=logging.INFO, format='%(asctime)s.%(msecs)03dZ %(levelname)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

logger.info('Starting')

secrets = dotenv_values('/home/alec/GitHub/enphase-idotmatrix/.env')

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

def combineDicts(list1, list2):
   logger.debug('In combineDicts')
   try:
      dict1 = dict(list1)
      dict2 = dict(list2)
      combinedDict = dict(sorted(dict1.items() | dict2.items()))
      return(combinedDict)
   except Exception as err:
      logger.info(str(err))

def generateGraph(prodDict, consumeDict, dailyProdData, minuteDots):
    logger.debug('In generateGraph')
    image = Image.new("RGB", (64,64), (0,0,0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('/home/alec/GitHub/enphase-idotmatrix/fonts/MatrixChunky6.bdf', size=6)
    draw.fontmode='l'

    # Dividing axis
    draw.line([(0,38),(63,38)], fill=GREY, width=1)

    # Minute dots to show its working
    draw.line([(63,0),(63,int(minuteDots))], fill=GREY, width=1)

    logger.debug('Processing production data')
    X=0
    for prodTime, prodWatts in prodDict.items():
      # prodWatts has a decimal portion, so we can't just go straight from str to int.
      # We divide by 240 watts and discard the remainder - that gets us 240 watts per pixel on the array, which lets us visualize the entire range of power output in the pixels we have to use
      pixels = int(float(prodWatts)) // 240
      logger.debug(str(prodTime) + ' ' + str(int(float(prodWatts))) + ' ' + str(pixels) + ' ' + str(X))
      if pixels > 0:
         logger.debug('Line: ' + str(X) + ',37 -> ' + str(X) + ',' + str(37 - pixels))
         draw.line([(X,37),(X,37 - (pixels - 1))], fill=GREEN, width=1)
      X+=1

    logger.debug('Processing consumption data')
    X=0
    for consumeTime, consumeWatts in consumeDict.items():
      pixels = int(float(consumeWatts)) // 240
      logger.debug(str(consumeTime) + ' ' + str(int(float(consumeWatts))) + ' ' + str(pixels) + ' ' + str(X))
      if pixels > 0:
         logger.debug('Line: ' + str(X) + ',39 -> ' + str(X) + ',' +str(39 + pixels))
         draw.line([(X,39),(X,39 + (pixels - 1))], fill=RED, width=1)
      X+=1
    
    currentProd = float(next(reversed(prodDict.values()))) - float(next(reversed(consumeDict.values())))
    logger.debug("Current Prod:" + str(currentProd) + " " + next(reversed(prodDict.values())) + " " + next(reversed(consumeDict.values())))
    if currentProd < 0:
      fillColor = RED
    else:
      fillColor = GREEN
    draw.text((1,1), str(int(currentProd)), font=font, fill=fillColor)
    draw.text((32,1), str(round(float(dailyProdData), 2)), font=font, fill=GREEN, anchor='mt')

    image.save('/tmp/combined.png')

def main():
   logger.info('In main')
   # End time is now.
   # We can only show 64 bars. We want 15 minute resolution, so we have room for 15:45 hours worth of samples (0 - 63).
   now = datetime.datetime.now(datetime.UTC)
   roundedMinute = now.minute // 15 * 15
   minuteDots = roundedMinute / 15
   roundedTime = now.replace(minute=roundedMinute, second=0, microsecond=0)
   logger.debug('Now: ' + str(now.timestamp()) + ' Rounded Now: ' + str(roundedTime.timestamp()))
   endTime = roundedTime.timestamp()
   # 945 minutes = 15.75 hours = 64 fifteen minute buckets
   startTime = endTime - (60 * 945)
   logger.info('End: ' + str(endTime) + ' ' + 'Start: ' + ' ' + str(startTime))

   graphProdResponse = getGraphData('/api/datasources/proxy/uid/grafanacloud-prom/api/v1/query_range', 'solar_prod_wnow or on() vector(0)', startTime, endTime)
   logger.debug("Prod response: " + str(graphProdResponse))
   
   if len(graphProdResponse['data']['result']) == 2:
      prodDict = combineDicts(graphProdResponse['data']['result'][0]['values'], graphProdResponse['data']['result'][1]['values'])
   else:
      prodDict = dict(graphProdResponse['data']['result'][0]['values'])
   logger.debug('Prod Dict: ' + str(prodDict))

   graphConsumeResponse = getGraphData('/api/datasources/proxy/uid/grafanacloud-prom/api/v1/query_range', 'solar_consume_wnow or on() vector(0)', startTime, endTime)
   logger.debug('Consume response: ' + str(graphConsumeResponse))

   if len(graphConsumeResponse['data']['result']) == 2:
      consumeDict = combineDicts(graphConsumeResponse['data']['result'][0]['values'], graphConsumeResponse['data']['result'][1]['values'])
   else:
      consumeDict = dict(graphConsumeResponse['data']['result'][0]['values'])
   logger.debug('Consume Dict: ' + str(consumeDict))

   dailyProdResponse = getGraphData('/api/datasources/proxy/uid/grafanacloud-prom/api/v1/query', 'last_over_time(solar_prod_whtoday[16h]) / 1000', startTime, endTime)
   logger.debug('Daily prod response: ' + str(dailyProdResponse))

   generateGraph(prodDict, consumeDict, dailyProdResponse['data']['result'][0]['value'][1], minuteDots)

if __name__ == '__main__':
   main()
   logger.info('Done')
