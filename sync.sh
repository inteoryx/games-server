# The two ports that the service will use.
p1=8000
p2=8001

# Read the nginx config.  If p1 is there, p1 is main_port and p2 is alt_port.
if grep -q $p1 /etc/nginx/sites-enabled/nowplayok; then
    main_port=$p1
    alt_port=$p2
else
    main_port=$p2
    alt_port=$p1
fi

echo "Main port is $main_port, alt port is $alt_port"

# Check git for changes.  If no changes, exit.
git fetch
if git diff --quiet origin/master; then
    echo "No changes"
    exit 0
fi
