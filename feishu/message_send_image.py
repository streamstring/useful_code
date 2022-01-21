import json
from urllib import request
import io
import uuid
import mimetypes

class FeishuSendImage:
    def __init__(self, img_url="", appid="", appsec=""):
        temp_appid = appid if appid else 'xxx'
        temp_appsec = appsec if appsec else 'xxxxx'
        self.appid = temp_appid
        self.appsec = temp_appsec
        # 两小时内有效
        self.acctoken = self.get_app_access_token(temp_appid, temp_appsec)
        self.chatid = ""
        self.atusers = ()
        self.img_url = img_url

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
        result = FeishuSendImage.requst_all(url, req_body={"app_id": appid, "app_secret": appsec}, method='POST')
        return result.get("tenant_access_token", "")

    @staticmethod
    def _form_data(name):
        return 'Content-Disposition: form-data; name="{}"\r\n'.format(name).encode('utf-8')

    @staticmethod
    def _attached_file(name, filename):
        return 'Content-Disposition: form-data; name="{}"; filename="{}"\r\n'.format(name, filename).encode('utf-8')

    @staticmethod
    def _content_type(ct):
        return 'Content-Type: {}\r\n'.format(ct).encode('utf-8')

    # 需要at的人
    def set_names_to_at(self, names=(), atusers=()):
        if len(atusers) > 0:
            self.atusers = atusers
            return None
        temp_token = self.acctoken
        # 获取群成员列表
        url = 'https://open.feishu.cn/open-apis/im/v1/chats/{0}/members'.format(self.chatid)
        headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + temp_token}
        req_body = {"member_id_type": "open_id", "page_size": 100}

        result = self.requst_all(url, headers=headers, req_body=req_body, method='GET')
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

    def set_chat_id(self, chat_name, chat_id=""):
        if chat_id:
            self.chatid = chat_id
            return None
        temp_token = self.acctoken
        # 获取用户或机器人所在的群列表
        url = 'https://open.feishu.cn/open-apis/im/v1/chats?page_size=100&user_id_type=open_id'
        headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + temp_token}
        result = FeishuSendImage.requst_all(url, headers=headers, method='GET')
        if len(result) > 0:
            chats = result.get("data", dict()).get("items", list())
            temp_chat = list(cc for cc in chats if cc["name"] == chat_name)
            if len(temp_chat) == 1:
                self.chatid = temp_chat[0].get("chat_id", "")
            return None
        else:
            print("send message error, code = ", result.get("code", -1), ", msg =", result.get("msg", ""))
            return None

    def upload_image(self, imgpath):
        acctoken = self.acctoken
        url = 'https://open.feishu.cn/open-apis/im/v1/images'
        try:
            buffer = io.BytesIO()
            temp_boundary = uuid.uuid4().hex.encode('utf-8')
            boundary = b'--' + temp_boundary + b'\r\n'
            buffer.write(boundary)
            buffer.write(self._form_data("image_type"))
            buffer.write(b'\r\n')
            buffer.write('message'.encode('utf-8'))
            buffer.write(b'\r\n')
            buffer.write(boundary)
            buffer.write(self._attached_file('image', 'hehe.jpg'))
            mime_type = mimetypes.guess_type(imgpath)[0]
            buffer.write(self._content_type(mime_type))
            buffer.write(b'\r\n')
            iimage = open(imgpath, 'rb')
            buffer.write(iimage.read())
            buffer.write(b'\r\n')
            buffer.write(boundary)
            ddata = bytes(buffer.getvalue())
            req = request.Request(url, data=ddata, method='POST')
            req.add_header('Authorization', "Bearer " + acctoken)
            req.add_header('Content-Type', 'multipart/form-data; boundary={}'.format(temp_boundary.decode('utf-8')))
            req.add_header('Content-length', len(ddata))
            response = request.urlopen(req)
            rsp_body = response.read().decode('utf-8')
            rsp_dict = json.loads(rsp_body)
            self.img_url = rsp_dict.get("data", dict()).get("image_key", "")
        except Exception as e:
            print(e)

    # 富文本
    def send_message(self, title="haha", text="", open_id=""):
        temp_token = self.acctoken
        temp_receive_id = self.chatid if self.chatid else open_id

        first_line = list()
        if text:
            first_line.append({"tag": "text", "text": text})
        if len(self.atusers) > 0:
            temp_at_content = [{"tag": "at", "user_id": iid, "user_name": nname} for iid, nname in self.atusers]
            first_line.extend(temp_at_content)
        second_line = list()
        if self.img_url:
            second_line.append({"tag": "img", "image_key": self.img_url, "width": 300, "height": 300})

        temp_content = list()
        if len(first_line) > 0:
            temp_content.append(first_line)
        if len(second_line) > 0:
            temp_content.append(second_line)
        if len(temp_content) == 0:
            print("send nothing")
            return
        post_content = {
            "zh_cn": {
                "title": title
                , "content": temp_content
            }
        }
        post_content_str = json.dumps(post_content)
        url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={0}".format('chat_id' if self.chatid else 'open_id')
        headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + temp_token}
        req_body = {"receive_id": temp_receive_id, "msg_type": "post", "content": post_content_str}
        result = FeishuSendImage.requst_all(url, headers=headers, req_body=req_body, method='POST')
        if len(result) > 0:
            print("send_success")
        else:
            print("send message error, code = ", result.get("code", -1), ", msg =", result.get("msg", ""))

def main():
    # 开发者
    my_post = FeishuSendImage()
    my_post.upload_image(r'xxx')
    my_post.set_chat_id("xxx")
    my_post.set_names_to_at(("xxx", ))
    my_post.send_message(title="xxxx")


if __name__ == '__main__':
    main()
