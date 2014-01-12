# Dokku Setup on EC2 Instructions

export PFURL=aljohri.com
export PFPEM=~/Desktop/politicalframing.pem
alias pf="ssh -i $PFPEM ubuntu@$PFURL"
alias pflogs="pf 'dokku logs politicalframing -t'"
pf "echo 'export PFURL=$PFURL' >> ~/.bashrc"
pf "wget -qO- https://raw.github.com/progrium/dokku/v0.2.1/bootstrap.sh | sudo bash"
pf "export PFURL=$PFURL; sudo sh -c  'echo $PFURL > /home/dokku/VHOST'"
pf "sudo git clone https://github.com/statianzo/dokku-shoreman.git /var/lib/dokku/plugins/dokku-shoreman"
pf "sudo git clone https://github.com/teemow/dokku-pg-plugin /var/lib/dokku/plugins/postgresql"
pf "sudo git clone https://github.com/luxifer/dokku-redis-plugin /var/lib/dokku/plugins/redis"
pf "sudo dokku plugins-install"
pf "sudo dokku postgresql:create politicalframing"
pf "sudo dokku redis:create politicalframing"
cat ~/.ssh/id_rsa.pub | pf "sudo sshcommand acl-add dokku progrium"
git remote add aws "dokku@$PFURL:politicalframing"
git push aws master


pf "dokku config:set politicalframing HEROKU=1"
pf "dokku config:set politicalframing C_FORCE_ROOT=true"
pf "dokku run politicalframing python createdb.py"

# nginx temp fix
pfpush() {
	git push aws master
	pf "sudo sed -i 's/politicalframing\.//g' /home/dokku/politicalframing/nginx.conf"
	pf "sudo nginx -s reload"
}

# remove subdomain from /home/dokku/politicalframing/nginx.conf

# for micro instance only - 1 GB swap space
# pf "sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024"
# pf "sudo /sbin/mkswap /var/swap.1"
# pf "sudo /sbin/swapon /var/swap.1"

# Information
# EC2 Instance AMI: ami-ef795786
# EC2 Instance AMI url: https://console.aws.amazon.com/ec2/home?region=us-east-1#launchAmi=ami-ef795786
# EC2 Instance Finder: http://cloud-images.ubuntu.com/locator/ec2/
# Search Parameters: Ubuntu 13.04 raring amd64 ebs us-east-1

# https://github.com/progrium/dokku/wiki/Recipes#specifying-a-custom-buildpack
