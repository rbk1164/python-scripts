# Author: ROHIT KADAM

import json
import subprocess
#  Get-AdGroupMember -identity <VPN-user-groip-name> | select name    ***gets the members belonging to this group!
#  Get-ADPrincipalGroupMembership <username> | select name               **gets groups a user belongs to :)


def list_vendors_and_users(vendor):
    process=subprocess.Popen(["powershell","Get-AdGroupMember -identity {} | select SamAccountName".format(vendor)],stdout=subprocess.PIPE);
    result=process.communicate()
    x =  list(result)
    new = bytes.decode(x[0]).split("\r\n")
    vendor_users_list1 = []

    for item in new:
        if not item or 'Sam' in item or '-' in item:
            pass
        else:
            vendor_users_list1.append(item)


    vendor_users_list = [x.replace(' ', '') for x in vendor_users_list1]
    return vendor_users_list


def create_dictionary():
    for vendor in sg_vpn_vendors_list:
        user_list = list_vendors_and_users(vendor)
        for user in user_list:
            process=subprocess.Popen(["powershell","Get-ADPrincipalGroupMembership {} | select name".format(user)],stdout=subprocess.PIPE);
            result=process.communicate()
            x =  list(result)
            new = bytes.decode(x[0]).split("\r\n")
            for item in new:
                if 'VPN Users - RSA' in item:
                    print (vendor, user, "VPN Users - RSA")
				elif 'VPN Users - ADFS' in item:
				    print (vendor, user, "VPN Users - ADFS")
                else:
                    pass

#vendors_with_RSA_access = []
for vendor in sg_vpn_vendors_list:
    create_dictionary()



#vendors_with_RSA_access =  [vendor for vendor in vendors_with_RSA_access if vendor is not None]
#print (vendors_with_RSA_access)
