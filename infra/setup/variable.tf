variable "tf_state_bucket" {
  description = "Name of S3 bucket in AWS for storing TF state"
  default     = "devops-pycam-app-state"
}

variable "tf_state_lock_table" {
  description = "Name of DynamoDB table for TF state locking"
  default     = "devops-pycam-app-tf-lock"
}

variable "project" {
  description = "Project name for tagging resources"
  default     = "pycam-app-api"
}

variable "contact" {
  description = "Contact name for tagging resources"
  default     = "harriajames98@gmail.com"
}

