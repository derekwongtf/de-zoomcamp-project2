#!/usr/bin/env python
# coding: utf-8

from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
import process_data
import requests
import os
from tqdm import tqdm

@task()
def fetch_from_web (dataset_url: str, year: int, chunk_size: int) -> str:
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

@task()
def clean(input_path: str, year: int) -> str:
    
    output_path = f'data/pq'
    process_data.spark_process(input_path, output_path, year)

    return output_path

@task()
def write_gcs(path: str) -> None:
    """Upload local folder of parquet files to GCS"""
    gcp_cloud_storage_bucket_block = GcsBucket.load("de-project-gcs")
    gcp_cloud_storage_bucket_block.upload_from_path(from_path=path,to_path=path)
    # gcp_cloud_storage_bucket_block.upload_from_folder(from_folder=path,to_folder=path)


@flow()
def etl_web_to_gcs(year: int, version: str) -> None:
    chunk_size = 1048576 
    dataset_url = f"https://data.cityofnewyork.us/api/views/{version}/rows.csv?accessType=DOWNLOAD"

    input_dir = fetch_from_web (dataset_url, year, chunk_size)
    rootdir = clean(input_dir, year)
    # write_gcs(rootdir)
    for root, dirs, files in os.walk(rootdir):
        for filename in files:
            filename = os.path.join(root, filename)
            write_gcs(filename)

@flow()
def etl_parent_flow(years: dict = {2023: 'pvqr-7yc4'}):
    for year, version in years.items():
        print(f'processing data for {year}')
        etl_web_to_gcs(year, version)
        
if __name__ == "__main__":
    # years = {2023: 'pvqr-7yc4', 2022: '7mxj-7a6y', 2021: 'kvfd-bves', 2020: 'p7t3-5i9s', 2019: 'faiq-9dfq'}
    years = {2022: '7mxj-7a6y'}
    etl_parent_flow(years)

