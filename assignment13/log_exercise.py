import logging

logging.basicConfig(level=logging.DEBUG,filename='app.log', filemode='w',format='%(name)s -''%(levelname)s -''%(message)s')

logging.debug('This is a debug statement')
logging.info('This will get logging to a file')
logging.warning('This is a Warning')
logging.error('This is an error')
