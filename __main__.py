import os
import pulumi
import pulumi_docker as docker

config = pulumi.Config()
frontend_port = config.require_int('frontend_port')
backend_port = config.require_int('backend_port')
mongo_port = config.require_int('mongo_port')
mongo_host = config.require('mongo_host')
database = config.require('database')
node_environment = config.require('node_environment')
mongo_username = config.require('mongo_username')
mongo_password = config.require_secret('mongo_password')

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

# network
network = docker.Network('network', name=f'services:{stack}')

# mongo container
mongo_container = docker.Container(
  'mongo_container',
  name=f'mongo-{stack}',
  image=mongo_image.latest,
  ports=[docker.ContainerPortArgs(
    internal=mongo_port,
    external=mongo_port
  )],
  envs=[
    f'MONGO_INITDB_ROOT_USERNAME={mongo_username}',
    pulumi.Output.concat('MONGO_INITDB_ROOT_PASSWORD=', mongo_password)
  ],
  networks_advanced=[docker.ContainerNetworksAdvancedArgs(
    name=network.name,
    aliases=['mongo']
  )]
)

# backend container
backend_container = docker.Container(
  'backend_container',
  name=f'backend-{stack}',
  image=backend.base_image_name,
  ports=[docker.ContainerPortArgs(
    internal=backend_port,
    external=backend_port
  )],
  envs=[
    pulumi.Output.concat(
      'DATABASE_HOST=mongodb://',
      mongo_username,
      ':',
      mongo_password,
      '@',
      mongo_host,
      ':',
      f'{mongo_port}'
    ),
    f'DATABASE_NAME={database}?authSource=admin',
    f'NODE_ENV={node_environment}'
  ],
  networks_advanced=[docker.ContainerNetworksAdvancedArgs(
    name=network.name
  )],
  opts=pulumi.ResourceOptions(depends_on=[mongo_container])
)

data_seed_container = docker.Container(
  'data_seed_container',
  name='data_seed',
  image=mongo_image.latest,
  must_run=False,
  rm=True,
  opts=pulumi.ResourceOptions(depends_on=[backend_container]),
  mounts=[docker.ContainerMountArgs(
    target='/home/products.json',
    type='bind',
    source=f'{os.getcwd()}/app/data/products.json'
  )],
  command=[
    'sh', '-c',
    pulumi.Output.concat(
      'mongoimport --host ',
      mongo_host,
      ' -u ',
      mongo_username,
      ' -p ',
      mongo_password,
      ' --authenticationDatabase admin --db cart --collection products --type json --file /home/products.json --jsonArray'
    )
  ],
  networks_advanced=[docker.ContainerNetworksAdvancedArgs(
    name=network.name
  )]
)

# frontend container
frontend_container = docker.Container(
  'frontend_container',
  name=f'frontend-{stack}',
  image=frontend.base_image_name,
  ports=[docker.ContainerPortArgs(
    internal=frontend_port,
    external=frontend_port
  )],
  envs=[
    f'LISTEN_PORT={frontend_port}',
    f'HTTP_PROXY=backend-{stack}:{backend_port}'
  ],
  networks_advanced=[docker.ContainerNetworksAdvancedArgs(
    name=network.name
  )]
)

# exports
pulumi.export('url', f'http://localhost:{frontend_port}')
