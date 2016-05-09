#!/usr/bin/env bash

set -e

conda env create --channel bioconda environment_generic.yml

source activate virominer2

CONTAINING_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PTH_FILE=$CONDA_ENV_PATH/lib/python3.5/site-packages/virominer2.pth
echo "echo $CONTAINING_DIRECTORY > $PTH_FILE"
echo $CONTAINING_DIRECTORY > $PTH_FILE

ln -s `readlink -f $VIROMINER_DB/taxonomy` $CONDA_ENV_PATH/opt/krona/taxonomy


cd /home/jsmith/anaconda3/envs/analytics
mkdir -p ./etc/conda/activate.d
mkdir -p ./etc/conda/deactivate.d
touch ./etc/conda/activate.d/env_vars.sh
touch ./etc/conda/deactivate.d/env_vars.sh
Edit the two files. ./etc/conda/activate.d/env_vars.sh should have this:

#!/bin/sh

export MY_KEY='secret-key-value'
export MY_FILE=/path/to/my/file/
And ./etc/conda/deactivate.d/env_vars.sh should have this:

#!/bin/sh

unset MY_KEY
unset MY_FILE



source deactivate



