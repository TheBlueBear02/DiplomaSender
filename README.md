Created Vm instance in google
https://console.cloud.google.com/marketplace/product/google/compute.googleapis.com?project=gendiploma&returnUrl=%2Fcompute%2Finstances%3Fproject%3Dengaged-truth-445518-e7&inv=1&invt=AbpQ4g



Cheatsheet for activating site

project: GenDiploma
https://console.cloud.google.com/compute/instancesDetail/zones/us-west1-a/instances/instance-20241223-080652?inv=1&invt=AbpQ4g&project=gendiploma

## Activate site:

1. ssh it to get terminal
https://console.cloud.google.com/compute/instances?inv=1&invt=AbpRVw&project=gendiploma

3. activate virtual env
source projects/DiplomaSender/ds-env/bin/activate
4. run the app
cd /home/rony_gabbai/projects/DiplomaSender
python3 app.py 
5. open site
https://diplomasender.duckdns.org/

6. In Email body - use {{name}} for name subsituation 

known issues
CSV list exported from rav meser
required fields - first, last, email
I need to generate the csv using linux LibreOffice to use it
need to make python csv code more robust for hebrew..and csv format

google VM - need to make sure app.py is running
