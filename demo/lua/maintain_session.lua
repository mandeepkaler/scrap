function main(splash)
    splash:init_cookies(splash.args.cookies)
    assert(splash:go(splash.args.url))
    splash:set_viewport_full()
    assert(splash:wait(10))
    local entries = splash:history()

    
    assert(splash:runjs("$('#dgInventario__ctl2_descargarBtn').html('changed from lua')"))

    local last_response = entries[#entries].response
    return 
    {
        url = splash:url(),
        headers = last_response.headers,
        http_status = last_response.status,
        cookies = splash:get_cookies(),
        html = splash:html()
    }
end