datacard_folder=$1
path_to_an=/afs/cern.ch/user/b/brfranco/work/public/FCNC/git_AN-18-303/notes/AN-18-303/trunk/
#limit plots
cp $1/Hut_limits.png $path_to_an/fig/limits/
cp $1/Hct_limits.png $path_to_an/fig/limits/
#limit tables
cp $1/Hut_limits_table.tex $path_to_an/tables/
cp $1/Hct_limits_table.tex $path_to_an/tables/
#postfit plots
cp $1/Hut/*postfi*/*.png $path_to_an/fig/limits/postfit/BDT/
cp $1/Hct/*postfi*/*.png $path_to_an/fig/limits/postfit/BDT/
#impacts
cp $1/Hut/*Hut*_all_impacts.pdf $path_to_an/fig/limits/impacts/
cp $1/Hct/*Hct*_all_impacts.pdf $path_to_an/fig/limits/impacts/
