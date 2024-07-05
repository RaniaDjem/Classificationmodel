provider "google" {
  project = "terraform-424109"
  region  = "us-central1"
}

terraform {
  backend "gcs" {
    bucket = "bucket-de-machinelearning"
    prefix = "terraform/state"
  }
}

resource "google_cloud_run_service" "example" {
  name     = "predictionml"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/terraform-424109/my-repo/modelimage:latest"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
  
}

resource "google_cloud_run_service_iam_member" "noauth" {
  service    = google_cloud_run_service.example.name
  location   = google_cloud_run_service.example.location
  member     = "allUsers"
  role       = "roles/run.invoker"
}