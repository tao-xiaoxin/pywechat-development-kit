import base64
import requests
import json
import random
from urllib.parse import urlencode
from . import conf


class OauthWeChat(object):
    """微信登录工具"""

    def get_code_url(self):
        """
        获取微信登录的url
        返回说明：redirect_uri?code=CODE&state=STATE；
        请求成功返回code和state，否则只有state
        """

        # 开放平台
        # url = 'https://open.weixin.qq.com/connect/qrconnect?'
        # params = {
        #     'appid': conf.WE_CHAT_APP_ID,
        #     'redirect_uri': conf.REDIRECT_URI,
        #     'response_type': 'code',
        #     'scope': 'snsapi_login',
        #     'state': self.generate_state(),
        # }

        # 公众平台
        url = 'https://open.weixin.qq.com/connect/oauth2/authorize?'
        params = {
            'appid' : conf.WE_CHAT_APP_ID,
            'redirect_uri' : conf.REDIRECT_URI,
            'response_type' : 'code',
            'scope' : 'snsapi_userinfo',
            'state' : self.generate_state() + '#wechat_redirect',
        }

        params = urlencode(params)
        url = url + params
        return url


    def get_access_token(self, code):
        """
        获取access_token
        返回示例：
        {
            "access_token":"ACCESS_TOKEN",
            "expires_in":7200,
            "refresh_token":"REFRESH_TOKEN",
            "openid":"OPENID",
            "scope":"SCOPE",
            "unionid": "o6_bmasdasdsad6_2sgVt7hMZOPfL"
        }
        """
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        params = {
            'appid': conf.WE_CHAT_APP_ID,
            'secret': conf.WE_CHAT_APP_SECRET,
            'grant_type': 'authorization_code',
            'code': code
        }
        resp = requests.get(url, params=params)
        if 'errcode' in resp:
            return None
        info = json.loads(resp.text)
        return info

    def get_user_info(self, access_token, openid):
        """
        获取用户信息
        :param access_token:
        :param openid:用户唯一标识
        :return:
        {
            "openid":"OPENID",
            "nickname":"NICKNAME",
            # 1 男 2 女
            "sex":1,
            # 省份
            "province":"PROVINCE",
            "city":"CITY",
            "country":"COUNTRY",
            # 用户头像url
            "headimgurl": "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/0",
            # 用户特权信息
            "privilege":[
                "PRIVILEGE1",
                "PRIVILEGE2"
            ],
            "unionid": " o6_bmasdasdsad6_2sgVt7hMZOPfL"

        }
        """
        url = 'https://api.weixin.qq.com/sns/userinfo'
        params = {
            'access_token' : access_token,
            'openid' : openid
        }
        resp = requests.get(url, params=params).json()
        if 'errcode' in resp:
            return None
        resp['nickname'] = resp['nickname'].encode('iso8859-1').decode('utf8')
        return resp

    def get_refresh_token(self, refresh_token):
        """
        刷新access_token
        :param refresh_token:获取access_token时，refresh_token参数
        :return:
        {
            "access_token":"ACCESS_TOKEN",
            "expires_in":7200,
            "refresh_token":"REFRESH_TOKEN",
            "openid":"OPENID",
            "scope":"SCOPE"
        }
        """
        url = 'https://api.weixin.qq.com/sns/oauth2/refresh_token'
        params = {
            'appid': conf.WE_CHAT_APP_ID,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        resp = requests.get(url, params=params).json()
        if 'errcode' in resp:
            return None
        return resp

    def verification_access_token(self, access_token, openid):
        """
        验证access_token是否有效
        :param access_token:
        :param openid:
        :return: bool
        {
            "errcode":0,"errmsg":"ok"
        }
        """
        url = 'https://api.weixin.qq.com/sns/auth'
        params = {
            'openid': openid,
            'access_token': access_token
        }
        resp = requests.get(url, params=params).json()
        if resp.get('errcode') != 0:
            return False
        return True

    def generate_state(self):
        """生成state"""
        num = random.randint(1, 999)
        data = {'num': num}
        data_str = json.dumps(data)
        state = base64.b64encode(data_str.encode()).decode()
        return state

    @staticmethod
    def check_state(state):
        """
        检验保存用户数据的state
        :return: state or None
        """
        try:
            data_str = base64.b64decode(state).decode()
            ret_obj = json.loads(data_str)
        except Exception:
            return None
        if not ret_obj.get('num',None):
            return None
        return ret_obj