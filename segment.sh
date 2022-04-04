#!/bin/bash

config=$1


export PATH=$PATH:~/packages/bftools
#bfconvert -version
#sudo mount -t drvfs Z: /mnt/z
source venv/bin/activate
python scripts/quick_convert_to_ids_lif.py $config
python scripts/segment_to_ds_only_one_specified_in_code.py $config
deactivate
