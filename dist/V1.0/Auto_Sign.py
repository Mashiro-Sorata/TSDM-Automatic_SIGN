import urllib.request as urlr
import urllib.parse as urlp
import http.cookiejar as ck
import os
import re
import zlib
import pickle as pk 
import time
import random as r
from datetime import datetime

def get_Pkls(path):
    global headers,urls
    with open(path+'headers.pkl', 'rb') as f1:
        headers = pk.load(f1)
    with open(path+'urls.pkl', 'rb') as f2:
        urls = pk.load(f2)

def init_data():
    global data
    data.clear()
    data['username'] = user_data['username']
    data['password'] = user_data['password']
    data['loginfield'] = 'username'
    data['cookietime'] = '2592000'
    data['quickforward'] = 'yes'
    data['handlekey'] = 'ls'

def gzip_decode(rsp,code='utf-8'):
    content = rsp.read()
    gzipped = rsp.headers.get('Content-Encoding')
    if gzipped:
        html = zlib.decompress(content, zlib.MAX_WBITS | 32).decode(code,errors='ignore')
    else:
        html = content.decode(code)
    return html

def get_FormHash(html):
    return re.search(r'name="formhash" value="(.+?)"',html).group(1)

def get_Verify():
    global urls,headers,opener
    req = urlr.Request(urls['code_url'],headers=headers)
    rsp = opener.open(req)
    img = rsp.read()
    with open('code.jpg','wb') as f:
        f.write(img)
    temp = input('请输入验证码（验证码位置在此脚本根目录下）：')
    os.remove('code.jpg')
    return temp

def get_Data(html):
    global data
    data.pop('quickforward')
    data.pop('handlekey')
    data['formhash'] = get_FormHash(html)
    data['tsdm_verify'] = get_Verify()
    data['answer'] = ''
    data['questionid'] = '0'
    data['referer'] = 'http://www.tsdm.me/forum.php'

def isLogin():
    global urls,headers,opener
    print('正在尝试自动登录...\n(注：第一次或者长时间未运行此脚本无法进行自动登录，请按照之后的提示进行操作！)')
    req = urlr.Request(urls['first_url'],headers=headers)
    rsp = opener.open(req)
    html = gzip_decode(rsp)
    name = re.search(r'title="访问我的空间">(.+)</a>',html)
    if name:
        name = name.group(1)
        print('欢迎您，使者%s' % name)
        return True
    else:
        return False

def get_loginhash(html):
    return re.search(r'<div id="main_messaqge_(.+?)">',html).group(1)

def init_cookie(path):
    global cookie
    cookie_name = 'cookie.txt'
    cookie = ck.LWPCookieJar(path + cookie_name)
    try:
        cookie.load(path + cookie_name,True,True)
    except FileNotFoundError:
        cookie.save(path + cookie_name,True,True)

def save_cookie(path):
    global cookie
    cookie_name = 'cookie.txt'
    cookie.save(path + cookie_name,True,True)

def set_new_opener():
    global opener,cookie
    handler = urlr.HTTPCookieProcessor(cookie)
    opener = urlr.build_opener(handler)

def add_cookie(name,value):
    global cookie
    temp_cookie = ck.Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain=".tsdm.me",
        domain_specified=True,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=False,
        expires=None,
        discard=False,
        comment=None,
        comment_url=None,
        rest={}
    )
    cookie.set_cookie(temp_cookie)

def set_pgv_info():
    curMs  =datetime.utcnow().second
    ssid = "s" + str( (round(r.random() * 2147483647) * curMs) % 10000000000 )
    return ssid

def set_pgv_pvid():
    curMs  =datetime.utcnow().second
    pvidtmp = (round(r.random() * 2147483647) * curMs) % 10000000000
    return pvidtmp

def get_pgv_cookie(path):
    global cookie,opener,headers
    os.chdir(path)
    if ('pgv.txt') in os.listdir():
        with open('pgv.txt') as f:
            pgv_str = f.read()
        tgt = re.search(r'pgv_pvi=(.+); pgv_info=(.+)',pgv_str)
        add_cookie('pgv_pvi',tgt.group(1))
        add_cookie('pgv_info',tgt.group(2))
        si = re.search(r'ssi=(.+)', tgt.group(2)).group(1)
        url = 'http://pingtcss.qq.com/pingd?dm=www.tsdm.me&url=/forum.php&arg=-&rdm=-&rurl=-&adt=-&rarg=-&pvi=' + tgt.group(1) +'&si=' + si + '&ui=0&ty=1&rt=forum&pn=1&qq=000&r2=8480046&scr=1366x768&scl=24-bit&lg=zh-cn&jv=0&pf=Win32&tz=-8&fl=26.0%20r0&ct=-&ext=bc=0;adid=&r3=454'
        req = urlr.Request(url,headers=headers)
        rsp = opener.open(req)
    else:
        pgv_ssid = set_pgv_info()
        pgv_pvi = set_pgv_pvid()
        url = 'http://pingtcss.qq.com/pingd?dm=www.tsdm.me&url=/forum.php&arg=-&rdm=-&rurl=-&adt=-&rarg=-&pvi=' + str(pgv_pvi) +'&si=' + str(pgv_ssid) + '&ui=0&ty=1&rt=forum&pn=1&qq=000&r2=8480046&scr=1366x768&scl=24-bit&lg=zh-cn&jv=0&pf=Win32&tz=-8&fl=26.0%20r0&ct=-&ext=bc=0;adid=&r3=454'
        new_req = urlr.Request(url,headers=headers)
        rsp = opener.open(new_req)
        pgv_str = 'pgv_pvi=' + str(pgv_pvi) +'; pgv_info=ssi=' + str(pgv_ssid)
        with open('pgv.txt','wt') as f:
            f.write(pgv_str)
        add_cookie('pgv_pvi',str(pgv_pvi))
        add_cookie('pgv_info','ssi=' + str(pgv_ssid))
    os.chdir(os.pardir)

