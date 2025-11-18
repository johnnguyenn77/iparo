#!/bin/bash

for module in $(ls test/[^_]*)
do
  module=${module##*/}
  module=${module%.*}
  if [ "$module" != "SysIPFSDateTest" -a "$module" != "IPAROTestConstants" -a \
  "$module" != "IPAROTestHelpers" -a "$module" != "IPAROStrategyTest" ]
  then
    python3 -m unittest "test.${module}" -v
  fi
done