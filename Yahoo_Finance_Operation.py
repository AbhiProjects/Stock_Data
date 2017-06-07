from Helper_Functions import *
from bs4 import BeautifulSoup
import html5lib,HTMLParser

YAHOO_FINANCE_URL = 'https://in.finance.yahoo.com/quote/{0}?p={0}'

def beautiful_soup_operation(HTML,Symbol):
    try:
        Soup = BeautifulSoup(HTML,'html5lib')
        
        Name = Soup.find('h1', {'class' : 'D(ib) Fz(18px)'}).text.strip()
        Name_Bracket = Name.find('(')
        if Name_Bracket >= 0:
            Name = Name[:Name_Bracket]
            
        Price_Span = Soup.find('div', {'class' : 'D(ib) Fw(200) Mend(20px)'}).find_all('span')
        if len(Price_Span) >= 2: 
            Price = Price_Span[0].text.strip()
            Change = Price_Span[1].text.strip().split('(')
            Change_Value = Change[0].strip()
            Change_Percent = Change[1].replace(')','').strip()
        else:
            raise Exception('No Price Data Found')
        
        Open = Soup.find('td', {'data-test' : 'OPEN-value'}).text.strip()
        Close = Soup.find('td', {'data-test' : 'PREV_CLOSE-value'}).text.strip()
        Day_Range = Soup.find('td', {'data-test' : 'DAYS_RANGE-value'}).text.strip()
        Year_Range = Soup.find('td', {'data-test' : 'FIFTY_TWO_WK_RANGE-value'}).text.strip()
        Volume = Soup.find('td', {'data-test' : 'TD_VOLUME-value'}).text.strip()
        
        Stock_Data = collections.OrderedDict()
        Stock_Data['Date'] = '%s'%(time.strftime("%d-%m-%Y")) 
        Stock_Data['Symbol'] = Symbol
        Stock_Data['Name'] = Name
        Stock_Data['Price'] = Price
        Stock_Data['Change_Value'] = Change_Value
        Stock_Data['Change_Percent'] = Change_Percent
        Stock_Data['Open'] = Open
        Stock_Data['Close'] = Close
        Stock_Data['Day_Range'] = Day_Range
        Stock_Data['Year_Range'] = Year_Range
        Stock_Data['Volume'] = Volume

    except Exception as e:
        Logger = logging.getLogger(LOGGER_NAME)
        Logger.error(['Exception in Beautiful Soup Operation %s'%(Symbol)], exc_info=True)
    else:
        return Stock_Data

def main(Symbol_Data):
    Logger = logging.getLogger(LOGGER_NAME)
    Logger.info('Yahoo Finance Operations Started')
    Data = []
    for Symbol in Symbol_Data:
        try:
            URL = YAHOO_FINANCE_URL.format(Symbol)
            Response_Data = get_api_request(URL)
            if not Response_Data:
                raise Exception()
            Stock_Data = beautiful_soup_operation(Response_Data,Symbol)
            if not Stock_Data:
                raise Exception()

        except Exception as e:
            Logger.error(['No Data found for Symbol %s'%(Symbol)], exc_info=True)
            continue
        else:
            Logger.info('Stock Symbol %s Added'%(Symbol))
            Data.append(Stock_Data)
    
    Logger.info('Yahoo Finance Operations Ended')
    return Data