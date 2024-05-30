#!/bin/bash

dir=$(dirname "$0")

PATH=${PATH}:"${dir}"
export PATH

if [ $# -eq 0 ] ; then
    echo "Usage: $0 <file> [file ...]"
    exit 1
fi

grepthreaddump() {
    grepblocks.py -b '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' "$@"
}

oldt=''
n=1
cat "$@" | egrep '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' | sort | while read t ; do
    if [ "$t" != "$oldt" ] ; then
        n=1
    fi
    echo "$t"
    cat "$@" | grepthreaddump -g "$n" -n 1 "^$t" >/tmp/threadpool-usage-tmp.$$
    n=$(($n + 1))
    # Thread pool utilization is the number of threads in the pool that
    # are *not* executing getTask() versus the total number of threads in
    # the pool.
    echo "ThreadPool        Used    Total   Utilization"
    cat /tmp/threadpool-usage-tmp.$$ | (egrep --text '"http-[nb]io-((127.0.0.1-)?[0-9]+-)?exec-' ; echo MIServerWorker) | awk '{print $1}' | sed -e 's/"//g' -e 's/-[0-9][0-9]*$//' | sort -u | while read x ; do
        total=$(grep --text "$x" /tmp/threadpool-usage-tmp.$$ | wc -l)
        free=$(grepthread "$x" /tmp/threadpool-usage-tmp.$$ | grep --text getTask | wc -l)
        used=$((${total} - ${free}))
        utilization=$(bc -l <<EOF
scale = 2
${used} / ${total} * 100
EOF
        )
        # echo "x = $x, total = $total, free = $free"
        printf "%s  %s      %s      %s\n" "$x" "${used}" "${total}" "${utilization}"
    done
    echo
done
rm -f /tmp/threadpool-usage-tmp.$$
