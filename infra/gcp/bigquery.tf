resource "google_bigquery_dataset" "raw_gcs_data" {
  dataset_id                      = var.raw_bq_dataset
  description                     = "data from gcs"
  location                        = var.region
}