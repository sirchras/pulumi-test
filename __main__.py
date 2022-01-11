import os
import pulumi
import pulumi_docker as docker

stack = pulumi.get_stack()

# build backend image
backend_image_name = 'backend'
backend = docker.Image(
  backend_image_name,
  build=docker.DockerBuild(context=f'{os.getcwd()}/app/backend'),
  image_name=f'{backend_image_name}:{stack}',
  skip_push=True
)

# build frontend image
frontend_image_name = 'frontend'
frontend = docker.Image(
  frontend_image_name,
  build=docker.DockerBuild(context=f'{os.getcwd()}/app/frontend'),
  image_name=f'{frontend_image_name}:{stack}',
  skip_push=True
)

# build mongodb image
mongo_image = docker.RemoteImage('mongo', name='mongo:bionic')
