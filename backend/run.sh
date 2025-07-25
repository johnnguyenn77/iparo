#!/bin/bash

pythoncmd="python src/SimulationWriter.py -v -V"
while read -r line
do
  # Run all scripts on all densities and version volumes (besides hyper large for a certain set of )
  for vol in "single" "small" "medium" "large"
  do
    $pythoncmd $vol $line &
    $pythoncmd $vol -l 2 $line &
    $pythoncmd $vol -b 20 $line &
    $pythoncmd $vol -m 0.5 0 300 -m 0.5 1000 400 $line &
  done
done < "scripts.txt"
IFS=$'\n' read -d '' -ra arr <<< $(grep -F -v -f max-gap-scripts.txt scripts.txt)
for line in "${arr[@]}"
do
   $pythoncmd hyperlarge $line &
   $pythoncmd hyperlarge -l 2 $line &
   $pythoncmd hyperlarge -b 20 $line &
   $pythoncmd hyperlarge -m -m 0.5 0 300 -m 0.5 1000 400 $line &
done