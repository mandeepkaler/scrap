import scrapy
import parsel
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from scrapy_splash import SplashFormRequest
from requests import post as http_post
from urllib import urlencode
from os.path import exists
from os import makedirs
from db.connect import getPasswordFromDb

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
    response_dir = 'response/'
    lua_dir = 'lua/'
    formdata = {
        'secuencia': 'FSLfzE4PnLk=',
        '__EVENTTARGET': 'dgInventario$_ctl2$descargarBtn',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': '/wEPDwUKLTc5NDQ1OTM3NQ9kFgJmD2QWAgIBD2QWAgIHDzwrAAsBAA8WCB4IRGF0YUtleXMWAB4LXyFJdGVtQ291bnQCAR4JUGFnZUNvdW50AgEeFV8hRGF0YVNvdXJjZUl0ZW1Db3VudAIBZBYCZg9kFgZmDw8WBh4GSGVpZ2h0HB4MVGFibGVTZWN0aW9uCyopU3lzdGVtLldlYi5VSS5XZWJDb250cm9scy5UYWJsZVJvd1NlY3Rpb24AHgRfIVNCAoABZBYGZg8PFgIeBFRleHQFC0RlcGVuZGVuY2lhZGQCAQ8PFgIfBwUWw5psdGltYSBhY3R1YWxpemFjacOzbmRkAgIPDxYCHwcFBiZuYnNwO2RkAgEPDxYEHwQcHwYCgAFkFgZmDw8WAh8HBQUwODUwM2RkAgEPDxYCHwcFCjI0LTA5LTIwMThkZAICD2QWAgIBDw8WAh8HBQlEZXNjYXJnYXJkZAICDw8WBh8EHB8FCysEAh8GAoABZBYGZg8PFgIfBwUGJm5ic3A7ZGQCAQ8PFgIfBwUGJm5ic3A7ZGQCAg8PFgIfBwUGJm5ic3A7ZGRkQq7l0C+Y8mmYtoJtC09ke27V59w=',
        '__VIEWSTATEGENERATOR': '0D382CE1',
        '__EVENTVALIDATION': '/wEdAASZl3p/5O7wxNyC9P/LuDZw3g2FJ7ZaNvfIUtTgRkXtqh5imCNaP+hAjiyMTgSvBl7kwrWzZDYu2EKijpnhebiDIQ0FMv3CShlVATc7uImIABbEuNI=',
        'swctextbox1': ' '
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://edifichai.vw-finance.es/GestImpUI/Cobros_mes/Cobros_Mes.aspx',
        'Connection': 'keep-alive',
        'Host': 'edifichai.vw-finance.es',
        'Origin': 'https://edifichai.vw-finance',
        'Cookie': ''
    }
    txtUser = 'SA08503'  # gitignore
    txtPassword = 'acu0918'  # gitignore
    txtDependencia = '08503'  # gitignore
    ComboTipoDep = '3'  # gitignore
    btnAceptar = 'Aceptar'  # gitignore

    #txtPassword = getPasswordFromDb()

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url)

    # check wether the credentials have been set
    def credentials(self):
        if self.txtPassword == '' or self.txtDependencia == '' or self.txtUser == '' or self.ComboTipoDep == '' or self.btnAceptar == '':
            return False
        return True

    # attempt login with SplashFormRequest to process javascript
    def parse(self, response):
        if not self.credentials():
            self.logger.error('add the credentials first!')
            return
        yield SplashFormRequest.from_response(
            response,
            formdata={
                'txtUser': self.txtUser,
                'txtPassword': self.txtPassword,
                'txtDependencia': self.txtDependencia,
                'ComboTipoDep': self.ComboTipoDep,
                'btnAceptar':   self.btnAceptar
            },
            callback=self.parse_login,
            endpoint='execute',
            cache_args=['lua_source'],
            session_id='dummy',
            args={
                'html': 1,
                'lua_source': self.getFileContentAsString(self.lua_dir + 'init.lua'),
                'wait': 5
            })

    # process the response through splash and ridirects to Cobros_Mes.aspx while maintaing the session
    def parse_login(self, response):
        if 'ifrMenu' in response.body:
            self.log('logged in successfuly!')
        else:
            self.log('login failed')
            return
        # save the html response as a file
        self.save_response('after_login.html', response.body)
        yield SplashRequest(
            url=self.download_url,
            callback=self.download,
            endpoint='execute',
            cache_args=['lua_source'],
            args={
                'html': 1,
                'lua_source': self.getFileContentAsString(self.lua_dir + 'maintain_session.lua'),
                'wait': 5
            },
            session_id='dummy',
            cookies=response.data['cookies'],
            headers=response.data['headers']
        )

    # extracts the session keys from splash response and does a POST request to download the file
    def download(self, response):
        self.save_response('download_page.html', response.body)
        self.log('download page saved as : {}'.format(
            self.response_dir + 'download_page.html'))
        # extract the cookies that are neccesary to maintain the session
        for cookie in response.data['cookies']:
            self.headers['Cookie'] += str(cookie['name']) + \
                "=" + str(cookie['value']) + ';'
        formdata = urlencode(self.formdata)
        res = http_post(self.download_url, formdata,
                            allow_redirects=False, headers=self.headers)
        if res.status_code == 200:
            filename = res.headers['Content-Disposition'].split('=')[1]
            if 'csv' not in filename:
                filename = "response.html"
            self.save_response(filename, res.content)
            self.log('downloaded file saved as: {}'.format(
                self.response_dir + filename))

    # returns the content of a file, as a string
    def getFileContentAsString(self, filepath):
        if not exists(filepath):
            return ''
        with open(filepath, 'r') as myfile:
            string = myfile.read().replace('\n', '')
        return string

    # saves the content argument in the response directory
    def save_response(self, filename, content):
        if not exists(self.response_dir):
            makedirs(self.response_dir)
        with open(self.response_dir + filename, 'wb') as f:
            f.write("%s" % content)
            self.log('response saved as :{}'.format(
                self.response_dir + filename))
