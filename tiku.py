import re
import time
import json
import random
import requests
from urllib.parse import quote

login_url = 'http://sddxs.sdsafeschool.gov.cn:7007/#/pages/public/login/ajax/getapi/studLogin'

login_params = {
    'school_title': '',
    'stud_name': '',
    'stud_xuehao': '',
    'stud_pass': ''
}

login_headers = {
    'Referer': 'http://sddxs.sdsafeschool.gov.cn:7007/#/pages/public/login',
    'User-Agent': 'User-Agent,Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0'
}

tiku_url = 'http://tiku.hanfocus.com/ajax/getapi/getLianxi'

tiku_params = {
    'act': 'sort',
    'celue': 1,
    'page': 1
}

tiku_headers = {
    'Referer': 'http://tiku.hanfocus.com/pc/lianxi?act=sort',
    'User-Agent': 'User-Agent,Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0'
}

kaoshi_url = 'http://tiku.hanfocus.com/pc/kaoshi?act=kaoshi'

kaoshi_headers = {
    'Referer': 'http://tiku.hanfocus.com/pc/kaoshi?act=kaoshi',
    'User-Agent': 'User-Agent,Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0'
}

r = requests.session()

login_params['school_title'] = input('学校:').encode('unicode_escape').decode('ascii').replace('\\', '%')
login_params['stud_xuehao'] = input('学号:')
login_params['stud_pass'] = input('密码:')

login_stat = r.get(login_url, params=login_params, headers=login_headers, timeout=5)

if login_stat.status_code != 200:
    print('网站请求错误')
    exit(0)

login_result = login_stat.json()

if login_stat.json()['error_code'] != '0':
    print('登录失败！', login_result['error_code'], login_result['result'])
    exit(0)

print('登录成功！开始做题...')
cookies = {}
for i in login_result['data']:
    cookies[i] = quote(str(login_result['data'][i]))

# conn = sqlite3.connect('tiku.db')
#
# for i in range(1, 41):
#     tiku_params['page'] = i
#     tiku_result = r.get(tiku_url, params=tiku_params, headers=tiku_headers, timeout=5, cookies=cookies)
#     tiku = tiku_result.json()['data']['list']
#     for j in tiku:
#         print(j)
#         conn.execute('INSERT INTO tiku VALUES (?, ?, ?, ?)', [j['timu_id'], j['timu_tixing_title'], j['timu_title'], j['timu_daan']])
#         conn.commit()

kaoshi_page = r.get(kaoshi_url, headers=kaoshi_headers, cookies=cookies)

kaoshi_daan = re.findall("daan:escape\('(.*?)'\),", kaoshi_page.text)[0]

savekaoshi_data = re.findall("var data={(edit_id:'0'.*?)}", kaoshi_page.text)[0]
savekaoshi_data = savekaoshi_data.replace('daan:escape(', '"daan":')
savekaoshi_data = savekaoshi_data.replace('),lockid', ",'lockid'")
savekaoshi_data = savekaoshi_data.replace('edit_id', "'edit_id'")
savekaoshi_data = savekaoshi_data.replace('act', "'act'")
savekaoshi_data = savekaoshi_data.replace('celue', "'celue'")
savekaoshi_data = savekaoshi_data.replace('timu', "'timu'")
savekaoshi_data = savekaoshi_data.replace('stud', "'stud'")
savekaoshi_data = savekaoshi_data.replace("'", '"')
savekaoshi_data = '{' + savekaoshi_data + '}'
savekaoshi_data = json.loads(savekaoshi_data)

# print(savekaoshi_data)

savekaoshi = r.post('http://tiku.hanfocus.com/ajax/save/saveKaoshi', headers=kaoshi_headers, data=savekaoshi_data,
                    cookies=cookies)

# print(savekaoshi.json())

kaoshi_time = random.randint(80, 120)

kaoshiend_data = {
    'act': 'kaoshi',
    'stud': savekaoshi_data['stud'],
    'ceshi_id': savekaoshi.json()['data']['ceshi_id'],
    'dati': savekaoshi_data['daan'],
    'ceshi_long': kaoshi_time,
}

print('模拟做题，等待', kaoshi_time, '秒')
time.sleep(kaoshi_time)


kaoshiend = r.post('http://tiku.hanfocus.com/ajax/save/saveKaoshiend', headers=kaoshi_headers, data=kaoshiend_data,
                   cookies=cookies)

print('分数:', kaoshiend.json()['data']['ceshi_defen'])
