import pulumi

class MyMocks(pulumi.runtime.Mocks):
  def new_resource(self, args: pulumi.runtime.MockResourceArgs):
    outputs = args.inputs
    return [args.name + '_id', outputs]

  def call(self, args: pulumi.runtime.MockCallArgs):
      return {}

pulumi.runtime.set_mocks(MyMocks())

pulumi.runtime.set_all_config({
  'project:backend_port': '3000',
  'project:frontend_port': '3001',
  'project:database': 'cart',
  'project:mongo_host': 'mongodb://mongo:27017',
  'project:mongo_port': '27017',
  'project:node_environment': 'development'
})

import my_first_app

@pulumi.runtime.test
def test_my_first_app_tags():
  def check_tags(args):
    urn, tags = args
    assert tags, f'instance {urn} must have tags'
    assert 'Name' in tags, f'instance {urn} must have a name tag'

  return pulumi.Output.all(my_first_app.cluster.urn, my_first_app.cluster.tags).apply(check_tags)
