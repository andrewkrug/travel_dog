import iam_roles
import userdata
from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_ecs_patterns as ecs_patterns,
    App, CfnOutput, Stack
)

from aws_cdk.aws_ecr_assets import DockerImageAsset
from constructs import Construct
from pathlib import Path


class TravelDogECS(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, *kwargs)

        instance_role = iam_roles.generate_role(self)

        vpc = ec2.Vpc(
            self, "TravelDogVpc",
            max_azs=2
        )

        cluster = ecs.Cluster(
            self, 'TravelDogEc2Cluster',
            vpc=vpc
        )

        asg = autoscaling.AutoScalingGroup(
            self, "TravelDogDefaultAutoScalingGroup",
            instance_type=ec2.InstanceType("a1.medium"),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(ecs.AmiHardwareType.ARM),
            vpc=vpc,
            user_data=userdata.cluster_userdata,
            role=instance_role
        )

        capacity_provider = ecs.AsgCapacityProvider(self, "TravelDogAsgCapacityProvider",
            auto_scaling_group=asg
        )
        cluster.add_asg_capacity_provider(capacity_provider)

        table = dynamodb.Table(self, "Users",
            partition_key=dynamodb.Attribute(name="username", type=dynamodb.AttributeType.STRING),
            table_name="traveldog-users"
        )

        task_role = iam_roles.generate_task_role(self)
        ecs_service = ecs_patterns.NetworkLoadBalancedEc2Service(
            self, "Ec2Service",
            cluster=cluster,
            memory_limit_mib=512,
            task_image_options=ecs_patterns.NetworkLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry(f"{self.account}.dkr.ecr.us-west-2.amazonaws.com/travel_dog_sample:latest"),
                task_role=task_role,
                execution_role=task_role,
                environment=dict(
                    FLASK_info="1",
                    DD_APPSEC_ENABLED="true",
                    DD_TRACE_AGENT_PORT="8126",
                    DD_LOGS_INJECTION="true",
                    DD_ENV="development",
                    DD_SERVICE="travel_dog",
                    DD_VERSION="2.1.1",
                    DD_AGENT_HOST="172.17.0.1",
                    AWS_DEFAULT_REGION="us-west-2",
                    CREATE_TABLES="False"
                )
            )
        )

        asg.connections.allow_from_any_ipv4(port_range=ec2.Port.tcp_range(80,80), description="TravelDog allow incoming traffic from ALB")
        asg.connections.allow_from_any_ipv4(port_range=ec2.Port.tcp_range(32768, 65535), description="allow incoming traffic from ALB")

        CfnOutput(
            self, "TravelDogLoadBalancerDNS",
            value="http://"+ecs_service.load_balancer.load_balancer_dns_name
        )

app = App()
TravelDogECS(app, "TravelDogECSStack")
app.synth()
