# Dokku Setup on EC2 Instructions

# Because our AWS instance is associated with an elastic IP address, the PFURL should persist
# across deleting and re-creating the instance given the elastic IP is reassociated.

# Please note when doing anything that may change the instance's public IP (e.g. re-creating
# or upgrading) you will recieve an error "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!".
# It will be accompanied with a line in known_hosts to remove such as:
# Offending RSA key in /Users/atul/.ssh/known_hosts:18
# Simply delete this line and repeat the command.

# Remember that the PEM file must have permissions 400.
# chmod 400 politicalframing.pem

# Attempted to create a profile.d folder with environment variables but that didn't seem to work.

export PFURL=aljohri.com
export PFPEM=~/Desktop/politicalframing.pem
export APP=alpha
alias pf="ssh -i $PFPEM ubuntu@$PFURL"

function pflogs() {

	if [ -z "$1" ]; then
	  	echo "missing app name"
	    echo "usage: pflogs app"
	    return -1
	fi

  pf "dokku logs $1 -t"
}

function pfcreatedb() {

	if [ -z "$1" ]; then
	  	echo "missing app name"
	    echo "usage: pfcreatedb app"
	    return -1
	fi

	pf "dokku run $1 python manage.py createdb"
}

function pfdeletedb() {

	if [ -z "$1" ]; then
	  	echo "missing app name"
	    echo "usage: pfdeletedb app"
	    return -1
	fi

	pf "dokku run $1 python manage.py deletedb"
}

function pfpush() {

	if [ -z "$1" ]; then
	  	echo "missing app name"
	    echo "usage: pfush app"
	    return -1
	fi

	if [ "$1" = "-h" ]; then
		echo "usage: pfush app"
		echo "note: if 'app' is a branch in git"
	    echo "pfpush will push the branch named 'app' to aws"
	    echo "otherwise, it will push the master branch"
	    return -1
	fi	

	if ! git remote | grep -qi $1; then
	    echo "$1 is not a remote of this repo"
	    echo "check git remote -v"
	    return -1
	fi

	if git branch | grep -qi $1; then
	    git push $1 $1:master
	else
	    git push $1 master
	fi

}

pf "echo 'export PFURL=$PFURL' >> ~/.bashrc"
pf "wget -qO- https://raw.github.com/progrium/dokku/v0.2.1/bootstrap.sh | sudo bash"
pf "export PFURL=$PFURL; sudo sh -c  'echo $PFURL > /home/dokku/VHOST'"
pf "sudo git clone https://github.com/statianzo/dokku-shoreman.git /var/lib/dokku/plugins/dokku-shoreman"
pf "sudo git clone https://github.com/Kloadut/dokku-pg-plugin /var/lib/dokku/plugins/postgresql"
pf "sudo git clone https://github.com/luxifer/dokku-redis-plugin /var/lib/dokku/plugins/redis"
# pf "sudo git clone https://github.com/jeffutter/dokku-postgresql-plugin.git /var/lib/dokku/plugins/postgresql"
# pf "sudo git clone https://github.com/jeffutter/dokku-mongodb-plugin.git /var/lib/dokku/plugins/mongodb"
pf "sudo dokku plugins-install"

cat ~/.ssh/id_rsa.pub | pf "sudo sshcommand acl-add dokku progrium"

pf "dokku config:set $APP HEROKU=1"
pf "dokku config:set $APP C_FORCE_ROOT=true"
pf "sudo dokku postgresql:create $APP"
pf "sudo dokku redis:create $APP"

git remote add $APP "dokku@$PFURL:$APP"

# 1 GB swap space
# pf "sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024"
# pf "sudo /sbin/mkswap /var/swap.1"
# pf "sudo /sbin/swapon /var/swap.1"

# Information
# EC2 Instance AMI: ami-ef795786
# EC2 Instance AMI url: https://console.aws.amazon.com/ec2/home?region=us-east-1#launchAmi=ami-ef795786
# EC2 Instance Finder: http://cloud-images.ubuntu.com/locator/ec2/
# Search Parameters: Ubuntu 13.04 raring amd64 ebs us-east-1

# https://github.com/progrium/dokku/wiki/Recipes#specifying-a-custom-buildpack
