# Dokku Setup on EC2 Instructions

export PFURL=aljohri.com
export PFPEM=~/Desktop/politicalframing.pem
export APP=alpha
alias pf="ssh -i $PFPEM ubuntu@$PFURL"

echo "Creating 1GB swap space on EC2 instance."
pf "sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024"
pf "sudo /sbin/mkswap /var/swap.1"
pf "sudo /sbin/swapon /var/swap.1"
pf "sudo sh -c 'echo /var/swap.1 swap swap defaults 0 0 >> /etc/fstab'"

echo "Installing Dokku"
pf "echo 'export PFURL=$PFURL' >> ~/.bashrc"
pf "wget -qO- https://raw.github.com/progrium/dokku/v0.2.1/bootstrap.sh | sudo bash"
pf "export PFURL=$PFURL; sudo sh -c  'echo $PFURL > /home/dokku/VHOST'"

echo "Installing Dokku Plugins"
pf "sudo git clone https://github.com/statianzo/dokku-shoreman.git /var/lib/dokku/plugins/dokku-shoreman"
pf "sudo git clone https://github.com/Kloadut/dokku-pg-plugin /var/lib/dokku/plugins/postgresql"
pf "sudo git clone https://github.com/luxifer/dokku-redis-plugin /var/lib/dokku/plugins/redis"
pf "sudo git clone https://github.com/AlJohri/dokku-bower-grunt-build-plugin.git /var/lib/dokku/plugins/bower-grunt"
pf "sudo git clone https://github.com/Kloadut/dokku-md-plugin.git /var/lib/dokku/plugins/mariadb"
pf "sudo git clone https://github.com/dyson/dokku-persistent-storage.git /var/lib/dokku/plugins/persistent-storage"
pf "sudo dokku plugins-install"

echo "Send Public Key to EC2 Instance"
cat ~/.ssh/id_rsa.pub | pf "sudo sshcommand acl-add dokku progrium"

echo "Create Databases"
pf "sudo dokku postgresql:create $APP"
pf "sudo dokku redis:create $APP"

echo "Configure git and push"
git remote rm $APP
git remote add $APP "dokku@$PFURL:$APP"
git push $APP $APP:master

echo "Add environment variables"
pf "dokku postgresql:link $APP $APP"
pf "dokku config:set $APP HEROKU=1"
pf "dokku config:set $APP C_FORCE_ROOT=true"

# /home/dokku/piwik/storage/tmp:/app/tmp
# /home/dokku/piwik/storage/config:/app/config

# Wordpress
# GOOG_UA_ID:   UA-37924780-2

# PIWIK
# GOOG_UA_ID:   UA-37924780-2

# Because our AWS instance is associated with an elastic IP address, the PFURL should persist
# across deleting and re-creating the instance given the elastic IP is reassociated.

# Please note when doing anything that may change the instance's public IP (e.g. re-creating
# or upgrading) you will recieve an error "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!".
# It will be accompanied with a line in known_hosts to remove such as:
# Offending RSA key in /Users/atul/.ssh/known_hosts:18
# Simply delete this line and repeat the command.

# When upgrading or changing the AWS instance you must also reassociate teh elastic IP address
# with the instance.

# Remember that the PEM file must have permissions 400.
# chmod 400 politicalframing.pem

# EC2 Instance AMI: ami-ef795786
# EC2 Instance AMI url: https://console.aws.amazon.com/ec2/home?region=us-east-1#launchAmi=ami-ef795786
# EC2 Instance Finder: http://cloud-images.ubuntu.com/locator/ec2/
# Search Parameters: Ubuntu 13.04 raring amd64 ebs us-east-1