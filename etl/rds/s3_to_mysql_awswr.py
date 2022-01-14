import logging

from pymysql.connections import Connection
import awswrangler as wr

# 使用awswr加载parquet到mysql
def load_parquet_to_mysql(s3_path, dest_db, dest_tb, mysql_host, auth_user, auth_pass,  mysql_port=3306, mode='append', chunksize=5000, boto3_session=None):
    ddf = wr.s3.read_parquet(path=s3_path, boto3_session=boto3_session)
    with Connection(host=mysql_host, user=auth_user, password=auth_pass, port=mysql_port, database=dest_db) as conn:
        if mode == 'append':
            with conn.cursor() as cursor:
                rows = cursor.execute("truncate {0}.{1}".format(dest_db, dest_tb))
                print("清空{0}.{1}表：{2}条".format(dest_db, dest_tb, rows))
        wr.mysql.to_sql(ddf, conn, schema=dest_db, table=dest_tb, mode=mode, chunksize=chunksize)
    return 'success'


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s----%(message)s')

    mysql_conn_conf = {
        "mysql_host": '127.0.0.1'
        , 'auth_user': 'test'
        , 'auth_pass': 'test'
        , 'mysql_port': 3306
        , 'dest_db': 'test1'
        , 'dest_tb': 'test_tb'
    }

    s3_path = 's3://test_bucket/test_path'
    result = load_parquet_to_mysql(s3_path, **mysql_conn_conf)
    print(result)


if __name__ == '__main__':
    main()
