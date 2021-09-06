import redis
import logging
import requests
from urllib.parse import urlencode
from . import conf

logger = logging.getLogger()


class ComponentWechat(object):
    """公众号授权"""

    def get_component_access_token(self):
        """获取component_access_token"""
        pool = redis.ConnectionPool(host='localhost', port=6379)
        redis_conn = redis.Redis(connection_pool=pool)
        component_access_token = redis_conn.get('component_access_token')
        if component_access_token:
            component_access_token = component_access_token.decode()
            return component_access_token
        else:
            component_verify_ticket = redis_conn.get('component_verify_ticket')
            if component_verify_ticket:
                component_verify_ticket = component_verify_ticket.decode()
            else:
                return None
            url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
            data = {
                "component_appid": conf.component_appid,
                "component_appsecret": conf.component_APPSECRET,
                "component_verify_ticket": component_verify_ticket
            }
            resp = requests.post(url, json=data).json()
            # print(resp,'===========component_access_token=======req')
            try:
                component_access_token = resp['component_access_token']
            except:
                return None
            # 保存到redis  conf.EXPIRES redis_conn.setex('test_key',EXPIRES,'component_access_token')
            redis_conn.setex("component_access_token", conf.EXPIRES, component_access_token)
            return component_access_token

    def get_pre_auth_code(self):
        """获取预授权码"""
        component_access_token = self.get_component_access_token()
        if not component_access_token:
            return None

        url = 'https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode?'
        params = {
            'component_access_token':component_access_token
        }
        postdata = {"component_appid": conf.component_appid}
        params = urlencode(params)
        url = url + params
        resp = requests.post(url, json=postdata).json()
        try:
            pre_auth_code = resp['pre_auth_code']
        except:
            return None
        return pre_auth_code

    def get_authorization_qr_url(self, task_id):
        """获取授权二维码链接"""
        pre_auth_code = self.get_pre_auth_code()
        # print(pre_auth_code, '================pre_auth_code')
        if not pre_auth_code:
            return None
        # 二维码授权
        url = 'https://mp.weixin.qq.com/cgi-bin/componentloginpage?'
        # 跳转链接直接授权
        # url = 'https://mp.weixin.qq.com/safe/bindcomponent?'
        params = {
            # 'action':'bindcomponent',
            # 'auth_type': 3,
            # 'no_scan':1,
            'component_appid':conf.component_appid,
            'pre_auth_code':pre_auth_code,
            'redirect_uri':conf.component_redirect_uri+'?task_id='+task_id,
        }
        params = urlencode(params)
        url = url + params
        return url

    def get_authorization_url(self):
        """获取授权链接"""
        pre_auth_code = self.get_pre_auth_code()
        # print(pre_auth_code, '================pre_auth_code')
        if not pre_auth_code:
            return None
        # 二维码授权
        # url = 'https://mp.weixin.qq.com/cgi-bin/componentloginpage?'
        # 跳转链接直接授权
        url = 'https://mp.weixin.qq.com/safe/bindcomponent?'
        params = {
            'action':'bindcomponent',
            'auth_type': 3,
            'no_scan':1,
            'component_appid':conf.component_appid,
            'pre_auth_code':pre_auth_code,
            'redirect_uri':conf.component_redirect_uri,

        }
        params = urlencode(params)
        url = url + params
        return url

    def get_authorization_info(self,authorization_code):
        """获取授权信息"""
        component_access_token = self.get_component_access_token()
        if not component_access_token:
            return None
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth?'
        params = {
            'component_access_token':component_access_token
        }

        postdata = {
            'component_appid':conf.component_appid,
            'authorization_code':authorization_code
        }
        params = urlencode(params)
        url = url + params
        resp = requests.post(url, data=json.dumps(postdata)).json()
        try:
            authorization_info = resp['authorization_info']
        except:
            return None
        return authorization_info

    def api_get_authorizer_info(self,authorizer_appid):
        """获取授权公众号信息"""
        component_access_token = self.get_component_access_token()
        if not component_access_token:
            return None
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info?'
        params = {
            'component_access_token':component_access_token
        }
        postdata = {
            'component_appid':conf.component_appid,
            'authorizer_appid':authorizer_appid
        }
        params = urlencode(params)
        url = url + params
        resp = requests.post(url, json=postdata).json()
        try:
            authorizer_info = resp['authorizer_info']
        except:
            return None
        return authorizer_info

    @staticmethod
    def save_component_verify_ticket(xml_tree):
        """
        保存component_verify_ticket
        :param xml_tree: 解析的xml对象
        :return:
        """
        tick = xml_tree.find("ComponentVerifyTicket")
        try:
            if tick.text:
                # 内容保存到redis中
                pool = redis.ConnectionPool(host='localhost', port=6379)
                redis_conn = redis.Redis(connection_pool=pool)
                redis_connect.set('component_verify_ticket', tick.text)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def update_authorized_info(xml_tree,info_type):
        """
        更新授权信息
        :param xml_tree:
        :return:
        """
        AuthorizerAppid = xml_tree.find('AuthorizerAppid')
        # 取消授权
        if info_type == 'unauthorized':
            try:
               print('取消授权')
            except Exception as e:
                logger.error(e)