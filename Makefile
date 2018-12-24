
./output/us_map: ./data/us_map.json ./analyze.py
	mkdir -p $@
	./analyze.py -g $< -o ./output/us_map/

clean:
	-rm -rf output
