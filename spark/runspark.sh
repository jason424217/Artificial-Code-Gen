#!/bin/bash
#PBS -N test
#PBS -l nodes=1:hima:ppn=1
#PBS -l walltime=00:10:00
#PBS -j oe

# go to active directory
cd $PBS_O_WORKDIR

# gather some node info
nodes=($( cat $PBS_NODEFILE | uniq ))
nnodes=${#nodes[@]}
last=$(( $nnodes - 1 ))

# Start the SPARK MASTER
start-master.sh 
sparkmaster="spark://${nodes[0]}:7077"

# Loop over workers and start
for i in `seq 0 $last`
do
    ssh ${nodes[$i]} start-slave.sh -m 4G -d /local/scr/nacooper01/TMPDIR -c $PBS_NUM_PPN ${sparkmaster}
done

#Run python script
time python ./sparkex.py LONG

# Loop over workers and kill
for i in `seq 0 $last`
do
	ssh ${nodes[$i]} stop-all.sh
done



