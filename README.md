#HOWTO

pip install -r requirements.txt

*remember to install aws-cli and login to your account, then*

fab ec2.create
fab docker
fab hosts

ssh ubuntu@ip-from-provious-step

etc...