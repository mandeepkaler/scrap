#coding=utf-8
import scrapy
from scrapy.http import FormRequest
from scrapy_splash import SplashFormRequest
from scrapy_splash import SplashRequest
import base64
class FbSpider(scrapy.Spider):
    name = 'splash_fb'
    fb_login_url = 'http://www.facebook.com/login/'
    start_urls = [fb_login_url]
    user_name = ''
    password = ''


    def parse(self, response):
        if self.password == '':
            self.logger.error('first add a password')
            return
        return SplashFormRequest.from_response(
                    response,
                    formdata=
                    {
                        'email' : self.user_name,
                        'pass' : self.password
                    },
                    callback = self.after_login,
                    formid = 'loginform',
                    dont_process_response = True

                    )

    def getFriendListDiv(self, divs, boh):
            #divs = response.css('div.linkWrap').extract()
            for div in divs:
                extractedText = div.css('::text').extract_first()
                if extractedText == 'Friend List':
                    return div
            print('printing  boh {}'.format(boh))
            return False

    def getNotificationCount(self, response):
        #response.xpath('//span[@id="notificationsCountValue"]/@content').extract()
        return response.css('span#notificationsCountValue::text').extract_first()

    def after_login(self, response):
        print('response splash \n{}'.format(response.headers))
        print('response splash \n{}'.format(response.url))
        print('response splash \n{}'.format(response.status))
        print('\ntype: {}\n'.format(type(response.headers)))
        filename = 'response.html'
        '''with open(filename, 'wb') as f:
            f.write(response)
            self.log('Saved file %s' % filename)'''

        # if 'The password you’ve entered is incorrect' in response.css('div._4rbf _53ij::text').extract_first():
        
        if 'The password you’ve entered is incorrect' in response.body:
            self.log("Login failed! incorrect credentials", level = 40)
        else:
            #logged in
            print('you have {} new notifications'.format(response.css('span#notificationsCountValue::text').extract_first()))
            div_pagelet = response.xpath('//div[@id="pagelet_navigation"]')
            print('\n printing pagelet\n{}\n'.format(div_pagelet))   
            with open('temp', 'wb') as f:   
                for div in div_pagelet:
                    print(div)
                    try:
                        f.write(div.extract())
                        f.write('\n')
                    except Exception:
                        pass 
            '''divs = response.css('div.noCount.linkWrap::text')
            print('printing divs: {} \n\n'.format(divs))
            for div in divs:
                print('printing divs: {} \n\n'.format(div))
                extractedText = div.css('::text').extract_first()
                if extractedText == 'Friend List':
                     print('friendListDiv : {}'.format(extractedText))
                     break'''
        #logout

        return

