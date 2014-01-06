# Dokku Setup on EC2 Instructions

export PFURL=ec2-54-224-242-94.compute-1.amazonaws.com
export PFPEM=~/Desktop/politicalframing.pem
alias pf="ssh -i $PFPEM ubuntu@$PFURL"
# Create 1GB swap space
pf "sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024"
pf "sudo /sbin/mkswap /var/swap.1"
pf "sudo /sbin/swapon /var/swap.1"
# Set environment variables
pf "echo 'export PFURL=$PFURL' >> ~/.bashrc"
# Install dokku
pf "wget -qO- https://raw.github.com/progrium/dokku/v0.2.1/bootstrap.sh | sudo DOKKU_REPO=https://github.com/AlJohri/dokku.git STACK_URL=https://github.com/AlJohri/buildstep.git BUILD_STACK=true bash"
# Set VHOST
pf "export PFURL=$PFURL; sudo sh -c  'echo $PFURL > /home/dokku/VHOST'"
# Install dokku plugins
pf "sudo git clone https://github.com/statianzo/dokku-shoreman.git /var/lib/dokku/plugins/dokku-shoreman"
pf "sudo git clone https://github.com/AlJohri/dokku-pg-plugin.git /var/lib/dokku/plugins/postgresql"
pf "sudo git clone https://github.com/AlJohri/dokku-redis-plugin /var/lib/dokku/plugins/redis"
pf "sudo dokku plugins-install"
# Create databases
pf "sudo dokku postgresql:create politicalframing"
pf "sudo dokku redis:create politicalframing"
# Set SSH key
cat ~/.ssh/id_rsa.pub | pf "sudo sshcommand acl-add dokku progrium"
# Add git remote
git remote add aws "dokku@$PFURL:politicalframing"

# git push aws master
# pf "sudo dokku config:set politicalframing HEROKU=1"
# pf "sudo dokku config:set politicalframing C_FORCE_ROOT='true'"

# REMEMBER TO SEED DATABASE NOW!!!!!


# dokku run python createdb.py

# OR

# sudo docker run -i -t app/politicalframing:latest /bin/bash
# export HEROKU=1
# export DATABASE_URL= ((get value from dokku config politicalframing))
# export REDIS_URL= ((get value from dokku config politicalframing))
# /app/.heroku/python/bin/python /app/createdb.py

# Information
# EC2 Instance AMI: ami-ef795786
# EC2 Instance AMI url: https://console.aws.amazon.com/ec2/home?region=us-east-1#launchAmi=ami-ef795786
# EC2 Instance Finder: http://cloud-images.ubuntu.com/locator/ec2/
# Search Parameters: Ubuntu 13.04 raring amd64 ebs us-east-1





# https://github.com/progrium/dokku/wiki/Recipes#specifying-a-custom-buildpack