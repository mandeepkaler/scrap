#coding=utf-8
import scrapy
from scrapy.http import FormRequest


class FbSpider(scrapy.Spider):
    name = 'fb'
    fb_login_url = 'https://facebook.com/login/'
    start_urls = [fb_login_url]
    user_name = '' #ignoreline
    password = '' #ignoreline

    def parse(self, response):
        if self.password == '':
            self.logger.error('first add a pasword')
            return
        return [FormRequest(
                    self.fb_login_url,
                    method = 'POST',
                    formdata =
                        {
                            'email':  self.user_name,
                            'pass' :  self.password
                        },
                    callback = self.after_login
                    )]

    def after_login(self, response):
       # filename = 'response.html'
       # with open(filename, 'wb') as f:
       #       f.write(response.body)
       #      self.log('Saved file %s' % filename)

       # if 'The password you’ve entered is incorrect' in response.css('div._4rbf _53ij::text').extract_first():
        
        if 'The password you’ve entered is incorrect' in response.body:
            self.log("Login failed! incorrect credentials", level = 40)
        else:
            #response.xpath('//span[@id="notificationsCountValue"]/@content').extract()
            notif_count = response.css('span#notificationsCountValue::text').extract_first()
            if notif_count > 0:
                print 'you have {} notifications'.format(notif_count)
            else:
                 print('you have no notifications')
        return