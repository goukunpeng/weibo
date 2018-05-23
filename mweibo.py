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

    def __init__(self, username, password):
        '''
        GetMweiboFollow给绑定属性username,password；使用requests的Session(),使得登录微博后能够保持登录状态
        :param username: 用户登录新浪微博的账号(邮箱，手机号码等，不包括QQ登录)
        :param password: 账号密码
        '''
        self.__username = username
        self.__password = password
        self.request = requests.Session()

    def login_mweibo(self):
        # 登录微博
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
            login_response = self.request.post(login_url, headers=headers, data=data)
            login_status = login_response.json()['msg']   # 获得登录状态信息，用于判断是否成功登录。
            if login_response.status_code == 200 and login_status == '用户名或密码错误':
                print('{}登录失败!'.format(login_status))
            else:
                print("{}成功登录微博！".format(data['username']))
                # 以下为成功登录微博的标志。无论是否成功登录微博，此请求状态码都为200
                # login_response.json()['msg'] == ''或者login_response.json()['retcode'] == 20000000
                self.uid = login_response.json()['data']['uid']   # 获得用户ID，即uid
                self.cookie_info = login_response.headers['Set-Cookie']  # 获得服务器响应此请求的set-cookie，用于后面构建cookie
                return True, self.uid, self.cookie_info
        except Exception as e:
            print('Error:', e.args)

    def get_cookies(self):
        # 构建cookie，用于获得关注列表get_follow_url()时，发送请求的headers的Cookie设置
        # 通过正则表达式，获得cookie里的几个参数SUB、SHUB、SCF、SSOloginState
        comp = re.compile(r'SUB=(.*?);.*?SUHB=(.*?);.*?SCF=(.*?);.*?SSOLoginState=(.*?);.*?ALF=(.*?);.*?')
        reg_info = re.findall(comp, self.cookie_info)[0]
        SUB = reg_info[0]
        SHUB = reg_info[1]
        SCF = reg_info[2]
        SSOLoginState = reg_info[3]
        # ALF = reg_info[4]
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
        # 发送请求给m.weibo.cn，获得响应体中的其它cookie参数，_T_WM、H5_INDEX_TITLE
        # MLOGIN、H5_INDEX、WEIBOCN_FROM的值是固定的
        # H5_INDEX_TITLE是将用户昵称经过urlencode得到的
        m_weibo_resp = self.request.get('https://m.weibo.cn/', headers=headers)
        username = re.findall(r'"userName":"(.*?)"', m_weibo_resp.text)[0]
        # 获得的用户昵称，中文字符是转成了Unicode编码(如\u4e5d)，而英文字符没有。因此要将username由unicode编码为utf-8，再以uniocde_escape解码
        # unicode_escape可以将转义字符\u读取出来
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
        # 关注列表的api接口，Ajax加载。每一页最多十条关注列表信息；页数大于1，传入page参数
        # 获得每页的api接口的json格式数据，即关注列表信息
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
            resp = self.request.get(follow_url, headers=headers, params=params)
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
        # 获得关注列表的用户的信息，使用yield
        follow_info = response.json()['data']['cards']
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
        # param has_title: 用于判断是否在csv表格中写入关注列表信息的列名。一般只写入一次。
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
    user = input('user:')
    passwd = input('password:')
    start_time = time.time()
    gkp = GetMweiboFollow(user, passwd)
    gkp.login_mweibo()
    gkp.get_cookies()
    if gkp.get_follow_url() is not None: # 若gkp.get_follow_url()不为None，说明成功发送了请求，并获得api的json数据
        if isinstance(gkp.get_follow_url(), tuple): # 若gkp.get_follow_url()是tuple，说明关注列表有两页及以上（大于10个）
            follow_maxPage = gkp.get_follow_url()[1] # 最大页数
            gkp.write_to_csv(has_title=True)
            for page in range(1, follow_maxPage + 1):  # 获得每页的api的response，从而得到关注的人的信息，并写入csv
                response = gkp.get_follow_url(follow_maxPage, page)[0]
                gkp.write_to_csv(response, has_title=False)
            end_time = time.time()
            print('耗费时间:', end_time - start_time)
        else:
            # 页数为1
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
