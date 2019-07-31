year_2017=$1
year_2018=$2

combineCards.py  year_2017=$year_2017 year_2018=$year_2018 > comb_MVAHutComb_hut.txt
    b2j3=input_MVAHutComb_b2j3_hut.txt \
    b2j4=input_MVAHutComb_b2j4_hut.txt \
    b3j3=input_MVAHutComb_b3j3_hut.txt \
    b3j4=input_MVAHutComb_b3j4_hut.txt \
    > comb_MVAHutComb_hut.txt

