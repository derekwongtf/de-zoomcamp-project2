resource "google_bigquery_dataset" "raw_gcs_data" {
  dataset_id                      = var.raw_bq_dataset
  description                     = "data from gcs"
  location                        = var.region
}

resource "google_bigquery_table" "table" {
  dataset_id          = google_bigquery_dataset.raw_gcs_data.dataset_id
  table_id            = var.table_id
  deletion_protection = false
  external_data_configuration {
    autodetect    = false # true
    source_uris   = ["gs://${google_storage_bucket.data-lake-bucket.name}/*.parquet"]
    source_format = "PARQUET"
    hive_partitioning_options {
      mode                     = "CUSTOM"
      source_uri_prefix        = "gs://${google_storage_bucket.data-lake-bucket.name}/data/pq/{Fiscal_Year:INTEGER}/{Issue_Year:INTEGER}/{Issue_Month:INTEGER}"
      require_partition_filter = false
    }
  }
  schema = file("yearly_data_external_tabledef.json")
}