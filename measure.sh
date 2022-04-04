#!/bin/bash

config=$1


export PATH=$PATH:~/packages/bftools
#bfconvert -version
#sudo mount -t drvfs Z: /mnt/z
source venv/bin/activate
python ~/root_measurement/scripts/resumable_measure_from_config.py $config
python ~/root_measurement/scripts/gather_working_dir.py $config
python ~/root_measurement/scripts/generate_spherefit_visualisations.py $config
python ~/root_measurement/scripts/generate_projection_composites.py $config
deactivate
