#!/usr/bin/env bash

for config in xq.json yh.json global.json
do
    cp easytrader/config/${config} .
done

for file in easytrader/webtrader.py easytrader/xqtrader.py easytrader/yhtrader.py easytrader/api.py easytrader/helpers.py easytrader/log.py
do
    sed -e 's/\/config\///g; s/from \. import/import/g; s/from \./from /g ' ${file} > `basename ${file}`
done

# delete api.py invalid lines
delete_line_flag='_follower gftrader httrader yjbtrader'
sed_cmd=''
for flag in ${delete_line_flag}
do
    sed_cmd="/${flag}/d;${sed_cmd}"
done

sed -i ${sed_cmd} api.py
mv api.py jq_easytrader.py

sed -i '/thirdlibrary/d' helpers.py
echo generate jq files success
