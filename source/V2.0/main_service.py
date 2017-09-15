import urllib.request as urlr
import urllib.parse as urlp
import urllib.error as urle
import http.cookiejar as ck
import pickle as pk
import re
import zlib
import time
import random as r
from datetime import datetime, timedelta
import os
from lxml import etree
import tkinter.messagebox
from tkinter import *

def get_Pkls(path):
    if os.path.exists(path+'userdata.pkl'):
        with open(path+'userdata.pkl', 'rb') as f1:
            user_data = pk.load(f1)
    else:
        user_data = dict()
    with open(path+'headers.pkl', 'rb') as f2:
        head = pk.load(f2)
    with open(path+'urls.pkl', 'rb') as f3:
        url = pk.load(f3)
    return (user_data, head, url)


def gzip_decode(rsp,code='utf-8'):
    if rsp != None:
        content = rsp.read()
        gzipped = rsp.headers.get('Content-Encoding')
        if gzipped:
            html = zlib.decompress(content, zlib.MAX_WBITS | 32).decode(code,errors='ignore')
        else:
            html = content.decode(code)
        return html
    return ''

def get_FormHash(html):
    tgt = re.search(r'name="formhash" value="(.+?)"',html)
    if tgt:
        return tgt.group(1)
    return ''

def get_loginhash(html):
    tgt = re.search(r'<div id="main_messaqge_(.+?)">',html)
    if tgt:
        return tgt.group(1)
    return ''

def set_pgvs():
        curMs = datetime.utcnow().second
        pgv_ssid = "s" + str( (round(r.random() * 2147483647) * curMs) % 10000000000 )
        pgv_pvi = (round(r.random() * 2147483647) * curMs) % 10000000000
        return (pgv_ssid, pgv_pvi)


