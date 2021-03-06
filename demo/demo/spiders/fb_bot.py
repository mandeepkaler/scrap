#coding=utf-8
import scrapy
from scrapy.http import FormRequest


class FbSpider(scrapy.Spider):
    name = 'fb'
    fb_login_url = 'https://facebook.com/login/'
    start_urls = [fb_login_url]
    user_name = ''
    password = ''


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
        # filename = 'response.html'
        # with open(filename, 'wb') as f:
        #       f.write(response.body)
        #      self.log('Saved file %s' % filename)

        # if 'The password you’ve entered is incorrect' in response.css('div._4rbf _53ij::text').extract_first():
        
        if 'The password you’ve entered is incorrect' in response.body:
            self.log("Login failed! incorrect credentials", level = 40)
        else:
            #logged in
            '''filename = 'response.html'
            with open(filename, 'wb') as f:
                f.write(response.body)
                self.log('Saved file %s' % filename)'''
            print('you have {} new notifications'.format(response.css('span#notificationsCountValue::text').extract_first()))
            div_pagelet = response.xpath('//div[@id="pagelet_navigation"]/div')    
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

