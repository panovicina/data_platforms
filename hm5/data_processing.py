from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from onetl.connection import SparkHDFS
from onetl.file import FileDFReader
from onetl.db import DBWriter
from onetl.connection import Hive
from onetl.file.format import CSV
from prefect import flow, task


@task
def create_session():
    # Создание Spark сессии с конфигурацией для работы с YARN и Hive
    spark = SparkSession.builder \
        .master("yarn") \
        .appName("spark-with-yarn") \
        .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
        .config("spark.hive.metastore.uris", "thrift://<your-server-name>:<port>") \
        .enableHiveSupport() \
        .getOrCreate()
    return spark


@task
def extract_data(spark):
    # Чтение данных в формате CSV с указанием, что первая строка содержит заголовки
    df = spark.read.format("csv").option("header", "true").load("/input/data-20241101-structure-20180828.csv")
    return df


@task
def transform_data(df):
    # Добавление новой колонки 'reg_year'
    df = df.withColumn("reg_year", F.col("registration_date").substr(0, 4))
    df = df.repartition(90, "reg_year")
    return df


@task
def load_data(df, spark):
    # Запись данных в Hive таблицу с перезаписью существующих данных, partition по 'reg_year'
    df.write.mode("overwrite").partitionBy("reg_year").saveAsTable("registration_data")

# Определение потока данных для процесса ETL
@flow
def process_data():
    # поток данных для процесса ETL
    spark_sess = create_session()
    edata = extract_data(spark_sess)
    tdata = transform_data(edata)
    load_data(tdata, spark_sess)
    spark_sess.stop()

# Запуск потока
if __name__ == "__main__":
    process_data()
