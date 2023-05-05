# Data Engineering - Zoomcamp - Project 2

# Overview
This project aims to build an end-to-end data pipeline using the various cloud technologies. It uses the datasets from the [New York City Open Data](https://data.cityofnewyork.us/City-Government/Parking-Violations-Issued-Fiscal-Year-2023/pvqr-7yc4).

# Problem
1. What is the trend of the total violation parking tickets over a certain period of time?
2. What are the major violation parking tickets?


# Technologies
* The following tools are used in this project.
* Terraform - manage the infrastructure resource on cloud
* Google Cloud Storage(GCS) - datalake
* Google Compute Engine(GCE) - virtual machine to host data pipeline
* Google BigQuery - data warehouse
* Prefect Cloud - manage and monitor the workflow
* Spark - process large-scale data
* dbt cloud - transformation tool to implement data modeling
* Looker Studio - visualize data and create dashboard


# Point to Note
* This project uses **GCS Bucket** as the data lake. The data file of each fiscal year is converted from a single csv into **hive-partitioned parquet** using the **SPARK**. 
 <img width="633" alt="image" src="https://user-images.githubusercontent.com/113747768/236157846-73ebd99e-9ad4-4523-be67-73c21cb5e334.png">

* The converted parquet files can be query in **Bigquery** with external table. 
<img width="854" alt="image" src="https://user-images.githubusercontent.com/113747768/236158387-0fd91579-8589-4574-91da-31e0550b1d7c.png">

* The **dbt** is used to transform data. It involves **joining 2 tables** of data, ***decoding*** violation code into human-understandable description, **cleaning** invalid data which is outside of particular fiscal year[^1].
<img width="537" alt="image" src="https://user-images.githubusercontent.com/113747768/236157128-bc3912aa-ed76-481d-a05e-c80e6391fc30.png">

* The transformed data is loaded to production dataset 'dbt_derekwongtf' with table 'fact_parking_tickets' ***partitioned by** 'Month' and **clustered by** 'Violation Code'
<img width="617" alt="image" src="https://user-images.githubusercontent.com/113747768/236158516-3a56e46e-42d0-4ff5-8932-25b796ec90d1.png">

# Dataflow Architecture
<img width="500" alt="image" src="https://user-images.githubusercontent.com/113747768/236186784-8e58f6f5-6f63-4e63-8bc9-ac3a1121eb9b.png">


# Dashboard
<img width="474" alt="image" src="https://user-images.githubusercontent.com/113747768/236154775-c5cbb4d5-bcc5-4018-b899-4107f6965cb7.png">
https://lookerstudio.google.com/s/jWdkdirwnyw


# Reproducability

Clone [this repository](https://github.com/derekwongtf/de-zoomcamp-project2.git) to your local workspace.

Open [google cloud console](https://console.cloud.google.com/) and create a new GCP project by clicking New Project button.

<img width="562" alt="image" src="https://user-images.githubusercontent.com/113747768/233042865-27712f7c-124d-4563-bfae-20cac6eb586d.png">

Run these two commands to spin up the gcp infrasturcture resources.
```
terraform -chdir=./infra/gcp init
terraform -chdir=./infra/gcp apply
```

```
NOTE: If you see this error, please rerun the command `terraform -chdir=./infra/gcp apply`
```
![image](https://user-images.githubusercontent.com/113747768/233051797-9a7bc598-563e-4401-b4de-371df27fccd2.png)


A ssh-key is created in folder /ssh for local machine to connect to the new VM. Copy this file to your $HOME/.ssh directory.
```
cp ssh/de-project ~/.ssh/
```

Get the KEY file of the new service account. 
```
terraform -chdir=infra/gcp output sa_private_key | base64 -di | jq > sa-de-project.json
```

Login to GCE 
```
ssh -i ~/.ssh/de-project [username of the cloud gmail]@[VM external IP address]
```

## In VM

Clone [this repository](https://github.com/derekwongtf/de-zoomcamp-project2.git) to VM workspace.

Back to home directory, create a new directory to install the spark.
```
mkdir spark
cd spark
wget https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
tar xzfv openjdk-11.0.2_linux-x64_bin.tar.gz
wget https://dlcdn.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz
tar xzfv spark-3.3.2-bin-hadoop3.tgz
```

Edit the .bashrc file
```
nano ~/.bashrc
```

Append new environment variables to .bashrc
```
export JAVA_HOME="${HOME}/spark/jdk-11.0.2"
export PATH="${JAVA_HOME}/bin:${PATH}"
export SPARK_HOME="${HOME}/spark/spark-3.3.2-bin-hadoop3"
export PATH="${SPARK_HOME}/bin:${PATH}"
```

Reload the .bashrc file
```
source ~/.bashrc
```

Install the following packages.
```
sudo apt update
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
pip install pyopenssl --upgrade
pip install prefect
pip install prefect_gcp
pip install tqdm
```
Note: if you encounter error when installing pyopenssl, try re-login to VM or reboot it.

Go to [Prefect Cloud](https://www.prefect.io/cloud/), generate a API Key on Prefect Cloud
![image](https://user-images.githubusercontent.com/113747768/236147432-04561725-8ecc-4609-a528-998c09e2f565.png)

Configure it to VM's Prefect 
```
prefect cloud login -k [Prefect Cloud API Key]
```

Deploy schedule run
```
prefect deployment build flows/vm-etl-web-to-gcs.py:etl_web_to_gcs -n "monthly-ingest" \
--params='{"year": 2023, "version": "pvqr-7yc4"}' \
--cron='0 0 1 * *' \
--apply
```

Deploy manual run 
```
prefect deployment build flows/vm-etl-web-to-gcs.py:etl_web_to_gcs -n "manual-ingest" \
--apply
```

Input the values for the parameters.
![image](https://user-images.githubusercontent.com/113747768/236148926-efbd1792-b293-414a-8fb9-a4ef09afce56.png)

Here is the input. 
| year      | version    |
| :-------: |:----------:|
| 2021      | kvfd-bves  |
| 2022      | 7mxj-7a6y  |


Go to [dbt Cloud](https://cloud.getdbt.com/). Create a new repository for dbt.

Create a new account on dbt cloud and setup a new project
![image](https://user-images.githubusercontent.com/113747768/236152344-7efc80f3-a17b-41e4-b243-44f615f0d404.png)

During the dbt project setup, configure the followings
<img width="853" alt="image" src="https://user-images.githubusercontent.com/113747768/236152492-adf314a1-41cb-46db-83c5-b5cb8fb9659f.png">
<img width="250" alt="image" src="https://user-images.githubusercontent.com/113747768/236152646-527e87e4-269d-48c9-a2e1-86ef6f5fee24.png">
<img width="415" alt="image" src="https://user-images.githubusercontent.com/113747768/236152841-47e7fede-30f3-473f-8ee2-d823bd227617.png">
<img width="423" alt="image" src="https://user-images.githubusercontent.com/113747768/236152930-fff8e574-73fb-4827-a3ec-942d8240eccc.png">

Select the repository created just now on github.
<img width="571" alt="image" src="https://user-images.githubusercontent.com/113747768/236153418-5d95afa0-78fd-45c7-af17-aa07a72c2925.png">

[^1] [City probes after News finds thousands of parking tickets written for violations that haven’t happened yet](https://www.nydailynews.com/news/politics/ny-parking-tickets-invalid-future-dates-20190609-pcia3ze3szbuxfr6c7ut2ilqvm-story.html)
