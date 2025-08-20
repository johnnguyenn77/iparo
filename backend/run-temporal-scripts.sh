pythoncmd="python src/SimulationWriter.py -S -v -V"

while read -r line
do
  # Run all scripts on all densities and version volumes (besides huge)
  for vol in 1 10 100 1000 1000
  do
    $pythoncmd $vol $line &
    $pythoncmd $vol -l 2 $line &
    $pythoncmd $vol -b 20 $line &
    $pythoncmd $vol -m 0.5 0 300 -m 0.5 1000 400 $line &
    wait
  done
done < "temporal-scripts.txt"