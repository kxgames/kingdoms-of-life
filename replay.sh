#!/usr/bin/env sh

prefix=$1
histogram="replay.histogram${prefix}"
output="replay.output${prefix}"

if [ -e $histogram ]; then
    read -p "Overwrite previous runs? " yn
    if [ _$yn = _n ]; then
        exit
    else
        rm $histogram
        rm $output
    fi
fi

# Watch one game to make sure things look reasonable.
./debug.py --wealthy &> /dev/null

# Play 100 game in batch mode to collect statistics.
for iteration in {000..100}; do
    echo -n "${iteration}... "
    ./debug.py --wealthy --batch &> buffer

    cat buffer >> $output
    grep KeyError buffer > /dev/null

    if [ $? -eq 0 ]; then
        echo "broke" | tee --append $histogram
    else
        echo "worked" | tee --append $histogram
    fi

    rm buffer
done

echo -n "Failure Percent: "
grep "broke" $histogram | wc -l
