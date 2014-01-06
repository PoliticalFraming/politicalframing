# Dokku Setup on EC2 Instructions

export PFURL=ec2-54-224-242-94.compute-1.amazonaws.com
export PFPEM=~/Desktop/politicalframing.pem
alias pf="ssh -i $PFPEM ubuntu@$PFURL"

pf "sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024"
pf "sudo /sbin/mkswap /var/swap.1"
pf "sudo /sbin/swapon /var/swap.1"
pf "echo 'export PFURL=$PFURL' >> ~/.bashrc"
pf "wget -qO- https://raw.github.com/progrium/dokku/v0.2.1/bootstrap.sh | sudo bash"
pf "export PFURL=$PFURL; sudo sh -c  'echo $PFURL > /home/dokku/VHOST'"
pf "sudo git clone https://github.com/statianzo/dokku-shoreman.git /var/lib/dokku/plugins/dokku-shoreman"
pf "sudo git clone https://github.com/teemow/dokku-pg-plugin /var/lib/dokku/plugins/postgresql"
pf "sudo git clone https://github.com/luxifer/dokku-redis-plugin /var/lib/dokku/plugins/redis"
pf "sudo dokku plugins-install"
pf "sudo dokku postgresql:create $PFURL"
pf "sudo dokku redis:create $PFURL"
cat ~/.ssh/id_rsa.pub | pf "sudo sshcommand acl-add dokku progrium"
git remote add aws "dokku@$PFURL:$PFURL"
git push aws master
dokku run python createdb.py

# I changed the script to use the default buildstep and use the scipy/numpy buildpack using an environment variable.
# I also changed the declaration of environment variables to be within a .env file.
# pf "wget -qO- https://raw.github.com/progrium/dokku/v0.2.1/bootstrap.sh | sudo STACK_URL=https://github.com/AlJohri/buildstep.git BUILD_STACK=true bash"

# Information
# EC2 Instance AMI: ami-ef795786
# EC2 Instance AMI url: https://console.aws.amazon.com/ec2/home?region=us-east-1#launchAmi=ami-ef795786
# EC2 Instance Finder: http://cloud-images.ubuntu.com/locator/ec2/
# Search Parameters: Ubuntu 13.04 raring amd64 ebs us-east-1

# https://github.com/progrium/dokku/wiki/Recipes#specifying-a-custom-buildpack