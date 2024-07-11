sitl="./arducopter -w --model copter --speedup 8 --defaults copter.parm --home 36.715606689453125,3.1846301555633545,0.0,0.0"
vehicle="python main.py"

cleanup() {
  rm eeprom.bin
  rm -r logs
  rm -r terrain
}

move() {
  file_name="data.csv"
  dir_name="real_missions"

  if [ -z "$file_name" ]; then
    echo "Error: Please provide a file name as the first argument."
    exit 1
  fi

  base_name="${file_name%.*}"
  extension="${file_name##*.}"

  if [ ! -d "$dir_name" ]; then
    echo "Error: Directory '$dir_name' does not exist."
    exit 1
  fi

  counter=1
  while [ -f "$dir_name/$base_name-$counter.$extension" ]; do
    counter=$((counter + 1))
  done

  new_file_name="$base_name-$counter.$extension"

  mv "$file_name" "$dir_name/$new_file_name"
  echo "Moved '$file_name' to '$dir_name/$new_file_name'"
}

trap cleanup INT

for i in $(seq 1 600); do
  echo "Running iteration $i..."

  $sitl > /dev/null &
  sitl_pid=$!

  $vehicle
  vehicle_pid=$!

  kill "$sitl_pid"
  move
  cleanup
done

echo "All 600 iterations completed. sim_vehicle.py likely terminated after each do_mission.py."

