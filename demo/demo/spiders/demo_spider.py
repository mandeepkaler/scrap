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

            assert(splash:runjs("document.getElementById('dgInventario__ctl2_descargarBtn').click()"))

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
    txtUser = ''
    txtPassword = ''
    txtDependencia = ''
    ComboTipoDep = ''
    btnAceptar = ''

 
    formdata_d = {
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

    #login, without splash
    def parse(self, response):
        if self.txtPassword == '':
            self.logger.error('first add a pasword')
            return
        js = self.getFileContentAsString()
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
                            'iframes' : 1,
                            'lua_source' : lua_init,
                            'wait' : 10
                })

    #process the response through splash
    def scrap_iframe(self, response):
        if 'Errores' in response.body:
            self.log('login error')
            return
        elif 'ifrMenu' in response.body:
            self.log('successfuly logged in')
                
        with open('rawLogin.html', 'wb') as f:
            f.write("%s" % response.body)
            self.log('login response html saved at:  %s' % 'rawLogin.html')

        '''string_to_look_for = 'ifrMenu'
        filename = 'responseAfterLog.html'
        iframe = response.data['childFrames'][1]['html']

        if string_to_look_for not in iframe:
            for i in range(len(response.data['childFrames'])):
                if string_to_look_for in response.data['childFrames'][i]['html']:
                    iframe = response.data['childFrames'][i]['html']
                    print('index of iframe obj containing #Menu27: {}'.format(i))
                    break
        
        with open(filename, 'wb') as f:
            f.write("%s" % iframe.encode('ascii', 'ignore').decode('ascii'))
            self.log('Saved after login file %s' % filename)

        selector = parsel.Selector(iframe)
        
        item = {
            'ifr_src': self.base_url + response.css('div#DIVMenu iframe#ifrMenu::attr(src)').extract_first()  
        }
        print('ifr_src {}'.format(item['ifr_src']))
        '''
        url_if = self.base_url + '/GestImpUI/Cobros_mes/Cobros_Mes.aspx'
        js = self.getFileContentAsString()
        yield SplashRequest(
            url = url_if,
            callback=self.download,
            endpoint='execute',
            cache_args = ['lua_source'],
            args={
                'png' : 1,
                'html' : 1,
                'js_source' : js,
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

        #self.headers['Cookie'] = response.cookiejar

        print('cookie {}'.format(response.data['cookies']))

        for cookie in response.data['cookies']:
            #for i in cookie:
            #    print('{}:{}'.format(i, cookie[i]))
                self.headers['Cookie'] +=  str(cookie['name']) + "=" + str(cookie['value']) + ';'

        print('cookies string {}'.format(self.headers['Cookie']))

        cookies = response.data['cookies']

       # for c in response.data['cookies']:
        #    self.headers['Cookie'][c['name']] = c['value']

        data = urllib.urlencode(self.formdata_d)
        r = requests.post(self.base_url + '/GestImpUI/Cobros_mes/Cobros_Mes.aspx', data, allow_redirects=False, headers=self.headers)
        with open('manual.csv', 'wb') as f:
            f.write(r.content)

        yield SplashFormRequest.from_response(
                    response,
                    formid =   'form1',
                    callback = self.extract_data,
                    endpoint = 'execute',
                    session_id = 'dummy',
                    dont_click = True,
                    clickdata = {
                        'id' : 'dgInventario__ctl2_descargarBtn'
                    },
                    formdata = {},
                    args = 
                    {
                                'html' : 1,
                                'iframes' : 1,
                                'wait' : 10,
                                'lua_source' : script
                    },
                    cookies = response.data['cookies'],
                    headers = response.data['headers']
                    )

    def extract_data(self, response):
        filename = 'lala.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
  
    def getFileContentAsString(self):
        with open('demo/spiders/script.js', 'r') as myfile:
            script = myfile.read().replace('\n', '')
        return script