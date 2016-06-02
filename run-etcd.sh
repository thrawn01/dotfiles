#! /bin/sh

HOST=192.168.15.10
if [ $(docker ps -a | grep -ci etcd) -eq 0 ]; then
    docker run -d --name etcd -p 2379-2380:2379-2380 -p 4001:4001 -p 7001:7001 -v /tmp/etcd:/tmp/etcd \
        quay.io/coreos/etcd:v3.0.0-beta.0 --data-dir /tmp/etcd \
        -name etcd0 \
        -advertise-client-urls http://${HOST}:2379,http://${HOST}:4001 \
        -listen-client-urls http://0.0.0.0:2379,http://0.0.0.0:4001 \
        -initial-advertise-peer-urls http://${HOST}:2380 \
        -listen-peer-urls http://0.0.0.0:2380 \
        -initial-cluster-token etcd-cluster-1 \
        -initial-cluster etcd0=http://${HOST}:2380 \
        -initial-cluster-state new
else
    echo "etcd already running"
fi
