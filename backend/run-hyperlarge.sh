#!/bin/bash

comprehensive="-c -o Results/Comprehensive"
maxgap="-g 2 -o Results/Sequential-2-Max-Gap"
maxgap4="-g 4 -o Results/Sequential-4-Max-Gap"
pythoncmd="python src/SimulationWriter.py -v -V hyperlarge"

IFS=$'\n' read -d '' -ra arr <<< $(grep -F -v -f memory-intensive-scripts.txt max-gap-scripts.txt)
for line in "${arr[@]}"; do
   $pythoncmd $line &
   $pythoncmd -l 2 $line &
   $pythoncmd -b 20 $line &
   $pythoncmd -m 0.5 0 30 -m 0.5 100 40 $line &
   wait
done

$pythoncmd $maxgap4 &
$pythoncmd -l 2 $maxgap4 &
wait
$pythoncmd -b 20 $maxgap4 &
$pythoncmd -m 0.5 0 30 -m 0.5 100 40 $maxgap4 &
wait

$pythoncmd $maxgap &
$pythoncmd -l 2 $maxgap &
wait
$pythoncmd -b 20 $maxgap &
$pythoncmd -m 0.5 0 30 -m 0.5 100 40 $maxgap &
wait

$pythoncmd $comprehensive
$pythoncmd -l 2 $comprehensive
$pythoncmd -b 20 $comprehensive
$pythoncmd -m 0.5 0 30 -m 0.5 100 40 $comprehensive
