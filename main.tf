terraform {
  cloud {
    organization = "projectwsb"

    workspaces {
      name = "Projektinzynierski"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.24.0"
    }
  }

  required_version = ">= 1.4.0"
}
