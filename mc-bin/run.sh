#!/bin/sh
# usage: run.sh bucketName fullPathToDataFolder
#
# bucketName, the name of the S3 bucket
# fullPathToDataFoler, for each jobsubmission, all related data and jobsubmission
#   file should be put in a new folder, never put two jobsubmission in one folder
#
# By default, each job submission includes a jobsubmit.json file, the jobsubmission json file.
# This filename is jobsubmit.json and should be submitted at the end until all other datafiles have been successfully
# submitted.


# Define Constants
TMPDIR=/home/ubuntu/tmp
#TMPDIR=/Users/jianwang/Downloads/tempdir
LOGDIR=$TMPDIR/log
OUTDIR=$TMPDIR/output

# Make File Structure For Data & Results
mkdir -p $TMPDIR
mkdir -p $LOGDIR
mkdir -p $OUTDIR

# Get Data & Config From Upload Bucket
aws s3 sync s3://$1/$2/ $TMPDIR

# >>> conda init >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$(CONDA_REPORT_ERRORS=false '/home/ubuntu/miniconda3/bin/conda' shell.bash hook 2> /dev/null)"
if [ $? -eq 0 ]; then
    \eval "$__conda_setup"
else
    if [ -f "/home/ubuntu/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/ubuntu/miniconda3/etc/profile.d/conda.sh"
        CONDA_CHANGEPS1=false conda activate base
    else
        \export PATH="/home/ubuntu/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda init <<<

# Start Subprocess To Continuously Sync Logdir
/home/ubuntu/bin/sync_dir.sh $LOGDIR s3://$1/$2/logs &

# Activate Conda-Env & Run Python Script
conda activate caiman
echo " -- Output From Python Script -- " > $LOGDIR/motionCorrectionLog.txt
#python /home/ubuntu/bin/compress.py $3 $INDIR $OUTDIR >> $LOGDIR/motionCorrectionLog.txt
python /home/ubuntu/bin/caiman_motion_correction.py $TMPDIR $OUTDIR >> $LOGDIR/motionCorrectionLog.txt

# Copy Logs & Results Back To S3 Subdirectory
aws s3 sync $OUTDIR s3://$1/$2/output/
aws s3 sync $LOGDIR s3://$1/$2/logs/

# Remove Temporary File Structure
rm -rf $TMPDIR

# Shutdown Instance
#shutdown -h now
