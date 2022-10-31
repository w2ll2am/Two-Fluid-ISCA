#!/bin/bash
#SBATCH --export=ALL # export all environment variables to the batch job
#SBATCH -D . # set working directory to .
#SBATCH -p $03 # submit to the parallel queue
#SBATCH --time=$01:00:00 # maximum walltime for the job
#SBATCH -A $04 # research project to submit under
#SBATCH --nodes=1 # specify number of nodes
#SBATCH --ntasks-per-node=$00 # specify number of processors per node
#SBATCH --mem=$05GB # specify bytes memory to reserve
#SBATCH --mail-type=END # send email at job completion
#SBATCH --mail-user=$02 # email address
#Commands you wish to run must go here, after the SLURM directives

start=`date +%s.%N`

module load DEDALUS/2.2006-foss-2020a 
module load FFmpeg/4.2.2-GCCcore-9.3.0 

printf "Simulation begin"
time mpirun -np $00 python3 "Hight_Normalisation_(KHH).py"
printf "Merge begin"
time python3 merge.py snapshots
printf "Plot begin"
time python3 $06
printf "Render begin"
time ffmpeg -framerate $07 -i plots/plot%04d.png -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p Animation.mp4
printf "End final timing"

end=`date +%s.%N`
runtime=$( echo "$end - $start" | bc -l )
