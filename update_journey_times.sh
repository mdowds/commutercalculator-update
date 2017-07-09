#!/usr/bin/env bash

path=$1
if [ -n "$path" ]; then
    result=`python3 -m journey_time`
    echo "$result"
    cd "$path"
    git add ccdb.sqlite
    git commit -m "$result"
fi
