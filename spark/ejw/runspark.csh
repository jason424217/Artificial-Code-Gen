#!/bin/tcsh
#PBS -N test
#PBS -l nodes=1:hima:ppn=2
#PBS -l walltime=00:10:00
#PBS -j oe

conda activate tf1.13.1

# go to active directory
cd $PBS_O_WORKDIR

set mem=4G
set master=`hostname -s`
echo $master
# Start the SPARK MASTER
start-master.sh 
set sparkmaster="spark://""$master"":7077"

# Loop over workers and start
foreach i (`cat $PBS_NODEFILE|uniq`)
    echo $i
    rsh $i start-slave.sh -m $mem -d /local/scr/nacooper01/TMPDIR -c $PBS_NUM_PPN ${sparkmaster}
end

#Run python script
date
echo $mem
echo nodenames `cat $PBS_NODEFILE|uniq`
echo nodes = `cat $PBS_NODEFILE|uniq|wc -l`
echo ppn = $PBS_NUM_PPN
time python ./sparkex.py LONG >& log.txt
date

# Loop over workers and kill
foreach i (`cat $PBS_NODEFILE|uniq`)
    echo $i
    rsh $i stop-all.sh
    rsh $i killall java
end





