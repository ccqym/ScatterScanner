python scatter_scanner.py examples/sml_00001.png -o examples/out/scanner_sml1.json -O examples/out/scanner_sml1.png --out-point-size=3 --out-point-color=red
#exit
python scatter_scanner.py examples/sml_00001.png -o examples/out/scanner_sml1a.json -O examples/out/scanner_sml1a.png --out-point-size=3 --out-point-color=red --no-is-auto-kernel --kernel-side=9
python scatter_scanner.py examples/biomass.png  --is-hsv-s-channel -o examples/out/scanner_biomass.json -O examples/out/scanner_biomass.png --out-point-size=10 --out-point-color=black
python scatter_scanner.py examples/correlation.png --is-hsv-s-channel -o examples/out/scanner_correlation.json -O examples/out/scanner_correlation.png --is-remove-text-and-axis --remove-kernel-size=25 --out-point-size=21 --out-point-color=black
python scatter_scanner.py examples/multi_markers1.png -o examples/out/scanner_multi_markers1.json -O examples/out/scanner_multi_markers1.png --out-point-size=3 --out-point-color=red
python scatter_scanner.py examples/multi_markers2.png -o examples/out/scanner_multi_markers2.json -O examples/out/scanner_multi_markers2.png --out-point-size=3 --out-point-color=red
python scatter_scanner.py examples/multi_markers3.png -o examples/out/scanner_multi_markers3.json -O examples/out/scanner_multi_markers3.png --out-point-size=3 --out-point-color=red
