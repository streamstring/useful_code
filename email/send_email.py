import logging
import argparse
import smtplib
import mimetypes
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone


def create_basic_email(ssubject, tto, ffrom, ccc, hhtml=None, attach_path=None):
    temp_msg = EmailMessage()
    temp_msg['Subject'] = ssubject
    temp_msg['To'] = tto
    temp_msg['From'] = ffrom
    temp_msg['Cc'] = ccc
    if hhtml:
        temp_msg.add_alternative(hhtml, subtype='html')
    if attach_path:
        content_type, encoding = mimetypes.guess_type(attach_path)
        maintype, subtype = content_type.split('/', 1)
        # linux路径
        filename = attach_path.split('/')[-1]
        with open(attach_path, 'rb') as fp:
            temp_msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=filename)
    return temp_msg


def send_email(mmsg, auth_user='emailxxxx', auth_pass='xxxxx', ssever='smtp.163.com', pport='994'):
    temp_server = smtplib.SMTP_SSL(ssever, pport)
    temp_server.login(auth_user, auth_pass)
    with temp_server as smtp:
        smtp.helo()
        smtp.send_message(mmsg)
    print("邮件发送成功")


def main(args):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s----%(message)s')
    # logging.info(os.getcwd())

    my_date = args.data_date
    local_excel = '/home/xxxx/xxxx.xlsx'

    my_email_text = """
        <html>
            <body>
                <head>
                    <meta charset="utf-8">
                    <STYLE TYPE="text/css" MEDIA=screen>
                        table.dataframe {
                            border-collapse: collapse;border: 1px solid ;margin: auto;margin-left: 10px;}
                        table.dataframe thead {
                            border: 1px solid #000000;background: #C8C8C8;padding: 10px 10px 10px 10px;color: #000000;}
                        table.dataframe tbody {
                            border: 1px solid #000000;padding: 5px 5px 5px 5px;}
                        table.dataframe tr { }
                        table.dataframe th {
                            vertical-align: top;font-size: 14px;padding: 5px 5px 5px 5px;color: #000000;font-family: arial;text-align: center;}
                        table.dataframe td {
                            text-align: center;padding: 10px 10px 10px 10px;}
                        body {
                            font-family: 微软雅黑;}
                    </STYLE>
                </head>
                <p style="font-family:arial;font-size:18px;font-weight:800;">Dear all,</p>
            </body>
        </html>
    """

    my_subject = 'xxx日报'
    my_address_from = 'email1'
    my_address_to = ["email2", ]
    my_address_cc = ["email3", ]

    my_message = create_basic_email(my_subject, my_address_to, my_address_from, my_address_cc, hhtml=my_email_text, attach_path=local_excel)
    send_email(my_message)


if __name__ == '__main__':
    data_date = (datetime.now(timezone.utc) + timedelta(days=-1)).strftime('%Y-%m-%d')
    parser = argparse.ArgumentParser(usage="send email", description="help info")
    parser.add_argument("--date", default=data_date, help="pull_data_time.", dest="data_date")
    argss = parser.parse_args()
    main(argss)
