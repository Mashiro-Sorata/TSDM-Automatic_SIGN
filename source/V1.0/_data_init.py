import os
import pickle as pk 


urls = {}
urls['login_url'] = 'http://www.tsdm.me/member.php?mod=logging&action=login'
urls['enter_url'] = ''
urls['enter_url_start'] = 'http://www.tsdm.me/member.php?mod=logging&action=login&loginsubmit=yes&handlekey=ls&loginhash='
urls['enter_url_end'] = '&inajax=1'
urls['first_url'] = 'http://www.tsdm.me/forum.php'
urls['code_url'] = 'http://www.tsdm.me/plugin.php?id=oracle:verify'
urls['to_sign_url'] = 'http://www.tsdm.me/plugin.php?id=dsu_paulsign:sign'
urls['sign_url'] = 'http://www.tsdm.me/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1'
urls['to_mission_url'] = 'http://www.tsdm.me/forum.php?mod=viewthread&tid=321479'
urls['mission_url'] = 'http://www.tsdm.me/plugin.php?id=np_cliworkdz:work'

head = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'www.tsdm.me',
    'Connection': 'keep-alive'
}

path = os.curdir + r'/_data/'
with open(path + 'urls.pkl', 'wb') as f1:
    pk.dump(urls,f1)

with open(path + 'headers.pkl', 'wb') as f2:
    pk.dump(head,f2)

input('press enter:')
