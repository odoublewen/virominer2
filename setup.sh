#!/usr/bin/env bash
set -e

absPath(){
    [[ -d $1 ]] && { cd "$1"; echo "$(pwd -P)"; } || { cd "$(dirname "$1")"; echo "$(pwd -P)/$(basename "$1")"; }
}

# from http://stackoverflow.com/questions/3963716/how-to-manually-expand-a-special-variable-ex-tilde-in-bash/29310477#29310477
expandPath() {
  local path
  local -a pathElements resultPathElements
  IFS=':' read -r -a pathElements <<<"$1"
  : "${pathElements[@]}"
  for path in "${pathElements[@]}"; do
    : "$path"
    case $path in
      "~+"/*)
        path=$PWD/${path#"~+/"}
        ;;
      "~-"/*)
        path=$OLDPWD/${path#"~-/"}
        ;;
      "~"/*)
        path=$HOME/${path#"~/"}
        ;;
      "~"*)
        username=${path%%/*}
        username=${username#"~"}
        IFS=: read _ _ _ _ _ homedir _ < <(getent passwd "$username")
        if [[ $path = */* ]]; then
          path=${homedir}/${path#*/}
        else
          path=$homedir
        fi
        ;;
    esac
    resultPathElements+=( "$path" )
  done
  local result
  printf -v result '%s:' "${resultPathElements[@]}"
  printf '%s\n' "${result%:}"
}


echo "
Virominer2 setup
----------------
Step 1: User provides a path for the virominer databases.  
        Path should have 100+GB free space to accommodate blast and taxonomy databases.
Step 2: Conda environment called virominer2 will be automatically created and provisioned.

"

conda --version > /dev/null 2>&1 || { echo >&2 "Virominer setup requires conda. Aborting."; exit 1; }

read -e -p "Virominer2 database path: " VIROPATH

VIROPATH=$(expandPath $VIROPATH)
CONTAINING_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Virominer2 databases will be installed in $VIROPATH"
echo "Creating conda environment, this could take a few minutes..."

conda config --add channels bioconda
conda config --add channels r

conda env create --file $CONTAINING_DIRECTORY/environment_generic.yml || 
conda env update --file $CONTAINING_DIRECTORY/environment_generic.yml

echo "Conda env created.  Setting up paths..."
source activate virominer2
[[ ! -d $CONDA_ENV_PATH ]] && { echo "CONDA_ENV_PATH not a dir!"; source deactivate; exit; }
#PTH_FILE=$CONDA_ENV_PATH/lib/python3.5/site-packages/virominer2.pth
mkdir -p $CONDA_ENV_PATH/etc/conda/activate.d
mkdir -p $CONDA_ENV_PATH/etc/conda/deactivate.d
echo "export PYTHONPATH=$CONTAINING_DIRECTORY
export BLASTDB=$VIROPATH/blastdb
" > $CONDA_ENV_PATH/etc/conda/activate.d/env_vars.sh

echo "unset PYTHONPATH
unset BLASTDB
" > $CONDA_ENV_PATH/etc/conda/deactivate.d/env_vars.sh

ln -s $VIROPATH/taxonomy $CONDA_ENV_PATH/opt/krona/taxonomy


