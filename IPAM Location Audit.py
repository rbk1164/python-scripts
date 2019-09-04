# Author: ROHIT KADAM

import subprocess as sp
audit_file = open("C:\\Users\\rokadam\\Desktop\\Book1.csv")
#read_file = audit_file.read()


def read_file_create_list():
    read_csv = audit_file.read().split("\n")

    for line in read_csv:
        subnet = line.split(",")[0]
        comments = line.split(",")[1]
        vlan = line.split(",")[2]
        location = line.split(",")[3]

        if not location:
            if '.' in subnet:
                subnet_filter = subnet.split('/')
                if int(subnet_filter[1]) >= 24:
                    get_gateway = str(int(subnet.split('.')[3].split('/').pop(0))+1)
                    new_subnet = subnet.split('.')
                    new_subnet[3] = get_gateway
                    gateway = '.'.join(new_subnet)
                    result = sp.getstatusoutput("nslookup " + str(gateway))
                    result1 = result[1].split()
                    if 'Non-existent' in result1:
                        pass
                    else:
                        location = result1[5][0:5]
                        print(gateway,'---',location)
                else:
                    pass




read_file_create_list()

