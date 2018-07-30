import scrapy
from scrapy.http import FormRequest

'''
#a spider that downloads 2 html pages
class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        
#a spider that extracts data
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }

'''


class LoginSpider(scrapy.Spider):
    name = 'sp'
    start_urls = ['https://edifichai.vw-finance.es/GestImpUI/Enter.aspx']
    
    txtUser = ''
    txtPassword = ''
    txtDependencia = ''
    ComboTipoDep = ''


    def parse(self, response):
        return FormRequest.from_response(response,
                    formdata={
                        'txtUser' : self.txtUser,
                        'txtPassword' : self.txtPassword,
                        'txtDependencia' : self.txtDependencia,
                        'ComboTipoDep' : self.ComboTipoDep
                        },
                    callback=self.after_login)

    def after_login(self, response):
        # check login succeed before going on
        if "Errores:" in response.body:
            filename = 'response.html'
            with open(filename, 'wb') as f:
                f.write(response.body)
                self.log('Saved file %s' % filename)
            self.log("Login failed", level = 40)
            print(response.css("#idMensaje")[0])
        else:
            self.log('login successful')
            return

