#!/bin/sh
# `set -eu` combines two shell options:
#    - `-e`: exit when an unhandled command fails.
#    - `-u`: treat expansion of an undefined variable as an error.

set -eu

if [ -f ./unobfuscate.sh ]; then
    sh ./unobfuscate.sh
fi
