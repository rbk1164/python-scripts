# Author: ROHIT KADAM

import requests
import json
import subprocess
import datetime
from requests.utils import quote
trt_json_dumps =  open(input("Please enter the path of TRT json dumps: "))
vpn_roles = json.load(trt_json_dumps)

d = datetime.datetime.today()
output_file_TRT_open_sites_info = "open-sites-in-trt-{}.csv".format(d.strftime('%m-%d-%Y'))
output_file_sites_present_in_NB_or_not = "Sites-present-or-not-in-NB-{}.csv".format(d.strftime('%m-%d-%Y'))
#output_file_sites_duplicates = "Site-duplicates-{}.csv".format(d.strftime('%m-%d-%Y'))


###################### Since there were multiple site functions present in list format trt dumps, function was created to extract all the site functions and were passed to write operation underneath ###########
def site_function(item):
    functions_list = []
    for items in item["functions"]:
        if not items:
            return False
        else:
            functions_list.append(items["name"])
    functions_str = ','.join(functions_list).replace(",","-")
    return functions_str

################# Open a file for writing the info regarding all the open sites from trt dumps ############################################
with open(output_file_TRT_open_sites_info, 'w',encoding="utf-8") as f:
    sites_code_list_from_TRT_dumps = []
    site_path_list = []
    f.write("Site Code,Site Function,Site Status,City,State,Country,Criticality,Subnet,Location,Open date,\n")
    for item in vpn_roles["data"]:
        #if 'Open' in item["status"]["name"] and not (item["site_code"] is None):
        site_functions = site_function(item)
        f.write ("{},{},{},{},{},{},{},{},{},{},\n".format(item["site_code"],site_functions,item["status"]["name"],item["address"]["city"],item["address"]["state_province"],item["address"]["country"],item["store_criticality"]["name"],item["subnet"],item["system_name"],item["opening_date"]))
        sites_code_list_from_TRT_dumps.append(str(item["site_code"]).upper())
        if len(str(item["site_code"]).upper()) != 5:
            pass
        elif 'Warehouse' in site_functions:
            pass
        else:
            site_path_list.append("My Network/{0}/{1}/{2}".format(str(item["system_name"]).split('-')[0].strip(),str(item["system_name"]).split('-')[1].strip(),str(item["site_code"]).upper()))

    #print(sites_code_list_from_TRT_dumps)
    #print (site_path_list)
    site_path_list = list(set(site_path_list))
    #print (site_path_list)





####################################### Get token for the session #######################################################
def get_token():
    url = "https://netbrain-server"

    headers = {"Content-Type": "application/json"}

    payload = {"username":"", "password":"", "authentication_id": "AD"}

    get_token  = requests.post(url, json=payload, headers=headers)

    token = (get_token.json()['token'])
    #print (token)

    return token



def site_path_function(pass_this_to_site_path_function):
    for site_path in site_path_list:
        if pass_this_to_site_path_function in site_path.split('/')[3]:
            return site_path

################################## New Discovery####################################################################

def check_device_in_NB(token):
    with open(output_file_sites_present_in_NB_or_not,"w",encoding="utf-8") as f1:

        f1.write("Site-path,Present_in_NB,Site-Code,Site-function,Site-Status,City,State,\n")
        list_for_removing_duplicates = []
        duplicate_sites = []
        for item in vpn_roles["data"]:
            site_functions = site_function(item)
            pass_this_to_site_path_function = str(item["site_code"]).upper()
            list_for_removing_duplicates.append(item["site_code"])

            if 'Warehouse' in site_functions:
                pass
            elif len(str(item["site_code"])) < 4:
                pass
            elif True:
                count=0

                for i in range(len(list_for_removing_duplicates)):
                    if item["site_code"] == list_for_removing_duplicates[i]:
                        count+=1
                if count >= 2 and item["status"]["name"] is not 'Open':
                    duplicate_sites.append(item["site_code"])
                    pass
                elif str(item["site_code"]).upper() in ','.join(site_path_list):
                    #print (item)
                    #print(item["site_code"],"\n")
                    #print(','.join(site_path_list))
                    site_path = site_path_function(pass_this_to_site_path_function)
                #else:
                    url = "https://netbrain-server-site={}".format(quote("{}".format(site_path),safe=''))

                    headers = {"Token":token, "Content-Type": "application/json"}

                    get_devices_from_NB = requests.get(url, headers=headers)

                    #print(get_devices_from_NB.json())

                    if "siteInfo" not in get_devices_from_NB.json():
                        f1.write("{0},False,{1},{2},{3},{4},{5},\n".format(site_path, item["site_code"], site_functions, item["status"]["name"], item["address"]["city"],item["address"]["state_province"]))

                    elif get_devices_from_NB.json()["siteInfo"]["sitePath"] == site_path:
                        f1.write("{0},True,{1},{2},{3},{4},{5},\n".format(site_path, item["site_code"], site_functions, item["status"]["name"], item["address"]["city"],item["address"]["state_province"]))
            else:
                pass
    print(duplicate_sites)

####################################### Removing duplicate entries from the csv ####################################



##################################### Go into right tenant/domain ##################################################

def get_tenant_domain():
    url = "https://netbrain-server"
    token = get_token()
    headers = {"Token":token, "Content-Type": "application/json"}

    payload = {"tenantId":"", "domainId":""}

    get_tenant_domain = requests.put(url, data=json.dumps(payload), headers=headers)

    check_device_in_NB(token)


get_tenant_domain()






