import aws_cdk as core
import aws_cdk.assertions as assertions

from deploy.deploy_stack import DeployStack

# example tests. To run these tests, uncomment this file along with the example
# resource in deploy/deploy_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DeployStack(app, "deploy")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
