# de-zoomcamp-project2

# Reproducability

Open [google cloud console](https://console.cloud.google.com/) and create a new GCP project by clicking New Project button.

<img width="562" alt="image" src="https://user-images.githubusercontent.com/113747768/233042865-27712f7c-124d-4563-bfae-20cac6eb586d.png">

Run these two command to spin up the gcp infrasturcture.
```
terraform -chdir=./infra/gcp init
terraform -chdir=./infra/gcp apply
```

```
NOTE: If you see this error, please rerun the 
![image](https://user-images.githubusercontent.com/113747768/233051797-9a7bc598-563e-4401-b4de-371df27fccd2.png)
``

A ssh-key is created in folder /ssh for local machine to connect to the new VM. Copy this file to your $HOME/.ssh directory.
```
cp ssh/de-project ~/.ssh/
```

Get the KEY file of the new service account. 
```
terraform -chdir=infra/gcp output sa_private_key | base64 -di | jq > sa-de-project.json
```
