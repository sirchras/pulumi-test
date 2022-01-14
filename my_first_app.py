import os
import pulumi
import pulumi_aws as aws

config = pulumi.Config()
registry_org = 'pulumi'
registry_stub = 'tutorial-pulumi-fundamentals'
frontend_port = config.require_int('frontend_port')
backend_port = config.require_int('backend_port')
mongo_port = config.require_int('mongo_port')
mongo_host = config.require('mongo_host')
database = config.require('database')
node_environment = config.require('node_environment')

stack = pulumi.get_stack()

# grab backend image
backend_image_name = 'backend'
backend_image_path = f'{registry_org}/{registry_stub}-{backend_image_name}:main'

# grab frontend image
frontend_image_name = 'frontend'
frontend_image_path = f'{registry_org}/{registry_stub}-{frontend_image_name}:main'

# grab database image
database_image_name = 'database'
database_image_path = f'{registry_org}/{registry_stub}-{database_image_name}:main'

# aws resources
cluster = aws.ecs.Cluster(
  'my-cluster',
  tags={
    'Name': 'tag'
  }
)

# mongodb resources

# app, frontend, backend config

# exports
