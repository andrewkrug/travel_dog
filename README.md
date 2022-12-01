# Sample application travel dog

Originally created for PRT326 at re:Invent 2022

# Getting started

## Prerequisites

* AWS CDK
* Docker on M1 (or other ARM)
* LaunchDarkly with flag triggers enabled
* Datadog Trial

## Setup some secrets

1. Add a Datadog API key to SSM: /datadog/reinvent2022/dd_api_key
2. Add a LaunchDarkly API key to SSM: /datadog/reinvent2022/ld_api_key

## Build and deploy the app

1. Create an ECR repository called "travel_dog_sample" in `us-west-2`
2. Run `make build`
3. Run `make tag`
4. Run `make push`
5. Install the python dependencies in a virtual env in the deploy folder
6. Activate the virtualenv
7. `cdk deploy`
8. The output will be the URL of your site
9. Visit ${YOUR_URL}/v1/seed to add users
10. The site is now active

# License 

MIT

# Author 

Andrew J Krug

# To-do

1. Add Lambda Function Code
2. Update ECS optimized AMI for Graviton to use Linux Kernel 5.x or greater