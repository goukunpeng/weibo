#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import requests
import time
import random


class GetMweiboFollow(object):
    request = requests.Session()

    def __init__(self, username, password):
        self.__username = username
        self.__password = password

    def login_mweibo(self):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '286',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'SUHB=0LcC_86LbbY_MQ; _T_WM=c72b609500ccb824bab21274e7cd9380; SSO-DBL=903b2dfe558d757c50a86dbd7d018964',
            'Host': 'passport.weibo.cn',
            'Origin': 'https://passport.weibo.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://passport.weibo.cn/signin/welcome?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn%2F',
            # http%3A%2F%2Fm.weibo.cn%2F 可用urldecode解码，http://m.weibo.cn/
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
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
            login_response = request.post(login_url, headers=headers, data=data)
            login_status = login_response.json()['msg']
            if login_response.status_code == 200 and login_status == '用户名或密码错误':
                print('登录失败!')
                exit()
            else:
                print('登录成功!')


        except Exception as e:
            print('Error:', e.args)
            order = input('Login again? (Y/N):')
            if order == 'Y':
                mweibo()
            else:
                exit()


if __name__ == '__main__':
    user = input('username:')
    passwd = input('password:')
    gkp = GetMweiboFollow(user, passwd)
    gkp.login_mweibo()