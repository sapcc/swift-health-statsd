#!/bin/bash
exec kubectl --namespace=swift exec "$(kubectl --namespace=swift get pods -l component=swift-proxy-cluster-3 --no-headers | awk '{print$1}' | head -n1)" -- swift-dispersion-report "$@"
