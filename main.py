from Helper_Functions import *
import Yahoo_Finance_Operation
import Google_Drive_Operations

INPUT_STOCK_SYMBOL_CSV = 'Stock_Symbol.csv'
OUTPUT_RESULT_CSV = ''

def main():
    global OUTPUT_RESULT_CSV
    global LOGGER_FILE_NAME 
    LOGGER_FILE_NAME  = os.path.join(LOGS_FOLDER,'STOCK_LOG_%s.log'%(time.strftime("%d_%m_%Y_%H_%M_%S")))
    OUTPUT_RESULT_CSV = os.path.join(CSV_FOLDER,'Result_%s.csv'%(time.strftime("%d_%m_%Y_%H_%M_%S")))
    setup_logging(LOGGER_NAME,LOGGER_FILE_NAME)

    Logger = logging.getLogger(LOGGER_NAME)
    Logger.info('Execution Started At %s'%(time.strftime("%d-%m-%Y %H:%M:%S")))
    
    Data = csv_read(INPUT_STOCK_SYMBOL_CSV)
    try:
        Data = Data[1:]
        if not Data:
            Logger.error('No Stock Data Found')
            return None
    except Exception as e:
        Logger.error('Stock Symbol not available', exc_info=True)
        return None
    else:
        Input_Data = []
        for Row in Data:
            for Column in Row:
                if Column:
                    Input_Data.append(Column)
        Logger.info('Stock Symbol Read From CSV')
    
    try:
        Service = Google_Drive_Operations.create_service()
        if Service is None:
            raise Exception('Google Login Unsuccessful')
    except Exception as e:
        Logger.error('Exception in Google Login', exc_info=True)
        return None
    else:
        Logger.info('Google Login Successful')
        
    Stock_Data = Yahoo_Finance_Operation.main(Input_Data)
    if not Stock_Data:
        Logger.error('No Results Found')
        Stock_Data = [collections.OrderedDict()]
    
    csv_write(OUTPUT_RESULT_CSV,Stock_Data,Open_Type='wb')
    Logger.info('CSV Results Written')
    
    Google_Drive_Operations.main(OUTPUT_RESULT_CSV,LOGGER_FILE_NAME)
    
    Logger.info('Execution Ended At %s'%(time.strftime("%d-%m-%Y %H:%M:%S")))

if __name__ == '__main__':
    main()