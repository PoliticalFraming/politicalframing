# Dokku Setup on EC2 Instructions

export PFURL=ec2-54-224-242-94.compute-1.amazonaws.com
export PFPEM=~/Desktop/politicalframing.pem
export PFREPO=~/Dropbox/Development/politicalframing

alias pf="ssh -i $PFPEM ubuntu@$PFURL"
pf "sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024"
pf "sudo /sbin/mkswap /var/swap.1"
pf "sudo /sbin/swapon /var/swap.1"
pf "echo 'export PFURL=$PFURL' >> ~/.bashrc"
pf "echo 'export DOKKU_REPO=https://github.com/AlJohri/dokku.git' >> ~/.bashrc"
pf "echo 'export STACK_URL=https://github.com/AlJohri/buildstep.git' >> ~/.bashrc"
pf "wget -qO- https://raw.github.com/progrium/dokku/v0.2.1/bootstrap.sh | sudo bash"
pf "export PFURL=$PFURL; sudo sh -c  'echo $PFURL > /home/dokku/VHOST'"
pf "sudo git clone https://github.com/statianzo/dokku-shoreman.git /var/lib/dokku/plugins/dokku-shoreman"
pf "sudo git clone https://github.com/AlJohri/dokku-pg-plugin.git /var/lib/dokku/plugins/postgresql"
pf "sudo git clone https://github.com/AlJohri/dokku-redis-plugin /var/lib/dokku/plugins/redis"
pf "sudo dokku plugins-install"
pf "sudo dokku postgresql:create politicalframing"
pf "sudo dokku redis:create politicalframing"
cat ~/.ssh/id_rsa.pub | pf "sudo sshcommand acl-add dokku progrium"
cd $PFREPO && git remote add aws "dokku@$PFURL:politicalframing"

# git push aws master
# pf "sudo dokku config:set politicalframing HEROKU=1"
# pf "sudo dokku config:set politicalframing C_FORCE_ROOT='true'"

# Information
# EC2 Instance AMI: ami-ef795786
# EC2 Instance AMI url: https://console.aws.amazon.com/ec2/home?region=us-east-1#launchAmi=ami-ef795786
# EC2 Instance Finder: http://cloud-images.ubuntu.com/locator/ec2/
# Search Parameters: Ubuntu 13.04 raring amd64 ebs us-east-1