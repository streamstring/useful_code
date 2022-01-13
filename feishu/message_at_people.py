import json
from urllib import request


class FeishuWarning:
    def __init__(self, appid="", appsec=""):
        temp_appid = appid if appid else 'default_appid'
        temp_appsec = appsec if appsec else 'default_appsec'
        self.appid = temp_appid
        self.appsec = temp_appsec
        # 两小时内有效
        self.acctoken = self.get_app_access_token(temp_appid, temp_appsec)
        self.chatid = ""
        self.atusers = ()

    @staticmethod
    def requst_all(url, method, req_body=None, headers=None):
        try:
            req_conf = {"url": url, "method": method}
            data = bytes(json.dumps(dict(req_body)), encoding='utf8') if req_body else None
            if req_body:
                req_conf["data"] = data
            req_conf["headers"] = headers if headers else {"Content-Type": "application/json; charset=utf-8"}
            req = request.Request(**req_conf)
            response = request.urlopen(req)
        except Exception as e:
            print(e)
            return dict()
        rsp_body = response.read().decode('utf-8')
        rsp_dict = json.loads(rsp_body)
        # print(rsp_dict)
        code = rsp_dict.get("code", -1)
        if code == 0:
            return rsp_dict
        else:
            # print("send message error,url = '{}',code = {},msg = {}".format(url, code, rsp_dict.get("errmsg", "")))
            return dict()

    # 获取app_access_token企业自建应用
    @staticmethod
    def get_app_access_token(appid, appsec):
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        result = FeishuWarning.requst_all(url, req_body={"app_id": appid, "app_secret": appsec}, method='POST')
        return result.get("tenant_access_token", "")

    # 设置群
    def set_chat_id(self, chat_name, chat_id=""):
        if chat_id:
            self.chatid = chat_id
            return None
        temp_token = self.acctoken
        # 获取用户或机器人所在的群列表
        url = 'https://open.feishu.cn/open-apis/im/v1/chats?page_size=100&user_id_type=open_id'
        headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + temp_token}
        result = FeishuWarning.requst_all(url, headers=headers, method='GET')
        if len(result) > 0:
            chats = result.get("data", dict()).get("items", list())
            temp_chat = list(cc for cc in chats if cc["name"] == chat_name)
            if len(temp_chat) == 1:
                self.chatid = temp_chat[0].get("chat_id", "")
            return None
        else:
            print("send message error, code = ", result.get("code", -1), ", msg =", result.get("msg", ""))
            return None

    # 设置要at的人
    def set_names_to_at(self, names=(), atusers=()):
        if len(atusers) > 0:
            self.atusers = atusers
            return None
        temp_token = self.acctoken
        # 获取群成员列表
        url = 'https://open.feishu.cn/open-apis/im/v1/chats/{0}/members'.format(self.chatid)
        headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + temp_token}
        req_body = {"member_id_type": "open_id", "page_size": 100}

        result = FeishuWarning.requst_all(url, headers=headers, req_body=req_body, method='GET')
        if len(result) > 0:
            members = result.get("data", dict()).get("items", list())
            temp_members = [cc for cc in members if cc["name"] in names]
            if len(list(temp_members)) > 0:
                # 匹配群成员名字
                self.atusers = tuple((member["member_id"], member["name"]) for member in temp_members)
            return None
        else:
            print("send message error, code = ", result.get("code", -1), ", msg =", result.get("msg", ""))
            return None

    # 发送消息
    def send_message(self, text, open_id=""):
        temp_token = self.acctoken
        temp_receive_id = self.chatid if self.chatid else open_id
        temp_content = text
        if len(self.atusers) > 0:
            temp_at_content = [r'<at user_id=\"{0}\">{1}</at>'.format(iid, nname) for iid, nname in self.atusers]
            temp_content = text + r'\n' + ' '.join(temp_at_content)
        url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={0}".format('chat_id' if self.chatid else 'open_id')
        headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + temp_token}
        context_text = ''.join(['{"text":"', temp_content, '"}'])
        req_body = {"receive_id": temp_receive_id, "msg_type": "text", "content": context_text}
        result = FeishuWarning.requst_all(url, headers=headers, req_body=req_body, method='POST')
        if len(result) > 0:
            print("send_success")
        else:
            print("send message error, code = ", result.get("code", -1), ", msg =", result.get("msg", ""))


def main():
    # 开发者
    appid = 'xxx'
    appsec = 'xxx'
    # 本地测试
    feishu = FeishuWarning(appid=appid, appsec=appsec)
    print(feishu.acctoken)
    feishu.set_chat_id("feishu_test")
    feishu.set_names_to_at(('xxx', ))
    feishu.send_message("haha")


if __name__ == '__main__':
    main()
