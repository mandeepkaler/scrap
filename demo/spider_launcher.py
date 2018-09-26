from scrapy.cmdline import execute
import logging as log
try:
    #execute(['scrapy','runspider', '/home/mkaler/Desktop/xerintel/scrap/demo/demo/spiders/file.py'])
    execute(['scrapy', 'crawl', 'edifichai_spalsh'])
except Exception as ex:
    log.exception(ex)
