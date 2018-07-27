import scrapy
from scrapy.http import FormRequest

class LoginSpider(scrapy.Spider):
    name = 'weebo'
    mal_login_url = 'https://myanimelist.net/login.php'
    start_urls = [mal_login_url]
    user_name = 'organipium'
    #enter the password before executing
    password = '#'
    token = None

    def parse(self, response):
        self.token = response.xpath('//meta[@name="csrf_token"]/@content').extract()
        self.log(self.token[0])
        self.log(type(self.token[0]))

        return [FormRequest(
                    url = self.mal_login_url,
                    method = 'POST',
                    formdata =
                        {
                            'user_name':  self.user_name,
                            'password' :  self.password,
                            'csrf_token': self.token[0],
                            'submit' : '1',
                            'cookie' : '1'
                        },
                    callback = self.after_login
                    )]

    def after_login(self, response):
        filename = 'response.html'
        with open(filename, 'wb') as f:
                f.write(response.body)
                self.log('Saved file %s' % filename)

        if "Your username or password is incorrect." in response.body:
            self.log("Login failed", level = 40)
            print(response.css(".badresult::text").extract_first())
        elif "Too many failed login attempts." in response.body:
            self.logger.error('Too many failed login attempts. Please try to login again after several hours')
        else:
            print('in else')
        return