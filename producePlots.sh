#!/bin/bash


####################################################################
#
# Initial configuration
#
####################################################################

# for pretty output
APP_NAME="[producePlots] === "

# load configuration file
if [[ -z $1 ]]; then
    echo "[$APPNAME] -- ERROR -- Configuration file not provided!"
    exit
else
    CONFIG_FILE=$1
    if [[ -e $CONFIG_FILE ]]; then
	echo "[$APPNAME] -- Loading $CONFIG_FILE"
	source $CONFIG_FILE
    else
	echo "[$APPNAME] -- ERROR -- Configuration file $CONFIG_FILE not found!"
	exit
    fi				
fi

# read plot configuration filename
if [[ -z $2 ]]; then
    echo "[$APPNAME] -- ERROR -- Plot configuration file not provided!"
    exit
else
    PLOT_CONFIG_FILE=$2
    if [[ ! -e $PLOT_CONFIG_FILE ]]; then
	echo "[$APPNAME] -- ERROR -- Configuration file $PLOT_CONFIG_FILE not found!"
	exit
    fi				
fi

# load .bashrc file
source $HOME/.bashrc
source $HOME/.bash_profile

# conda
if [[ ! -z $CONDA_CONFIG_FILE ]]; then
    echo "[$APPNAME] -- Loading $CONDA_CONFIG_FILE"
    source $CONDA_CONFIG_FILE
fi
echo "[$APPNAME] -- Activating conda environment $CONDA_ENV_NAME"
conda activate $CONDA_PLOT_ENV_NAME

# telegram config
echo "[$APPNAME] -- Loading $TELEGRAM_CONFIG_FILE"
source $TELEGRAM_CONFIG_FILE

# set variables
VARIABLES=("ssh" "temperature" "currents" "salinity")

# set paths
SCRIPT_PATH=$PLOTTER_BASE_PATH

# read input params
DATE=$3

# debug info
$TELEGRAM -t $TELEGRAMBOT -c $TELEGRAMCHAT "$(echo -e '\U00002699') ProducePlot script is starting! [$DATE]"


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

# iterate over the days for mean spread plots
for DAY in $(seq 0 8); do

    # debug print
    echo "$APPNAME Day $DAY"

    # iterate over variables
    for VAR in ${VARIABLES[*]}; do

	# debug print
	echo "$APPNAME === Variable $VAR"

	    # executable
	    EXE_PATH=$SCRIPT_PATH/mean_spread_${VAR}.py
	    echo -n "Invoking $SCRIPT_PATH/mean_spread_${VAR}.py ${PLOT_CONFIG_FILE} ${DATE} ${DAY}..."
	    
	    JOBID=$(bsub -q s_medium -P 0510 -J "plot_mean_spread_${VAR}_${DAY}" -o ${LOG_PATH}/plot_mean_spread_${VAR}_${DATE}_${DAY}__%J.log -e ${LOG_PATH}/plot_mean_spread_${VAR}_${DATE}_${DAY}__%J.err "python $EXE_PATH ${PLOT_CONFIG_FILE} ${DATE} ${DAY}" &)
	    echo $JOBID
	    
    done
    
done

# iterate over the variables for postage charts
for VAR in ${VARIABLES[*]}; do
    
    # debug print
    echo "$APPNAME === Variable $VAR"
    
    # executable
    EXE_PATH=$SCRIPT_PATH/postage_${VAR}.py
    echo -n "Invoking $SCRIPT_PATH/postage_${VAR}.py ${PLOT_CONFIG_FILE} ${DATE} ${DAY}..."
	    
    JOBID=$(bsub -q s_medium -P 0510 -J "plot_postage_${VAR}_${DAY}" -o ${LOG_PATH}/plot_postage_${VAR}_${DATE}_${DAY}__%J.log -e ${LOG_PATH}/plot_postage_${VAR}_${DATE}_${DAY}__%J.err "python $EXE_PATH ${PLOT_CONFIG_FILE} ${DATE} ${DAY}" &)
    echo $JOBID
    
done	   
