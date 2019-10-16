#!/bin/sh
# usage: run.sh bucket path filename

# Define Constants
TMPDIR=/home/ubuntu/tmp
INDIR=$TMPDIR/input 
LOGDIR=$TMPDIR/log
OUTDIR=$TMPDIR/output

# Make File Structure For Data & Results
mkdir -p $INDIR
mkdir -p $LOGDIR
mkdir -p $OUTDIR

# Get Data & Config From Upload Bucket
aws s3 sync s3://$1/$2/inputs $INDIR

# Configure Anaconda For SSM (added by Miniconda3 4.5.12 installer)
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

# Start Subprocess To Continuously Sync Logdir
/home/ubuntu/bin/sync_dir.sh $LOGDIR s3://$1/$2/logs &

# Activate Conda-Env & Run Python Script
conda activate trefide
echo " -- Output From Python Script -- " > $LOGDIR/pmd_out.txt	
python /home/ubuntu/bin/compress.py $3 $INDIR $OUTDIR >> $LOGDIR/pmd_out.txt

# Copy Logs & Results Back To S3 Subdirectory
aws s3 sync $OUTDIR s3://$1/$2/results/
aws s3 sync $LOGDIR s3://$1/$2/logs/

# Remove Temporary File Structure
rm -rf $TMPDIR

# Shutdown Instance
shutdown -h now
