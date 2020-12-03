datacard16=$1
datacard17=$2
datacard18=$3
datacardRun2=$4
outname=$5

mkdir $outname

declare -a FolderList=($datacard16 $datacard17 $datacard18 $datacardRun2)
for folder in "${FolderList[@]}"
do
  mkdir $outname/$folder
  mkdir $outname/$folder/Hut
  mkdir $outname/$folder/Hct

  cp $folder/Hut/*.dat $outname/$folder/Hut
  cp $folder/Hct/*.dat $outname/$folder/Hct
  cp $folder/Hut/*shapes.root $outname/$folder/Hut
  cp $folder/Hct/*shapes.root $outname/$folder/Hct
  #cp $folder/Hut/forCombine*.root $outname/$folder/Hut
  #cp $folder/Hct/forCombine*.root $outname/$folder/Hct
done

declare -a YearList=(1617 1618 1718)
for year in "${YearList[@]}"
do
  rm $outname/$datacardRun2/*/*_${year}_*
done

for i in $outname/$datacardRun2/*/*.dat
do
  sed -i 's/\/home\/minerva1993\/CMSSW_8_1_0\/src\/UserCode\/FCNCLimits/..\/../g' $i
done
