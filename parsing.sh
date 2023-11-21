#!/bin/bash

# Extract current used AMI ID from tf state
AMI_BLUE_ID=$(terraform show -json | jq -r '.values.root_module.resources[] | select(.address == "aws_instance.blue[0]") | .values.ami')

# Extract the AMI ID using jq
AMI_ID=$(jq -r '.builds[0].artifact_id' manifest.json | cut -d: -f2)

# Print the AMI ID (optional)
echo "Extracted AMI ID: $AMI_BLUE_ID"

# Export the AMI ID as an environment variable
export TF_VAR_green_ami_id="$AMI_ID"
export TF_VAR_blue_ami_id="$AMI_BLUE_ID"
