variable "active_deployment" {
  description = "Indicates the active deployment environment: blue or green"
  type        = string
  default     = "blue"  # You can set a default value or leave it without a default
}
variable "is_green_active" {
  description = "Determines if the green environment is active"
  type        = bool
  default     = false
}

