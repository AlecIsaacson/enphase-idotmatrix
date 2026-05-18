#1/usr/bin/python3

import requests
import json
import time
import urllib3
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from dotenv import dotenv_values

secrets = dotenv_values('/home/alec/enphase-idotmatrix/.env')

fontName = '../matrix-fonts/6-series/MatrixChunky6.bdf'

GREEN         = (70, 210, 70)
YELLOW        = (240, 190, 0)
RED           = (220, 55, 55)
ORANGE        = (255, 140, 0)
WHITE         = (255, 255, 255)
GREY          = (64, 64, 64)


def getGraphData(queryEndpoint, metric, startTime, endTime):
   try:
      headers = {'Authorization' : 'Bearer ' + secrets['grafanaApiKey'], 'Accept' : 'application/json'}
      params = {'query' : metric, 'start' : startTime, 'end' : endTime, 'step' : '900'} 
      response = requests.get(secrets['baseURL'] + queryEndpoint, headers=headers, params=params)
      return(response.json())
   
   except Exception as err:
      print(str(err))

def generateGraph(graphProdData, graphConsumeData):
    X=0
    image = Image.new("RGB", (64,64), (0,0,0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('./fonts/MatrixChunky6.bdf', size=6)
    draw.fontmode='l'

    # Dividing axis
    draw.line([(0,38),(64,38)], fill=GREY, width=1)

    for prodWatts in graphProdData:
      pixels = int(float(prodWatts[1])) // 240
      # print(str(int(float(prodWatts[1]))) + ' ' + str(pixels) + ' ' + str(X))
      if pixels > 0:
         draw.line([(X,37),(X,37 - pixels)], fill=GREEN, width=1)
      X+=1

    X=0
    for consumeWatts in graphConsumeData:
      pixels = int(float(consumeWatts[1])) // 240
      # print(str(int(float(consumeWatts[1]))) + ' ' + str(pixels) + ' ' + str(X))
      if pixels > 0:
         draw.line([(X,39),(X,39 + pixels)], fill=RED, width=1)
      X+=1

    currentProd = float(graphProdData[-1][1]) - float(graphConsumeData[-1][1])
    # print(str(currentProd))
    if currentProd < 0:
      fillColor = RED
    else:
      fillColor = GREEN
    draw.text((1,1), str(int(currentProd)), font=font, fill=fillColor)

    image.save('combined.png')

def main():
   # End time is now.
   # We can only show 64 bars. We want 15 minute resolution, so we have room for 15 hours 45 minutes worth of samples (0 - 63).
   # Pandas is in here to do rounding easily, but then we have to convert back to Int
   now = pd.Timestamp(time.time(), unit='s', tz='utc')
   floorTime = now.floor(freq='15min')
   # print(str(now) + ' ' + str(floorTime) + ' ' + str(floorTime.timestamp()))
   endTime = floorTime.timestamp()
   startTime = endTime - (60 * 945) 
   # print(str(endTime) + ' ' + str(startTime))
   graphProdResponse = getGraphData('/api/datasources/proxy/uid/grafanacloud-prom/api/v1/query_range', 'solar_prod_w_now_metric', startTime, endTime)
   graphConsumeResponse = getGraphData('/api/datasources/proxy/uid/grafanacloud-prom/api/v1/query_range', 'solar_consume_w_now_metric', startTime, endTime)
   # print(graphResponse) 

   generateGraph(graphProdResponse['data']['result'][0]['values'], graphConsumeResponse['data']['result'][0]['values'])


if __name__ == '__main__':
   main()

