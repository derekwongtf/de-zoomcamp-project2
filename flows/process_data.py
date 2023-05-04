#!/usr/bin/env python
# coding: utf-8
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import types
from pyspark.sql.functions import *

def spark_process (input_path: str, output_path: str, fiscal_year: int) -> str:
    
    spark = SparkSession.builder \
            .master("local[*]") \
            .appName('test') \
            .getOrCreate()
    
    df = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .option("multiline", "true") \
            .option("escape", "\"") \
            .csv(input_path)

    from pyspark.sql.functions import year,month,dayofmonth,lit,to_date,col

    df = df.withColumn("Issue Date",to_date(col("Issue Date"),"MM/dd/yyyy").cast(types.DateType()))
    
    df = df.withColumn("Issue_Year", year(col("Issue Date"))) \
        .withColumn("Issue_Month", month(col("Issue Date"))) \
        .withColumn("Issue_Day", dayofmonth(col("Issue Date"))) \
        .withColumn("Fiscal_Year", lit(f'{fiscal_year}').cast("integer"))

    df.write \
        .partitionBy("Fiscal_Year","Issue_Year","Issue_Month") \
        .parquet(output_path, mode='overwrite')
