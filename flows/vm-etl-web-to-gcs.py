#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pyspark
from pyspark.sql import SparkSession
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
import requests
import os
from tqdm import tqdm


# In[2]:


spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()


# In[3]:


def fetch_from_web (dataset_url: str, year:int, chunk_size: int) -> str:
    local_dir = f"data/raw/{year}"
    local_filename= f"{local_dir}/rows.csv"

    if not os.path.exists(f"{local_dir}"):
        os.makedirs(f"{local_dir}")

    with requests.get(dataset_url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
        print(f'Downloading {dataset_url}')
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                progress_bar.update(len(chunk))
    return local_dir


# In[4]:


def clean (input_path:str, year:int) -> str:
    print(f'processing data for {year}')

    output_path = f'data/pq/{year}'
    
    if not os.path.exists(f"{output_path}"):
        os.makedirs(f"{output_path}")

    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .option("multiline", "true") \
        .option("escape", "\"") \
        .csv(input_path)

    df \
        .repartition(20) \
        .write.parquet(output_path, mode='overwrite')
    
    return output_path


# In[5]:


@task()
def write_gcs(path: str) -> None:
    """Upload local parquet file to GCS"""
    gcp_cloud_storage_bucket_block = GcsBucket.load("de-project-gcs")
    gcp_cloud_storage_bucket_block.upload_from_path(from_path=path, to_path=path)


# In[6]:


@flow()
def etl_web_to_gcs(year: int, version: str) -> None:
    chunk_size = 1048576 
    dataset_url = f"https://data.cityofnewyork.us/api/views/{version}/rows.csv?accessType=DOWNLOAD"

    input_dir = fetch_from_web (dataset_url, year, chunk_size)
    rootdir = clean(input_dir, year)
    
    for file in os.listdir(rootdir):
        f = os.path.join(rootdir, file)
        if os.path.isfile(f):
            write_gcs(f)


# In[7]:


@flow()
def etl_parent_flow(years: dict = {2023: 'pvqr-7yc4'}):
    for year, version in years.items():
        etl_web_to_gcs(year, version)

        


# In[8]:


if __name__ == "__main__":
    # years = {2023: 'pvqr-7yc4', 2022: '7mxj-7a6y', 2021: 'kvfd-bves', 2020: 'p7t3-5i9s', 2019: 'faiq-9dfq'}
    years = {2021: 'kvfd-bves'}
    etl_parent_flow(years)

