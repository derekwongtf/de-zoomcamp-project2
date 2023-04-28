
# enable Dataproc API
resource "google_project_service" "dataproc" {
  project                    = var.project_id
  service                    = "dataproc.googleapis.com"
  disable_on_destroy         = true
  disable_dependent_services = true
}

# setup Dataproc cluster
resource "google_dataproc_cluster" "cluster" {
  name   = var.cluster_name
  region = var.region

  cluster_config {
    gce_cluster_config {
      zone = var.zone
      network    = google_compute_network.vpc_network.name
    }

    software_config {
      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "true"
      }
    }
  }

}
/*
resource "google_dataproc_cluster_iam_binding" "editor" {
  cluster = var.cluster_name
  role    = "roles/editor"
  members = [
    "serviceAccount:${google_service_account.service_account.email}",
  ]
}
*/