#!/bin/bash

echo "Building conda package ..."

cd conda_pkg

# remove old packages
conda-build purge

# building conda packages
conda-build .


# convert package to other platforms
# cd ~
# platforms=( linux-64 )
# find /home/eenpar/AppData/Local/Continuum/anaconda3/conda-bld/win-64/ -name *.tar.bz2 | while read file
# do
#     echo $(cygpath -w $file)
#     #conda convert --platform all $file  -o $HOME/conda-bld/
#     for platform in "${platforms[@]}"
#     do
#        conda convert -f --platform $platform $(cygpath -w $file)  -o $(cygpath -w /home/eenpar/AppData/Local/Continuum/anaconda3/conda-bld/)
#     done
    
# done

# # upload packages to conda
# find /home/eenpar/AppData/Local/Continuum/anaconda3/conda-bld/ -name *.tar.bz2 | while read file
# do
#     echo $file
#     anaconda upload $(cygpath -w $file)
#     rm $file
# done

echo "Building conda package done!"