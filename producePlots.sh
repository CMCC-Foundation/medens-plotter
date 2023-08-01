#!/bin/bash

# set variables
APP_NAME="[producePlots] === "
VARIABLES=("ssh" "temperature" "currents" "salinity")
LOG_PATH=/work/opa/medens-dev/logs
SCRIPT_PATH=/users_home/opa/$USER/operationalScripts/medens-plotter
CONFIG_FILE="${SCRIPT_PATH}/config_zeus_dev.conf"

# read input params
# - DATE is the production date
DATE=$1

source $HOME/.bash_profile


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

# iterate over the days for mean spread plots
for DAY in $(seq 0 8); do

    # debug print
    echo "$APP_NAME Day $DAY"

    # iterate over variables
    for VAR in ${VARIABLES[*]}; do

	# debug print
	echo "$APP_NAME === Variable $VAR"

	    # executable
	    EXE_PATH=$SCRIPT_PATH/mean_spread_${VAR}.py
	    echo -n "Invoking $SCRIPT_PATH/mean_spread_${VAR}.py ${CONFIG_FILE} ${DATE} ${DAY}..."
	    
	    JOBID=$(bsub -q s_medium -P 0510 -J "plot_mean_spread_${VAR}_${DAY}" -o ${LOG_PATH}/plot_mean_spread_${VAR}_${DATE}_${DAY}__%J.log -e ${LOG_PATH}/plot_mean_spread_${VAR}_${DATE}_${DAY}__%J.err "python $EXE_PATH ${CONFIG_FILE} ${DATE} ${DAY}" &)
	    echo $JOBID
	    
    done
    
done

# iterate over the variables for postage charts
for VAR in ${VARIABLES[*]}; do
    
    # debug print
    echo "$APP_NAME === Variable $VAR"
    
    # executable
    EXE_PATH=$SCRIPT_PATH/postage_${VAR}.py
    echo -n "Invoking $SCRIPT_PATH/postage_${VAR}.py ${CONFIG_FILE} ${DATE} ${DAY}..."
	    
    JOBID=$(bsub -q s_medium -P 0510 -J "plot_postage_${VAR}_${DAY}" -o ${LOG_PATH}/plot_postage_${VAR}_${DATE}_${DAY}__%J.log -e ${LOG_PATH}/plot_postage_${VAR}_${DATE}_${DAY}__%J.err "python $EXE_PATH ${CONFIG_FILE} ${DATE} ${DAY}" &)
    echo $JOBID
    
done	   
