from aws_cdk import (
    aws_iam as iam
)

def generate_task_role(stack):
        task_role = iam.Role(
            stack, 'TravelDogTaskRole',
            role_name = 'TravelDogTaskRole',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonECSTaskExecutionRolePolicy')]
        )

        task_role.add_to_policy(iam.PolicyStatement(
            resources=["arn:aws:ssm:*:*:parameter/datadog/reinvent2022/*"],
            actions=["ssm:DescribeParameters", "ssm:GetParameter"]
        ))

        task_role.add_to_policy(iam.PolicyStatement(
            resources=["*"],
            actions=["dynamodb:*"]
        ))

        task_role.add_to_policy(iam.PolicyStatement(
            resources=["*"],
            actions=["logs:CreateLogStream", "logs:PutLogEvents"]
        ))

        return task_role

def generate_role(stack):
    application_role = iam.Role(
        stack, 'TravelDogServiceRole',
        role_name = 'TravelDogServiceRole',
        assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
        managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonEC2RoleforSSM')]
    )

    application_role.add_to_policy(iam.PolicyStatement(
        resources=["arn:aws:ssm:*:*:parameter/datadog/reinvent2022/*"],
        actions=["ssm:DescribeParameters", "ssm:GetParameter"]
    ))

    application_role.add_to_policy(iam.PolicyStatement(
        resources=["arn:aws:ssm:*:*:parameter/datadog/reinvent2022/*"],
        actions=["ssm:DescribeParameters", "ssm:GetParameter"]
    ))

    application_role.add_to_policy(iam.PolicyStatement(
        resources=["arn:aws:ecs:*:*:cluster/TravelDogECSStack-*"],
        actions=[
            "ecs:DeregisterContainerInstance",
            "ecs:RegisterContainerInstance",
            "ecs:Submit*"
        ]
    ))

    application_role.add_to_policy(iam.PolicyStatement(
        resources=["*"],
        actions=["dynamodb:*"]
    ))

    application_role.add_to_policy(iam.PolicyStatement(
        resources=["*"],
        actions=[
            "ecs:Poll",
            "ecs:StartTelemetrySession",
            "ecr:GetAuthorizationToken",
            "ecs:DiscoverPollEndpoint",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ]
    ))

    application_role.add_to_policy(iam.PolicyStatement(
        resources=["arn:aws:ecr:*:*:repository/travel_dog_sample"],
        actions=[
            "ecr:BatchCheckLayerAvailability",
            "ecr:GetDownloadUrlForLayer",
            "ecr:GetRepositoryPolicy",
            "ecr:DescribeRepositories",
            "ecr:ListImages",
            "ecr:DescribeImages",
            "ecr:BatchGetImage",
        ]
    ))

    application_role.add_to_policy(iam.PolicyStatement(
        resources=["*"],
        actions=[
            "ecr:GetAuthorizationToken",
        ]
    ))

    application_role.add_to_policy(iam.PolicyStatement(
        resources=["*"],
        actions=["logs:CreateLogStream", "logs:PutLogEvents"]
    ))

    return application_role
