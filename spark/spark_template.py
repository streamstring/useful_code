import argparse
import datetime
import logging

from pyspark.sql.types import *
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json


def get_dates_between(s_date, e_date, s_form='%Y-%m-%d', t_form='%Y-%m-%d'):
    import datetime
    start_date = datetime.datetime.strptime(s_date, s_form)
    end_date = datetime.datetime.strptime(e_date, s_form)
    date_list = [(start_date + datetime.timedelta(dd)).strftime(t_form) for dd in range((end_date - start_date).days + 1)]
    return date_list


def create_schema(map_string):
    type_map = {"byte": ByteType(), "short": ShortType(), "integer": IntegerType(), "long": LongType(), "float": FloatType(), "double": DoubleType(),
                "decimal": DecimalType(), "string": StringType(), "binary": BinaryType(), "boolean": BooleanType(), "timestamp": TimestampType(),
                "date": DateType()}
    fields_list_strip = [tuple(x.strip().split(" ")) for x in map_string.split(",")]
    struct_type = StructType()
    for f_name, f_type, f_nullable in fields_list_strip:
        struct_type.add(StructField(f_name, type_map[f_type.lower()], bool(f_nullable)))
    return struct_type


def main(args):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s----%(message)s')
    spark = SparkSession.builder.enableHiveSupport().getOrCreate()
    my_sdate, my_edate = args.s_date, args.e_date
    my_alter = args.alter
    my_partition = args.n
    my_date_list = get_dates_between(my_sdate, my_edate)

    temp_schema = "id string 1,app_name string 1,app_ver string 1,first_install_time string 1,update_install_time string 1,status string 1,md5 string 1"
    data_schema = ArrayType(create_schema(temp_schema))

    return "success"


if __name__ == '__main__':
    data_date = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser()
    parser.add_argument("--sdate", default=str(data_date), help="pull_data_time.", dest="s_date")
    parser.add_argument("--edate", default=str(data_date), help="pull_data_time.", dest="e_date")
    parser.add_argument("--alter", default="no", help="alter metadata", dest="alter")
    parser.add_argument("--n", default=2, help="partitions", dest="n")
    argss = parser.parse_args()
    main(argss)
