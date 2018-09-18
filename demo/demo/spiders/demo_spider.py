import scrapy
from scrapy.http import FormRequest


class LoginSpider(scrapy.Spider):
    name = 'edifichai_spalsh'
    
    start_urls = ['https://edifichai.vw-finance.es/GestImpUI/Enter.aspx']
    #start_urls = [iframe_url]
    base_url = 'https://edifichai.vw-finance.es/'
    txtUser = ''
    txtPassword = ''
    txtDependencia = ''
    ComboTipoDep = ''
    btnAceptar = ''


    #login, without splash
    def parse(self, response):
        if self.txtPassword == '':
            self.logger.error('first add a pasword')
            return
        return scrapy.FormRequest.from_response(
                response,
                formdata =
                {
                    'txtUser' : self.txtUser,
                    'txtPassword' : self.txtPassword,
                    'txtDependencia' : self.txtDependencia,
                    'ComboTipoDep' : self.ComboTipoDep,
                    'btnAceptar'    :   self.btnAceptar
                },
                callback = self.scrap_iframe)

    #process the response and process it through splash
    def scrap_iframe(self, response):
        if 'Errores' in response.body:
            self.log('login error')
        elif 'ifrMenu' in response.body:
            self.log('successfuly logged in')

        filename = 'responseAfterLog.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
            self.log('Saved after login file %s' % filename)
        
        url_if = self.base_url + response.css('div#DIVMenu iframe#ifrMenu::attr(src)').extract_first()
        js = self.getFileContentAsString()
        return scrapy.Request(
                url = url_if,
                callback = self.extract_data,
                meta={
                    'splash' : {
                        'url' : url_if,
                        'endpoint' : 'render.html',
                        'args' : {
                            'html' : 1,
                            'js_source' : js,
                            'wait' : 5
                        }
                    }
                })

    def extract_data(self, response):
        filename = 'responseSplash.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
            self.log('Saved file %s' % filename)
        # check login succeed before going on
        if not 'Cobros del mes' in response.body:
            self.log("Login failed", level = 40)
            print(response.css("#idMensaje")[0])
        else:
            self.log('login successful')

    def getFileContentAsString(self):
        with open('demo/spiders/script.js', 'r') as myfile:
            script = myfile.read().replace('\n', '')
        return script

'''
class LoginSpider(scrapy.Spider):
    name = 'edifichai'
    start_urls = ['https://edifichai.vw-finance.es/GestImpUI/Enter.aspx']
    iframe_url = 'https://edifichai.vw-finance.es/GestImpUI/MenuMain.aspx'
    #start_urls = [iframe_url]
    base_url = 'https://edifichai.vw-finance.es/'
    txtUser = ''
    txtPassword = ''
    txtDependencia = ''
    ComboTipoDep = ''
    btnAceptar = ''


    def parse(self, response):
        if self.txtPassword == '':
            self.logger.error('first add a pasword')
            return
        return scrapy.FormRequest.from_response(
                response,
                formdata =
                {
                    'txtUser' : self.txtUser,
                    'txtPassword' : self.txtPassword,
                    'txtDependencia' : self.txtDependencia,
                    'ComboTipoDep' : self.ComboTipoDep,
                    'btnAceptar'    :   self.btnAceptar
                },
                callback = self.scrap_iframe)  

    def scrap_iframe(self, response):
        url_if = self.base_url + response.css('div#DIVMenu iframe#ifrMenu::attr(src)').extract_first()
        return scrapy.Request(
                url = url_if,
                callback = self.extract_data)

    def extract_data(self, response):
        filename = 'responseIframe.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
            self.log('Saved file %s' % filename)
        # check login succeed before going on
        if not 'Cobros del mes' in response.body:
            self.log("Login failed", level = 40)
            print(response.css("#idMensaje")[0])
        else:
            self.log('login successful')
            url_desc = self.base_url + response.css('div#DIVMenu iframe#ifrMenu::attr(src)').extract_first()
            return
'''