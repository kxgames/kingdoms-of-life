#!/usr/bin/env sh

if [ $# -ne 1 ]; then
    echo "Usage: $0 <lag>"
    exit 1
fi

# Cleanup on unexpected exit.
trap "tc qdisc del dev lo root netem; echo; exit" SIGINT SIGTERM

# Add an artificial delay to the loopback interface.
tc qdisc add dev lo root netem delay $(($1 / 2))ms

# Wait until the user has finished testing.
read -p "Press <enter> to reset the network... " prompt

# Remove the delay from the loopback interface.
tc qdisc del dev lo root netem
