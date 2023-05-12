#!/bin/bash

# set variables
APP_NAME="[producePlots] === "
VARIABLES=("ssh" "temperature" "currents" "salinity")
LOG_PATH=/users_home/opa/medens-dev/operationalScripts/logs
SCRIPT_PATH=/users_home/opa/$USER/operationalScripts/medens-plotter
CONFIG_FILE="${SCRIPT_PATH}/config_zeus_dev.conf"
CTYPE="mean_spread"

# read input params
# - DATE is the production date
DATE=$1


##########################################
#
# bsub command re-definition
#
########################################## 

# redefining bsub
bsub () {
    echo bsub $* >&2
    command bsub $* | head -n1 | cut -d'<' -f2 | cut -d'>' -f1
}   

# activate conda environment
source $HOME/.bash_anaconda_3.7
conda activate /work/opa/medens-dev/.conda/plot

# iterate over the days and over the variables
for DAY in $(seq 0 8); do

    # debug print
    echo "$APP_NAME Day $DAY"

    for VAR in ${VARIABLES[*]}; do

	# debug print
	echo "$APP_NAME === Variable $VAR"

	# executable
	EXE_PATH=$SCRIPT_PATH/mean_spread_${VAR}.py
	echo -n "Invoking $SCRIPT_PATH/${CTYPE}_${VAR}.py ${CONFIG_FILE} ${DATE} ${DAY}..."	
	JOBID=$(bsub -q s_medium -P 0510 -J "plot_${CTYPE}_${VAR}_${DAY}" -o ${LOG_PATH}/plot_${CTYPE}_${VAR}_${DATE}_${DAY}__%J.log -e ${LOG_PATH}/plot_${CTYPE}_${VAR}_${DATE}_${DAY}__%J.err "python $EXE_PATH ${CONFIG_FILE} ${DATE} ${DAY}" &)
	echo $JOBID
	    	
    done
    
done
