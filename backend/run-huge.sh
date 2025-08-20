#!/bin/bash

comprehensive="-c -o Results/Comprehensive/None"
maxgap2="-g 2 -o Results/Sequential-Max-Gap/2"
maxgap4="-g 4 -o Results/Sequential-Max-Gap/4"
pythoncmd="python src/SimulationWriter.py -v -V 10000"

IFS=$'\n' read -d '' -ra arr <<< $(grep -F -v -f memory-intensive-scripts.txt max-gap-scripts.txt)
for line in "${arr[@]}"
do
   $pythoncmd $line &
   $pythoncmd -l 2 $line &
   $pythoncmd -b 20 $line &
   $pythoncmd -m 0.5 0 300 -m 0.5 1000 400 $line &
   wait
done

$pythoncmd $maxgap4 &
$pythoncmd -l 2 $maxgap4 &
wait
$pythoncmd -b 20 $maxgap4 &
$pythoncmd -m 0.5 0 300 -m 0.5 1000 400 $maxgap4 &
wait

$pythoncmd $maxgap2 &
$pythoncmd -l 2 $maxgap2 &
wait
$pythoncmd -b 20 $maxgap2 &
$pythoncmd -m 0.5 0 300 -m 0.5 1000 400 $maxgap2 &
wait

$pythoncmd $comprehensive
$pythoncmd -l 2 $comprehensive
$pythoncmd -b 20 $comprehensive
$pythoncmd -m 0.5 0 300 -m 0.5 1000 400 $comprehensive