def delay(num,step_sec=1,sym='.',end='\n'):
    for i in range(num):
        print(sym,end='')
        time.sleep(step_sec)
    print('',end=end)

def is_login(html):
    temp = re.search(user_data['username'],html)
    if temp:
        return temp.group(0) + '成功登录！'
    else:
        return None

                        
#-----------------------------------main---------------------------------------#
if __name__ == '__main__':
    _code = 'utf-8'
    _data_path = os.curdir + r'/_data/'
    
    #用户信息
    user_data = {
    'username': 'Mashiro_Sorata',
    'password': '***********'
}
    #签到用语，内容不少于6个字母或3个中文字
    saylist = ['Mashiro_Sorata passed by dotay','Happy day again','Working hard, and make it!']

    #设置是否自动完成打工，True为自动完成
    mission = True

    #python's post_data
    get_Pkls(_data_path)
    data = {}
    init_cookie(_data_path)
    set_new_opener()
    #-------------------------------end_init--------------------------------#
    #login
    while True:
        if isLogin():
            get_pgv_cookie(_data_path)
            save_cookie(_data_path)
            print('登陆成功！\n正在请求签到界面',end='')
            break
        else:
            os.chdir(_data_path)
            if 'cookie.txt' in os.listdir():
                os.remove('cookie.txt')
            os.chdir(os.pardir)
            print('登录失败！重新进行验证码登录...')
            input('请打开此脚本目录，并等待验证码（code.jpg文件）生成。按Enter键继续：')
            init_data()
            post_data = urlp.urlencode(data).encode(_code)
            request = urlr.Request(urls['login_url'],post_data,headers)
            response = opener.open(request)
            save_cookie(_data_path)
            html = gzip_decode(response)
            urls['enter_url'] = urls['enter_url_start'] + get_loginhash(html) + urls['enter_url_end']
            get_Data(html)
            post_data = urlp.urlencode(data).encode(_code)
            request = urlr.Request(urls['enter_url'],post_data,headers)
            response = opener.open(request)
            save_cookie(_data_path)
    delay(3,0.5)

    #sign
    print('正在进行签到',end='')
    delay(4,0.5)
    request = urlr.Request(urls['to_sign_url'],headers=headers)
    response = opener.open(request)
    save_cookie(_data_path)
    html = gzip_decode(response)
    sign_data = {}
    sign_data['todaysay'] = r.choice(saylist)
    sign_data['qdxq'] = 'kx'
    sign_data['qdmode'] = '1'
    sign_data['formhash'] = get_FormHash(html)
    sign_data['fastreply'] = '1'
    post_data = urlp.urlencode(sign_data).encode(_code)
    request = urlr.Request(urls['sign_url'],post_data,headers)
    print('签到中',end='')
    delay(4,0.5)
    response = opener.open(request)
    save_cookie(_data_path)
    html = gzip_decode(response)
    rand_money = re.findall(r'恭喜你签到成功!(.+?)</div>', html)
    signed = re.search(r'您今日已经签到', html)
    if rand_money:
        print('签到成功！%s' % rand_money[0])
    elif signed:
        print('您今日已经签到，请明天再来！')
    else:
        print('签到失败！请保证saylist里的所有内容不少于6个字母或3个中文字！')

    #mission
    if mission:
        #模拟浏览器并检测是否成功登录
        print('登入任务界面中',end='')
        request = urlr.Request(urls['to_mission_url'],headers=headers)
        response = opener.open(request)
        save_cookie(_data_path)
        html = gzip_decode(response)
        save_cookie(_data_path)
        delay(3,0.5)
        if not is_login(html):
            print('登录状态错误，打工任务失败，可以尝试删除_data文件夹下的cookie.txt进行重新登录！')
        else:
            mission_data = {'act': 'clickad'}
            post_data = urlp.urlencode(mission_data).encode(_code)
            request = urlr.Request(urls['mission_url'],post_data,headers)
            response = opener.open(request)
            html = gzip_decode(response)
            wait = re.search(r'您需要等待(.+)后即可进行。',html)
            if wait:
                print('您在%s后才能进行打工任务，请耐心等待' % wait.group(1))
            else:
                print('已完成：%s / 6' % html,end='')
                delay(4,0.5)
                for i in range(5):
                    response = opener.open(request)
                    html = gzip_decode(response)
                    print('已完成：%s / 6' % html,end='')
                    delay(4,0.5)
                mission_data['act'] = 'getcre'
                post_data = urlp.urlencode(mission_data).encode(_code)
                request = urlr.Request(urls['mission_url'],post_data,headers)
                response = opener.open(request)
                save_cookie(_data_path)
                html = gzip_decode(response)
                mission_money = re.search(r'(恭喜，您已经成功领取了奖励天使币.+)<br />(每间隔.+可进行一次)。',html)
                fail = re.search(r'不要作弊哦，重新进行游戏吧！',html)
                if fail:
                    print('Oops...打工失败！请重新尝试...')
                else:
                    print('恭喜！打工成功！')
                    print(mission_money.group(1))
                    print(mission_money.group(2))
        



