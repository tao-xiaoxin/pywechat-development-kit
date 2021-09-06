import random
import requests
import urllib.parse
import datetime
import hashlib
from random import Random
from bs4 import BeautifulSoup
from . import conf


def get_sign(data_dict, key):
    """
    签名函数
    :param data_dict: 需要签名的参数，格式为字典
    :param key: 密钥 ，即上面的API_KEY
    :return: 字符串
    """
    params_list = sorted(data_dict.items(), key=lambda e: e[0], reverse=False)  # 参数字典倒排序为列表
    params_str = "&".join(u"{}={}".format(k, v) for k, v in params_list) + '&key=' + key
    # 组织参数字符串并在末尾添加商户交易密钥
    md5 = hashlib.md5()  # 使用MD5加密模式
    md5.update(params_str.encode('utf-8'))  # 将参数字符串传入
    sign = md5.hexdigest().upper()  # 完成加密并转为大写
    return sign


def random_str(randomlength=8):
    """
    生成随机字符串
    :param randomlength: 字符串长度
    :return:
    """
    strs = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        strs += chars[random.randint(0, length)]
    return strs


def trans_dict_to_xml(data_dict):
    """
    定义字典转XML的函数
    :param data_dict:
    :return:
    """
    data_xml = []
    for k in sorted(data_dict.keys()):  # 遍历字典排序后的key
        v = data_dict.get(k)  # 取出字典中key对应的value
        if k == 'detail' and not v.startswith('<![CDATA['):  # 添加XML标记
            v = '<![CDATA[{}]]>'.format(v)
        data_xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(data_xml))  # 返回XML


def trans_xml_to_dict(data_xml):
    """
    定义XML转字典的函数
    :param data_xml:
    :return:
    """
    soup = BeautifulSoup(data_xml, features='xml')
    xml = soup.find('xml')  # 解析XML
    if not xml:
        return {}
    data_dict = dict([(item.name, item.text) for item in xml.find_all()])
    return data_dict


def get_wechat_pay_url(order_id, total_fee, product_id,body,spbill_create_ip,redirect_url=conf.task_redirect_url):
    """
    返回手机支付链接
    """
    nonce_str = random_str()  # 拼接出随机的字符串即可，我这里是用  时间+随机数字+5个随机字母
    params = {
        'appid': conf.appid,  # APPID 公众平台
        'mch_id': conf.mch_id,  # 商户号
        'nonce_str': nonce_str,  # 随机字符串
        'out_trade_no': order_id,  # 订单编号，可自定义
        'total_fee': total_fee,  # 订单总金额（单位分，必须是整数）
        'spbill_create_ip': spbill_create_ip,  # 客户端ip
        'notify_url': conf.notify_url,  # 回调地址，微信支付成功后会回调这个url，告知商户支付结果
        'body': body,  # 商品描述
        'product_id': product_id,  # 商品id
        'trade_type': 'MWEB',  # H5支付
        'scene_info':{"h5_info" :{"type": "Wap","wap_url": "","wap_name": ""}}
    }

    sign = get_sign(params, conf.api_key)  # 获取签名
    params['sign'] = sign  # 添加签名到参数字典
    # print(params)
    xml = trans_dict_to_xml(params)  # 转换字典为XML
    response = requests.request('post', 'https://api.mch.weixin.qq.com/pay/unifiedorder', data=xml.encode('utf-8'))  # 以POST方式向微信公众平台服务器发起请求
    # print(response.content)
    data_dict = trans_xml_to_dict(response.content)  # 将请求返回的数据转为字典
    mweb_url = data_dict.get('mweb_url', None)
    if mweb_url:
        ret_redirect_url = urllib.parse.urlencode({'redirect_url':redirect_url})
        mweb_url = mweb_url + '&' + ret_redirect_url
    return mweb_url

def order_query(order_id):
    """查询订单支付状态"""
    url = 'https://api.mch.weixin.qq.com/pay/orderquery'
    nonce_str = random_str()  # 拼接出随机的字符串即可，我这里是用  时间+随机数字+5个随机字母
    params = {
        'appid': conf.appid,  # APPID 公众平台 wx6048923d456554e8
        'mch_id': conf.mch_id,  # 商户号
        'nonce_str': nonce_str,  # 随机字符串
        'out_trade_no': order_id,  # 订单编号，可自定义
    }
    sign = get_sign(params, conf.api_key)  # 获取签名
    params['sign'] = sign  # 添加签名到参数字典
    xml = trans_dict_to_xml(params)  # 转换字典为XML
    response = requests.request('post', url, data=xml.encode('utf-8'))  # 以POST方式向微信公众平台服务器发起请求
    data_dict = trans_xml_to_dict(response.content)  # 将请求返回的数据转为字典
    return data_dict

def enterprise_payment(order_id,openid,amount):
    """
    企业付款
    :param order_id: 提现订单id
    :param openid: 提现用户openid
    :param amount: 提现金额
    :return:
    """
    url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers'
    nonce_str = random_str()
    postdata = {
        'mch_appid':conf.appid,
        'mchid':conf.mch_id,
        'nonce_str':nonce_str,
        'partner_trade_no':order_id,
        'openid':openid,
        'check_name':'NO_CHECK', # 是否校验用户姓名
        'amount':amount,
        'desc':'收益提现'
    }
    sign = get_sign(postdata, conf.api_key)  # 获取签名
    postdata['sign'] = sign  # 添加签名到参数字典
    xml = trans_dict_to_xml(postdata)  # 转换字典为XML
    response = requests.request('post', url, data=xml.encode('utf-8'),cert=(conf.WXPAY_CLIENT_CERT_PATH, conf.WXPAY_CLIENT_KEY_PATH))
    data_dict = trans_xml_to_dict(response.content)  # 将请求返回的数据转为字典
    print(data_dict)
    return data_dict

def enterprise_payment_query(order_id):
    """
    企业付款结果查询
    :param order_id: 付款订单id
    :return:
    """
    nonce_str = random_str()
    postdata = {
        'mch_appid': conf.appid,
        'mchid': conf.mch_id,
        'nonce_str': nonce_str,
        'partner_trade_no': order_id
    }
    sign = get_sign(postdata, conf.api_key)  # 获取签名
    postdata['sign'] = sign  # 添加签名到参数字典
    xml = trans_dict_to_xml(postdata)  # 转换字典为XML
    # 要特别注意的是需要带证书（微信支付签发的）
    # 以POST方式向微信公众平台服务器发起请求
    response = requests.request('post', url, data=xml.encode('utf-8'),cert=(conf.WXPAY_CLIENT_CERT_PATH, conf.WXPAY_CLIENT_KEY_PATH))
    data_dict = trans_xml_to_dict(response.content)  # 将请求返回的数据转为字典
    if data_dict['status'] == 'SUCCESS':
        print('成功')
    elif data_dict['status'] == 'PROCESSING':
        print('处理中')
    else:
        print('失败')
        print(data_dict['reason'],'失败原因')
    return data_dict




