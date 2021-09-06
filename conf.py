"""
微信相关配置
"""
import os

# 公众平台
WE_CHAT_APP_ID = '<app_id>'
WE_CHAT_APP_SECRET = '<app_secret>'

# 开放平台
EncodingAESKey = '<EncodingAESKey>'
token = '<token>'

# 回调页面地址
REDIRECT_URI = '<REDIRECT_URI>'

# access_token 过期时间，默认2小时
EXPIRES = (1.5 * 60 * 60)

# 第三方平台配置
component_appid = '<component_appid>'
# 消息校验token
component_token = "<component_token>"
# 消息加密/解密 key
component_encodingAESKey = "<component_encodingAESKey>"
# 第三方平台APPSECRET
component_APPSECRET = '<component_APPSECRET>'
# 公众号授权回调地址
component_redirect_uri = '<component_redirect_uri>'
# middle_url = ''
# 接收消息推送地址

# 公众号授权地址
oauth_url = '<oauth_url>'

#################### 微信支付 ##############
import os

"""
微信支付配置
"""
# app id
appid = '<appid>'
# 商户号
mch_id = '<mch_id>'
# 接收微信支付异步通知回调地址
notify_url = '<notify_url>'
api_key = '<api_key>'
# 支付回调地址
redirect_url = '<redirect_url>'
# 微信API证书路径
WXPAY_CLIENT_CERT_PATH = "keys/apiclient_cert.pem"
WXPAY_CLIENT_KEY_PATH = "keys/apiclient_key.pem"
