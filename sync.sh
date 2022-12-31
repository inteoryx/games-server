#!/bin/bash

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

# Check git for changes.  If 'Your branch is up to date with 'origin/master'. is in the output, exit.
git fetch
output=$(git status)
if [[ $output == *"Your branch is up to date with 'origin/master'."* ]]; then
    echo "No changes to pull."
    exit 0
fi

# Pull the changes.
git pull

# Start a Screen with name of port running main.py
screen -dmS $alt_port python3 main.py $alt_port

# Run tests here.  For now, placeholder - always pass.
res=0

# If tests pass, kill the alt_port screen and restart nginx.
if [ $res -eq 0 ]; then
    sed -i "s/$main_port/$alt_port/g" /etc/nginx/sites-enabled/nowplayok
    service nginx restart
    screen -X -S $main_port quit
fi
