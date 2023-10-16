from datetime import datetime
import logging

errorLog = 'error_log.txt'
logging.basicConfig(filename=errorLog, level=logging.ERROR, format='%(asctime)s - %(levelname)s: %(message)s')
result = ["ass","mf","you"]

try:
    raise Exception("Ass")
except Exception as e:
    error_message = e.args[0]
    
    logging.error(result)
    logging.error(error_message)
    print(error_message)

# with open('error_log.txt', 'a') as f:
    # f.write("yo" + " - " + datetime.now().strftime("%m/%d/%Y %H:%M:%S") + "\n")