import scrapy
import parsel
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from scrapy_splash import SplashFormRequest
import requests
import urllib




lua_init = """ function main(splash)
  splash:init_cookies(splash.args.cookies)
  assert(splash:go{
    splash.args.url,
    headers=splash.args.headers,
    http_method=splash.args.http_method,
    body=splash.args.body,
    })
  assert(splash:wait(0.5))

  local entries = splash:history()
  local last_response = entries[#entries].response
  return {
    url = splash:url(),
    headers = last_response.headers,
    http_status = last_response.status,
    cookies = splash:get_cookies(),
    html = splash:html(),
  }
end
"""
script = """
        function main(splash)
            splash:init_cookies(splash.args.cookies)
            assert(splash:go(splash.args.url))
            splash:set_viewport_full()
            assert(splash:wait(10))
            local entries = splash:history()
            assert(splash:runjs("$('#dgInventario__ctl2_descargarBtn').html('changed from lua')"))
            local last_response = entries[#entries].response
            return {
                url = splash:url(),
                headers = last_response.headers,
                http_status = last_response.status,
                cookies = splash:get_cookies(),
                html = splash:html(),
            }
            end
"""
class LoginSpider(scrapy.Spider):
    name = 'edifichai_spalsh'
    
    start_urls = ['https://edifichai.vw-finance.es/GestImpUI/Enter.aspx']
    base_url = 'https://edifichai.vw-finance.es'
    download_url = base_url + '/GestImpUI/Cobros_mes/Cobros_Mes.aspx'
    txtUser = ''
    txtPassword = ''
    txtDependencia = ''
    ComboTipoDep = ''
    btnAceptar = ''

 
    formdata = {
        'secuencia': 'FSLfzE4PnLk=',
        '__EVENTTARGET' : 'dgInventario$_ctl2$descargarBtn',
        '__EVENTARGUMENT': '', 
        '__VIEWSTATE': '/wEPDwUKLTc5NDQ1OTM3NQ9kFgJmD2QWAgIBD2QWAgIHDzwrAAsBAA8WCB4IRGF0YUtleXMWAB4LXyFJdGVtQ291bnQCAR4JUGFnZUNvdW50AgEeFV8hRGF0YVNvdXJjZUl0ZW1Db3VudAIBZBYCZg9kFgZmDw8WBh4GSGVpZ2h0HB4MVGFibGVTZWN0aW9uCyopU3lzdGVtLldlYi5VSS5XZWJDb250cm9scy5UYWJsZVJvd1NlY3Rpb24AHgRfIVNCAoABZBYGZg8PFgIeBFRleHQFC0RlcGVuZGVuY2lhZGQCAQ8PFgIfBwUWw5psdGltYSBhY3R1YWxpemFjacOzbmRkAgIPDxYCHwcFBiZuYnNwO2RkAgEPDxYEHwQcHwYCgAFkFgZmDw8WAh8HBQUwODUwM2RkAgEPDxYCHwcFCjI0LTA5LTIwMThkZAICD2QWAgIBDw8WAh8HBQlEZXNjYXJnYXJkZAICDw8WBh8EHB8FCysEAh8GAoABZBYGZg8PFgIfBwUGJm5ic3A7ZGQCAQ8PFgIfBwUGJm5ic3A7ZGQCAg8PFgIfBwUGJm5ic3A7ZGRkQq7l0C+Y8mmYtoJtC09ke27V59w=',
        '__VIEWSTATEGENERATOR': '0D382CE1',
        '__EVENTVALIDATION': '/wEdAASZl3p/5O7wxNyC9P/LuDZw3g2FJ7ZaNvfIUtTgRkXtqh5imCNaP+hAjiyMTgSvBl7kwrWzZDYu2EKijpnhebiDIQ0FMv3CShlVATc7uImIABbEuNI=',
        'swctextbox1': ' '
    }

    headers = {
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://edifichai.vw-finance.es/GestImpUI/Cobros_mes/Cobros_Mes.aspx',
            'Connection' : 'keep-alive',
            'Host': 'edifichai.vw-finance.es',
            'Origin': 'https://edifichai.vw-finance',
            'Cookie' : ''
    }

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url)
    #check wether the credentials have been set
    def credentials(self):
        if self.txtPassword == '' or self.txtDependencia == '' or self.txtUser == '' or self.ComboTipoDep == '' or self.btnAceptar == '' :
            return False
        return True

    #attempt login with SplashFormRequest to process javascript
    def parse(self, response):
        if not self.credentials():
            self.logger.error('add the credentials first!')
            return
        yield SplashFormRequest.from_response(
                response,
                formdata =
                {
                    'txtUser' : self.txtUser,
                    'txtPassword' : self.txtPassword,
                    'txtDependencia' : self.txtDependencia,
                    'ComboTipoDep' : self.ComboTipoDep,
                    'btnAceptar'    :   self.btnAceptar
                },
                callback = self.scrap_iframe,
                endpoint = 'execute',
                cache_args = ['lua_source'],
                session_id = 'dummy',
                args = 
                {
                            'html' : 1,
                            'lua_source' : lua_init,
                            'wait' : 5
                })

    #process the response through splash
    def scrap_iframe(self, response):
        if 'Errores' in response.body:
            self.log('login failed!')
            return
        elif 'ifrMenu' in response.body:
            self.log('logged in successfuly!')
                
        with open('after_login.html', 'wb') as f:
            f.write("%s" % response.body)
            self.log('response html after login, saved as :  %s' % 'after_login.html')
        
        yield SplashRequest(
            url = self.download_url,
            callback=self.download,
            endpoint='execute',
            cache_args = ['lua_source'],
            args={
                'html' : 1,
                'lua_source' : script,
                'wait': 5
                },
            session_id = 'dummy',
            cookies = response.data['cookies'],
            headers = response.data['headers']
        )

    def download(self, response):
        filename = 'cobros.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        #extract the cookies that are neccesary to maintain the session
        for cookie in response.data['cookies']:
                self.headers['Cookie'] +=  str(cookie['name']) + "=" + str(cookie['value']) + ';'

        self.log('cookies: {}'.format(self.headers['Cookie']))

        formdata = urllib.urlencode(self.formdata)
        response = requests.post(self.base_url + '/GestImpUI/Cobros_mes/Cobros_Mes.aspx', formdata, allow_redirects=False, headers=self.headers)

        with open('result.csv', 'wb') as f:
            f.write(response.content)

    def getFileContentAsString(self):
        with open('demo/spiders/script.js', 'r') as myfile:
            script = myfile.read().replace('\n', '')
        return script