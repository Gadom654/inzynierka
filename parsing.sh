#!/bin/bash

#move current ami to old ami
#export TF_VAR_blue_ami_id="$TF_VAR_green_ami_id"

# Extract the AMI ID using jq
AMI_ID=$(jq -r '.builds[1].artifact_id' manifest.json | cut -d: -f2)

# Print the AMI ID (optional)
echo "Extracted AMI ID: $AMI_ID"

# Export the AMI ID as an environment variable
export TF_VAR_green_ami_id="$AMI_ID"

