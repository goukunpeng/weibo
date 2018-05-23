#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import requests
import time
import random
import re
import csv
from urllib import parse
from user_agent import getUserAgent


class GetMweiboFollow(object):
    global request
    request = requests.Session()

    def __init__(self, username, password):
        self.__username = username
        self.__password = password

    def login_mweibo(self):
        print('登录前请关闭微博的登录保护！！！')
        user_agent = getUserAgent()
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '286',
            'Content-Type': 'application/x-www-form-urlencoded',
            # 'Cookie': 'SUHB=0LcC_86LbbY_MQ; _T_WM=c72b609500ccb824bab21274e7cd9380; '
            #           'SSO-DBL=903b2dfe558d757c50a86dbd7d018964',
            'Host': 'passport.weibo.cn',
            'Origin': 'https://passport.weibo.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://passport.weibo.cn/signin/welcome?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn%2F',
            # http%3A%2F%2Fm.weibo.cn%2F 可用urldecode解码，http://m.weibo.cn/
            'User-Agent': user_agent
        }
        data = {
            'username': self.__username,
            'password': self.__password,
            'savestate': '1',
            'r': 'http://m.weibo.cn/',
            'ec': '0',
            'pagerefer': 'https://passport.weibo.cn/signin/welcome?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn%2F',
            'entry': 'mweibo',
            'wentry': '',
            'loginfrom': '',
            'client_id': '',
            'code': '',
            'qq': '',
            'mainpageflag': '1',
            'hff': '',
            'hfp': ''
        }
        login_url = 'https://passport.weibo.cn/sso/login'
        try:
            time.sleep(random.uniform(1.0, 2.5))
            login_response = request.post(login_url, headers=headers, data=data)
            login_status = login_response.json()['msg']
            if login_response.status_code == 200 and login_status == '用户名或密码错误':
                print('{}登录失败!'.format(login_status))
            else:
                print("{}成功登录微博！".format(data['username']))
                # login_response.json()['msg'] == ''或者login_response.json()['retcode'] == 20000000
                self.uid = login_response.json()['data']['uid']
                self.cookie_info = login_response.headers['Set-Cookie']
                return True, self.uid, self.cookie_info
        except Exception as e:
            print('Error:', e.args)

    def get_cookies(self):
        comp = re.compile(r'SUB=(.*?);.*?SUHB=(.*?);.*?SCF=(.*?);.*?SSOLoginState=(.*?);.*?ALF=(.*?);.*?')
        reg_info = re.findall(comp, self.cookie_info)[0]
        SUB = reg_info[0]
        SHUB = reg_info[1]
        SCF = reg_info[2]
        SSOLoginState = reg_info[3]
        ALF = reg_info[4]
        m_weibo_cookie = 'SUB' + '=' + SUB + ';' \
                         + 'SHUB' + '=' + SHUB + ';' \
                         + 'SCF' + '=' + SCF + ';' \
                         + 'SSOLoginState' + '=' + SSOLoginState
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': m_weibo_cookie,
            'Host': 'm.weibo.cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': getUserAgent()
        }
        m_weibo_resp = request.get('https://m.weibo.cn/', headers=headers)
        username = re.findall(r'"userName":"(.*?)"', m_weibo_resp.text)[0]
        username_unicode = username.encode('utf-8').decode('unicode_escape')
        _T_WM = re.findall(r'_T_WM=(.*?);', m_weibo_resp.headers['Set-Cookie'])[0]
        MLOGIN = 1
        H5_INDEX = 3
        WEIBOCN_FROM = 1110006030
        H5_INDEX_TITLE = parse.urlencode({'H5_INDEX_TITLE': username_unicode})
        self.build_weibo_cookie = m_weibo_cookie + ';' \
                                  + '_T_WM' + '=' + _T_WM + ';' \
                                  + 'MLOGIN' + '=' + str(MLOGIN) + ';' \
                                  + 'H5_INDEX' + '=' + str(H5_INDEX) + ';' \
                                  + H5_INDEX_TITLE + ';'\
                                  + 'WEIBOCN_FROM' + '=' + str(WEIBOCN_FROM)

    def get_follow_url(self, page=1, *args):
        user_agent = getUserAgent()
        contain_uid = str(100505) + self.uid
        if page <= 1:
            params = {'containerid': '{}_-_FOLLOWERS'.format(contain_uid)}
            cookie = self.build_weibo_cookie
        else:
            params = {'containerid': '{}_-_FOLLOWERS'.format(contain_uid),
                      'page': args[0]}
            cookie = self.build_weibo_cookie + ';' \
                     + 'M_WEIBOCN_PARAMS=fid%3D{}_-_FOLLOWERS%26uicode%3D10000012'.format(contain_uid)
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': cookie,
            'Host': 'm.weibo.cn',
            'Referer': 'https://m.weibo.cn/p/second?containerid={}'.format(params['containerid']),
            'User-Agent': user_agent,
            'X-Requested-With': 'XMLHttpRequest'
        }
        follow_url = 'https://m.weibo.cn/api/container/getSecond?'
        try:
            time.sleep(random.uniform(0.5, 2.7))
            resp = requests.get(follow_url, headers=headers, params=params)
            if resp.status_code == 200:
                follow_maxPage = int(resp.json()['data']['maxPage'])
                if follow_maxPage >= 1:
                    return resp, follow_maxPage
                else:
                    return resp
        except Exception as e:
            print(e.args)
            return None

    def get_follow(self, response):
        follow_info = response.json()['data']['cards']
        follow = {}
        for info in follow_info:
            follow = {'id': info['user']['id'],
                      'screen_name': info['user']['screen_name'],
                      'gender': info['user']['gender'],
                      'description': info['user']['description'],
                      'followers_count': info['user']['followers_count'],
                      'follow_count': info['user']['follow_count'],
                      'statuses_count': info['user']['statuses_count'],
                      'scheme': info['scheme']
                      }
            if info['user']['verified'] == 'true':
                follow['verified_reason'] = info['user']['verified_reason']
                yield follow
            else:
                follow['verified_reason'] = 'None'
                yield follow

    def write_to_csv(self, *args, has_title=True):
        if has_title is True:
            with open('follow.csv', 'w', encoding='utf-8', newline='') as file:
                follow_title = csv.writer(file, delimiter=',')
                follow_title.writerow(['id', 'screen_name', 'gender', 'description', 'follow_count', 'followers_count',
                                       'statuses_count', 'scheme', 'verified_reason'])
        if has_title is False:
            with open('follow.csv', 'a+', encoding='utf-8', newline='') as file:
                follow = csv.writer(file, delimiter=',')
                for data in self.get_follow(args[0]):
                    print(data)
                    follow.writerow([data['id'], data['screen_name'], data['gender'], data['description'],
                                     data['follow_count'], data['followers_count'], data['statuses_count'],
                                     data['scheme'], data['verified_reason']])


def main():
    user = input('username:')
    passwd = input('password:')
    start_time = time.time()
    gkp = GetMweiboFollow(user, passwd)
    gkp.login_mweibo()
    gkp.get_cookies()
    if gkp.get_follow_url() is not None:
        if isinstance(gkp.get_follow_url(), tuple):
            follow_maxPage = gkp.get_follow_url()[1]
            gkp.write_to_csv(has_title=True)
            for page in range(1, follow_maxPage + 1):
                response = gkp.get_follow_url(follow_maxPage, page)[0]
                gkp.write_to_csv(response, has_title=False)
            end_time = time.time()
            print('耗费时间:', end_time - start_time)
        else:
            response = gkp.get_follow_url()
            gkp.write_to_csv(has_title=True)
            gkp.write_to_csv(response, has_title=False)
            end_time = time.time()
            print('耗费时间:', end_time - start_time)
    else:
        print('获取关注列表失败！')
        end_time = time.time()
        print('耗费时间:', end_time - start_time)
        exit()


if __name__ == '__main__':
    main()
