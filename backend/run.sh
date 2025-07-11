#!/bin/bash

while read -r line; do
  # Run all scripts on all densities and version volumes
  for vol in "single" "small" "medium" "large" "hyperlarge"; do
    python src/SimulationWriter.py -v -V $vol $line &
    python src/SimulationWriter.py -v -V $vol -l 2 $line &
    python src/SimulationWriter.py -v -V $vol -b 20 $line &
    python src/SimulationWriter.py -v -V $vol -m 0.5 0 30 -m 0.5 100 40 $line &
  done
done < $1  # Take filename as user input
wait

