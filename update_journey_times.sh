#!/usr/bin/env bash

path=$1
if [ -n "$path" ]; then
    cd "$path"
    result=`python3 -m api.data.update.journey_time`
    echo "$result"
    cd data
    git add ccdb.sqlite
    git commit -m "$result"
fi
