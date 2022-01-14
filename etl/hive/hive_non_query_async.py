from datetime import datetime, timedelta, timezone
import argparse
import logging
import time

from pyhive import hive
from TCLIService.ttypes import TOperationState

# 非查询 create insert update delete
# 异步调用sql 防止运行时间过长timeout
def hive_non_query(sql, conn_conf, **kkwargs):
    temp_conf = dict(conn_conf)
    temp_conf["configuration"] = kkwargs
    logging.info(temp_conf)
    with hive.connect(**temp_conf) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, async_=True)
            status = cursor.poll().operationState
            while status in (TOperationState.INITIALIZED_STATE, TOperationState.RUNNING_STATE):
                # logs = cursor.fetch_logs()
                # for message in logs:
                #     print(message)
                logging.info(status)
                status = cursor.poll().operationState
                time.sleep(10)
            if status != TOperationState.FINISHED_STATE:
                logging.info('最终状态为：{}'.format(status))
                raise RuntimeError


def main(args):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s----%(message)s')
    # ================== 基本参数=======================================================#
    my_hive_conf = {
        "hive.variable.substitute": "true"
        , "hive.exec.reducers.max": "20"
        , "hive.exec.dynamic.partition.mode": 'nonstrict'
        , "hive.support.quoted.identifiers": "none"}
    # t+1
    my_utc_date = args.data_date
    # ================== 其他自定义变量=======================================================#
    conn_conf = {"auth": "CUSTOM", "host": "xxxx", "username": "xxxx", "password": "xxxxx"}
    # ================== sql=======================================================#
    sql0 = """
        insert overwrite table xxx
        select * from xxxxx
    """.format(part_date=my_utc_date)
    # 执行sql
    hive_non_query(sql0, conn_conf, **my_hive_conf)


if __name__ == '__main__':
    data_date = (datetime.now(timezone.utc) + timedelta(days=-1)).strftime('%Y-%m-%d')

    parser = argparse.ArgumentParser(usage="hive query", description="help info")
    parser.add_argument("--time", default=str(data_date), help="pull_data_time.", dest="data_date")
    argss = parser.parse_args()
    main(argss)