class WebService:
    def __init__(self, path):
        self.cookie_name = 'cookie.txt'
        self.code = 'utf-8'
        self.path = path
        self.userdata, self.headers, self.urls = get_Pkls(self.path)
        self.init_userdata()
        self.init_cookie()
        self.new_opener()
        self.error = False
        self.get_saylist()

    def init_userdata(self):
        if self.userdata.get('mission') == None:
            self.userdata['mission'] = True
        if self.userdata.get('autologin') == None:
            self.userdata['autologin'] = True

    
    def init_cookie(self):
        self.cookie = ck.LWPCookieJar(self.path + self.cookie_name)
        try:
            self.cookie.load(self.path + self.cookie_name, True, True)
        except FileNotFoundError:
            self.cookie.save(self.path + self.cookie_name, True, True)

    def save_cookie(self):
        self.cookie.save(self.path + self.cookie_name, True, True)

    def new_opener(self):
        self.opener = urlr.build_opener(urlr.HTTPCookieProcessor(self.cookie))

    def get_prelogin_data(self):
        self.data = {}
        self.data['username'] = self.userdata['username']
        self.data['password'] = self.userdata['password']
        self.data['loginfield'] = 'username'
        self.data['cookietime'] = '2592000'
        self.data['quickforward'] = 'yes'
        self.data['handlekey'] = 'ls'
        self.post_data = urlp.urlencode(self.data).encode(self.code)

    def get_response(self, url, data=None, headers=None):
        temp_headers = self.headers if headers==None else headers
        if data:
            req = urlr.Request(url, data, temp_headers)
        else:
            req = urlr.Request(url, headers=temp_headers)
        try:
            response = self.opener.open(req)
        except urle.URLError as e:
            if hasattr(e,'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
                prompt = 'We failed to reach a server.\nReason: ' + str(e.reason)
            elif hasattr(e, 'code'):
                print('The server could\' fulfill the request.')
                print('Error code: ', e.code)
                prompt = 'The server could\' fulfill the request.\nError code: ' + str(e.code)
            tkinter.messagebox.showerror('出错啦！', prompt)
            response = None
        except ConnectionResetError as e:
            print(e)
            tkinter.messagebox.showerror('出错啦！', e)
            response = None
        finally:
            return response

    def get_Verify_img(self):
        os.chdir(self.path)
        response = self.get_response(self.urls['code_url'])
        if response:
            img = response.read()
            with open('code.png', 'wb') as f:
                f.write(img)
        os.chdir(os.pardir)

    def get_login_data(self, code):
        self.data.pop('quickforward')
        self.data.pop('handlekey')
        self.data['formhash'] = get_FormHash(self.html)
        self.data['tsdm_verify'] = code#获取Entry值
        self.data['answer'] = ''
        self.data['questionid'] = '0'
        self.data['referer'] = 'http://www.tsdm.me/forum.php'
        self.post_data = urlp.urlencode(self.data).encode(self.code)
    
    def add_cookie(self, name, value):
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
        self.cookie.set_cookie(temp_cookie)


    def get_pgv_cookie(self):
        os.chdir(self.path)
        if os.path.exists('pgv.txt'):
            with open('pgv.txt') as f:
                pgv_str = f.read()
            tgt = re.search(r'pgv_pvi=(.+); pgv_info=(.+)', pgv_str)
            self.add_cookie('pgv_pvi', tgt.group(1))
            self.add_cookie('pgv_info', tgt.group(2))
            si = re.search(r'ssi=(.+)', tgt.group(2)).group(1)
            r3 = int(r.random() * 450) + 350
            url = 'http://pingtcss.qq.com/pingd?dm=www.tsdm.me&url=/forum.php&arg=-&rdm=-&rurl=-&adt=-&rarg=-&pvi=' + tgt.group(1) +'&si=' + si + '&ui=0&ty=1&rt=forum&pn=1&qq=000&r2=8480046&scr=1366x768&scl=24-bit&lg=zh-cn&jv=0&pf=Win32&tz=-8&fl=26.0%20r0&ct=-&ext=bc=0;adid=&r3=' + str(r3)
            self.get_response(url)
        else:
            pgv_ssid, pgv_pvi = set_pgvs()
            r3 = int(r.random() * 450) + 350
            url = 'http://pingtcss.qq.com/pingd?dm=www.tsdm.me&url=/forum.php&arg=-&rdm=-&rurl=-&adt=-&rarg=-&pvi=' + str(pgv_pvi) +'&si=' + str(pgv_ssid) + '&ui=0&ty=1&rt=forum&pn=1&qq=000&r2=8480046&scr=1366x768&scl=24-bit&lg=zh-cn&jv=0&pf=Win32&tz=-8&fl=26.0%20r0&ct=-&ext=bc=0;adid=&r3=' + str(r3)
            self.get_response(url)
            pgv_str = 'pgv_pvi=' + str(pgv_pvi) +'; pgv_info=ssi=' + str(pgv_ssid)
            with open('pgv.txt', 'wt') as f:
                f.write(pgv_str)
            self.add_cookie('pgv_pvi',str(pgv_pvi))
            self.add_cookie('pgv_info','ssi=' + str(pgv_ssid))
        os.chdir(os.pardir)

    
                        
    def autoLogin(self):
        response = self.get_response(self.urls['first_url'])
        self.html = gzip_decode(response)
        return re.search(r'title="访问我的空间">(.+)</a>',self.html)

    def is_login(self, html):
        return re.search(self.userdata['username'], html)

    def get_enter_url(self, account, passwd):
        self.userdata['username'] = account
        self.userdata['password'] = passwd
        self.get_prelogin_data()
        response = self.get_response(self.urls['login_url'], self.post_data)
        self.save_cookie()
        self.html = gzip_decode(response)
        self.urls['enter_url'] = self.urls['enter_url_start'] + get_loginhash(self.html) + self.urls['enter_url_end']
        self.get_Verify_img()
    
    def save_userdata(self):
        with open(self.path + 'userdata.pkl', 'wb') as f:
            pk.dump(self.userdata, f)

    def get_author_image(self):
        html = etree.HTML(self.html)
        src = html.xpath('//div[@id="um"]/div[@class="avt y"]/a/img/@data-original')[0]
        rsp = self.get_response(src)
        if rsp:
            img = rsp.read()
            with open(self.path+'author.jpg','wb') as f:
                f.write(img)
    
    def get_saylist(self):
        if os.path.exists(self.path+'saylist.txt'):
            self.saylist = []
            with open(self.path+'saylist.txt') as f:
                for each in f:
                    each = each.strip()
                    if each:
                        self.saylist.append(each)
        else:
            prompt = '天使奏赛高！！！\n真白赛高~~~\n日常签到。。。\n'
            self.saylist = ['天使奏赛高！！！','真白赛高~~~','日常签到。。。']
            with open(self.path+'saylist.txt' ,'wt') as f:
                f.write(prompt)
        
                
    
    def get_sign_data(self):
        rsp = self.get_response(self.urls['to_sign_url'])
        self.html = gzip_decode(rsp)
        sign_data = {}
        sign_data['todaysay'] = r.choice(self.saylist)
        sign_data['qdxq'] = 'kx'
        sign_data['qdmode'] = '1'
        sign_data['formhash'] = get_FormHash(self.html)
        sign_data['fastreply'] = '1'
        self.post_data = urlp.urlencode(sign_data).encode(self.code)

    def do_sign(self):
        rsp = self.get_response(self.urls['sign_url'], self.post_data)
        self.save_cookie()
        self.html = gzip_decode(rsp)
        rand_money = re.findall(r'恭喜你签到成功!(.+?)</div>', self.html)
        signed = re.search(r'您今日已经签到', self.html)
        if rand_money:
            return ('签到成功！%s' % rand_money[0])
        elif signed:
            return '您今日已经签到，请明天再来！'
        else:
            return None

    def pre_mission(self):
        rsp = self.get_response(self.urls['to_mission_url'])
        self.html = gzip_decode(rsp)
        return self.is_login(self.html)

    def do_mission(self):
        mission_data = {'act': 'clickad'}
        self.post_data = urlp.urlencode(mission_data).encode(self.code)
        rsp = self.get_response(self.urls['mission_url'], self.post_data)
        self.html = gzip_decode(rsp)
        wait = re.search(r'您需要等待(.+)后即可进行。',self.html)
        time.sleep(r.randint(2,5))
        if wait:
            return wait.group(1)
        else:
            for i in range(5):
                rsp = self.get_response(self.urls['mission_url'], self.post_data)
                time.sleep(r.randint(2,5))
            mission_data['act'] = 'getcre'
            self.post_data = urlp.urlencode(mission_data).encode(self.code)
            rsp = self.get_response(self.urls['mission_url'],self.post_data)
            self.save_cookie()
            self.html = gzip_decode(rsp)
            self.mission_money = re.search(r'恭喜，您已经(成功领取了奖励天使币.+)<br />(每间隔.+可进行一次)。',self.html)
            fail = re.search(r'不要作弊哦，重新进行游戏吧！',self.html)
            if fail:
                return 'fail'
            return None
        

class Logs:
    def __init__(self, path=os.curdir, filename='logs.pkl'):
        self.logname = filename
        self.path = path
        self.init_logs()

    def init_logs(self):
        if os.path.exists(self.path + self.logname):
            with open(self.path + self.logname, 'rb') as f:
                self.logs = pk.load(f)
        else:
            self.logs = dict()

    def save_logs(self):
        with open(self.path + self.logname, 'wb') as f:
            pk.dump(self.logs, f)

    def log2file(self, content):
        prompt = self.date2str(self.now())+content+'\n'
        if os.path.exists(self.path+'logs.txt'):
            with open(self.path+'logs.txt', 'at') as f:
                f.write(prompt)
        else:
            with open(self.path+'logs.txt', 'wt') as f:
                f.write(prompt)

    def datelist2str(self, datelist):
        return (str(datelist[0])+'年'+str(datelist[1])+'月'+str(datelist[2])+'日<-'+str(datelist[3])+':'+str(datelist[4])+':'+str(datelist[5])+'->：')

    def date2str(self, date):
        return (str(date.year)+'年'+str(date.month)+'月'+str(date.day)+'日<-'+str(date.hour)+':'+str(date.minute)+':'+str(date.second)+'->：')
    
    def update_log(self, name, time=datetime.now(), save=True):
        self.logs[name] = self.date2list(time)
        if save:
            self.save_logs()

    def now(self):
        return datetime.now()
    

    def dt_list2sec(self, datelist2, datelist1):
        dt = self.list2date(datelist2) - self.list2date(datelist1)
        return dt.seconds

    def date2list(self, date):
        datelist = []
        datelist.append(date.year)
        datelist.append(date.month)
        datelist.append(date.day)
        datelist.append(date.hour)
        datelist.append(date.minute)
        datelist.append(date.second)
        return datelist

    def list2date(self, datelist):
        return datetime(datelist[0],datelist[1],datelist[2],datelist[3],datelist[4],datelist[5])

    def sign_avaliable(self):
        if self.logs.get('sign'):
            dt = self.now() - self.list2date(self.logs['sign'])
            if (self.now().day - self.logs['sign'][2] >= 1) or (dt.seconds > 24*60*60):
                return True
            else:
                return False
        return True

    def mission_avaliable(self):
        if self.logs.get('mission'):
            delta = self.now() - self.list2date(self.logs['mission'])
            dt = 6*60*60 - delta.seconds
            if dt > 0:
                return dt
        return True
    
    def get_missionedtime(self, dtlist):
        dt = timedelta(hours=6) - timedelta(hours=dtlist[0], minutes=dtlist[1], seconds=dtlist[2])
        self.update_log('mission', self.now() - dt)

    

