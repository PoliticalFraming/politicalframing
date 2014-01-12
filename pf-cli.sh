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