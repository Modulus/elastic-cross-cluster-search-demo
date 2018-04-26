import boto3
from fabric.api import env, roles, task, run
from fabric.operations import put
from fabric.contrib import files

ec2 = boto3.resource("ec2")
instances = ec2.instances.filter(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])

public_ips = [instance.public_ip_address for instance in instances]


env.roledefs["nodes"] = public_ips
#env.roledefs["search"] = public_ips[3:4]
#env.roledefs["elastic"] = public_ips[0:3]

env.user = "ubuntu"
env.key_filename = "/Users/user/.ssh/id_rsa_tv2"

@task
def nodes():
    print("nodes available")
    for instance in [instance for instance in instances]:
        name = None
        for tag in instance.tags:
            if tag["Key"] == "Name":
                name = tag["Value"]
        print("id: {}, Name: {}, public_ip: {}, private_ip: {}".format(instance.id, name, instance.public_ip_address, instance.private_ip_address))
@task
def check():
    run("echo 'pong'")

@roles("nodes")
@task
def docker():
    run("sudo apt-get update")
    run("sudo apt-get remove docker docker-engine docker.io")
    run("sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common")
    run("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -")
    run("sudo apt-key fingerprint 0EBFCD88")
    run("sudo add-apt-repository 'deb [arch=amd64] https://download.docker.com/linux/ubuntu xenial stable'")
    run("sudo apt-get update")
    run("sudo apt-get -y install docker-ce")
    run("sudo docker pull docker.elastic.co/elasticsearch/elasticsearch-oss:6.2.4")

    if not files.exists("/home/ubuntu/config"):
        run("mkdir /home/ubuntu/config")

    put("./docker-compose.yml", "/home/ubuntu/docker-compose.yml")
    put("./config/elastic.yml", "/home/ubuntu/config/elastic.yml")
    put("./config/kibana.yml", "/home/ubuntu/config/kibana.yml")
    put("./config/search.yml", "/home/ubuntu/config/search.yml")

    # Install docker compose
    run("sudo apt-get install python-pip -y")
    run("pip install docker-compose")


@roles("nodes")
@task
def config():
    if not files.exists("/home/ubuntu/config"):
        run("mkdir /home/ubuntu/config")
    put("./docker-compose.yml", "/home/ubuntu/docker-compose.yml")
    put("./config/elastic.yml", "/home/ubuntu/config/elastic.yml")
    put("./config/kibana.yml", "/home/ubuntu/config/kibana.yml")
    put("./config/search.yml", "/home/ubuntu/config/search.yml")

import ec2