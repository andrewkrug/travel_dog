from aws_cdk import (
    aws_ec2 as ec2
)

cluster_userdata = ec2.UserData.for_linux(shebang="#!/bin/bash -xe")
cluster_userdata.add_commands(
         "echo '======================================================='",
         "sudo yum update -y && sudo yum install jq unzip python-pip -y",
         "sudo python -m pip install awscli",
         "sudo systemctl start amazon-ssm-agent",
         "export AWS_DEFAULT_REGION=us-west-2",
         "DD_API_KEY=\"$(aws ssm get-parameter --name=/datadog/reinvent2022/dd_api_key --with-decryption --region us-west-2 | jq .Parameter.Value -r -c)\" DD_SITE=\"datadoghq.com\" bash -c \"$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)\"",
         "sudo echo \"runtime_security_config.enabled: true\" >> /etc/datadog-agent/security-agent.yaml",
         "sudo echo \"runtime_security_config.enabled: true\" >> /etc/datadog-agent/system-probe.yaml",
         "sudo echo \"runtime_security_config.network.enabled: true\" >> /etc/datadog-agent/system-probe.yaml",
         "sudo echo \"logs_enabled: true\" >> /etc/datadog-agent/datadog.yaml",
         "sudo echo \"logs_config.container_collect_all: true\" >> /etc/datadog-agent/datadog.yaml",
         "sudo echo \"apm_config.enabled: true\" >> /etc/datadog-agent/datadog.yaml",
         "sudo echo \"apm_config.apm_non_local_traffic: true\" >> /etc/datadog-agent/datadog.yaml",
         "sudo echo \"process_config.process_collection.enabled: true\" >> /etc/datadog-agent/datadog.yaml",
         "sudo echo \"process_config.container_collection.enabled: true\" >> /etc/datadog-agent/datadog.yaml",
         "sudo cp /etc/datadog-agent/conf.d/disk.d/conf.yaml.default /etc/datadog-agent/conf.d/disk.d/conf.yaml",
         "systemctl restart datadog-agent",
         "echo 'Patch the kernel to 5.x or later'",
         # "echo \"if [ ! -f /etc/.kernel-ng-installed ]; then \namazon-linux-extras install kernel-ng \ntouch /etc/.kernel-ng-installed \nreboot\nfi\" > /tmp/patch-kernel",
         # "sudo chmod +x /tmp/patch-kernel",
         # "sudo /tmp/patch-kernel",
)