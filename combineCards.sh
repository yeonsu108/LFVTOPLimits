year_2016=$1
year_2017=$2
year_2018=$3

cd fullComb/Hct/
combineCards.py year_2016=../../$year_2016/Hct/FCNC_Hct_Discriminant_DNN_Hct_all.dat \
                year_2017=../../$year_2017/Hct/FCNC_Hct_Discriminant_DNN_Hct_all.dat \
                year_2018=../../$year_2018/Hct/FCNC_Hct_Discriminant_DNN_Hct_all.dat > comb_Hct_all.txt
combineCards.py year_2017=../../$year_2017/Hct/FCNC_Hct_Discriminant_DNN_Hct_all.dat \
                year_2018=../../$year_2018/Hct/FCNC_Hct_Discriminant_DNN_Hct_all.dat > comb_Hct_1718.txt
combineCards.py year_2016=../../$year_2016/Hct/FCNC_Hct_Discriminant_DNN_Hct_all.dat \
                year_2017=../../$year_2017/Hct/FCNC_Hct_Discriminant_DNN_Hct_all.dat > comb_Hct_1617.txt
cd ../../
cd fullComb/Hut/
combineCards.py year_2016=../../$year_2016/Hut/FCNC_Hut_Discriminant_DNN_Hut_all.dat \
                year_2017=../../$year_2017/Hut/FCNC_Hut_Discriminant_DNN_Hut_all.dat \
                year_2018=../../$year_2018/Hut/FCNC_Hut_Discriminant_DNN_Hut_all.dat > comb_Hut_all.txt
combineCards.py year_2017=../../$year_2017/Hut/FCNC_Hut_Discriminant_DNN_Hut_all.dat \
                year_2018=../../$year_2018/Hut/FCNC_Hut_Discriminant_DNN_Hut_all.dat > comb_Hut_1718.txt
combineCards.py year_2016=../../$year_2016/Hut/FCNC_Hut_Discriminant_DNN_Hut_all.dat \
                year_2017=../../$year_2017/Hut/FCNC_Hut_Discriminant_DNN_Hut_all.dat > comb_Hut_1617.txt
cd ../..
