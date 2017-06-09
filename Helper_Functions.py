#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')
sys.dont_write_bytecode = True

import os
import logging
import time
import csv
import collections
import requests

CSV_FOLDER = 'CSV'
LOGS_FOLDER = 'LOGS'

LOGGER_NAME = 'STOCK'
LOGGER_FILE_NAME = ''

def setup_logging(Logger_Name,Logger_File_Name):
    Logger = logging.getLogger(Logger_Name)
    Logger.setLevel(logging.DEBUG)
    Formatter = logging.Formatter('%(levelname)s - %(message)s')

    Stream_Handler = logging.StreamHandler()
    Stream_Handler.setLevel(logging.DEBUG)
    Stream_Handler.setFormatter(Formatter)
    Logger.addHandler(Stream_Handler)
    
    File_Handler = logging.FileHandler(Logger_File_Name, mode='a')
    File_Handler.setLevel(logging.DEBUG)
    File_Handler.setFormatter(Formatter)
    Logger.addHandler(File_Handler)

def get_api_request(Url):
    Response = requests.get(Url)
    if Response.status_code == 200:
        Response = Response.text
        return Response

def csv_read(File_Name):
    try:
        Data = []
        with open(File_Name,'rb') as f:
            reader=csv.reader(f)
            for row in reader:
                Data.append(row)
    except Exception as e:
        Logger = logging.getLogger(LOGGER_NAME)
        Logger.error(['CSV Read',File_Name], exc_info=True)
    else:
        return Data

def csv_write(File_Name,Data,Open_Type='wb'):
    try:
        f = open(File_Name,Open_Type)
        CSV_Header = Data[0].keys()
        csvWriter = csv.DictWriter(f,fieldnames=CSV_Header)
        csvWriter.writeheader()
        csvWriter.writerows(Data)
        f.close()
    except Exception as e:
        Logger = logging.getLogger(LOGGER_NAME)
        Logger.error(['CSV Write',File_Name,Open_Type], exc_info=True)
    else:
        return 'OK'