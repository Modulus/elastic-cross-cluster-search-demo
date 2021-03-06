import boto3
from fabric.decorators import task

amount = 1


def has_valid_name(instance):
    try:
        for tag in instance.tags:
            if tag["Key"] == "Name":
                return "node-" in tag["Value"]
        return False
    except TypeError:
        return False


@task
def create():
    # ubuntu 16.04 image
    image_id = "ami-f90a4880"

    ec2 = boto3.resource("ec2")
    print("Checking for existing instances firsts")

    instances = ec2.instances.filter(Filters=
                                     [
                                         {"Name": "instance-state-name", "Values": ["running"]}
                                     ])
    instance = [instance for instance in instances if has_valid_name(instance)]
    if len(instance) >= amount:
        print("Instances already created, skipping")
    else:
        print("No instances found")
        print("Creating instances")

        for i in range(1, amount + 1):
            instance_name = "node-{}".format(i)
            print("Creating instance {}".format(instance_name))
            ec2.create_instances(
                ImageId=image_id,
                MinCount=1, MaxCount=amount,
                InstanceType="t2.large",
                KeyName="id_rsa_tv2_aws",
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [{
                            'Key': 'Name',
                            'Value': '{}'.format(instance_name)
                        },
                            {
                                "Key": "Type",
                                "Value": "elastic"
                            }
                        ]
                    }
                ])

@task
def delete():
    ec2 = boto3.resource("ec2")
    instances = ec2.instances.filter(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])

    instance_ids = [instance.id for instance in instances if has_valid_name(instance)]
    print("Preparing to terminate")

    for instance_id in instance_ids:
        print(instance_id)

    print("Stopping insances and terminating")

    ec2.instances.filter(InstanceIds=instance_ids).stop()
    ec2.instances.filter(InstanceIds=instance_ids).terminate()


