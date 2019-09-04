# Author: ROHIT KADAM

from netmiko import ConnectHandler
import multiprocessing.dummy
import multiprocessing
import time
import subprocess as sp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import getpass
from easygui import passwordbox


Benchmark_file = input("Please enter the imported benchmark file: ")

Benchmark_file = open(Benchmark_file,'r').read().split("\n")
Output_file = input("Please write the name and location of file where you want your output: ")
f = open(Output_file,"w")
f.write('Device Name,Configuration,Ping,SSH,NDP Table,Route Table,ARP Table,MAC Table,STP Table,BGP Advertised-route Table,Device Info,Interface Info,BGP VPNV4 Imported Routes,IPsec VPN Table,IPsec VPN Table[Real-time],NAT Table,NAT Table[Real-time],OSPF Neighbors,Interface Information Brief,BGP Neighbors,Zone Table,show route protocol bgp,Seconds spent,\n')

starttime = time.time()
def ssh(device, username, password):

    connection_info = {"device_type":"juniper_junos",
                       "username":username,
                       "password":password,
                       "ip":device}

    connect_to_device = ConnectHandler(**connection_info)
    #print(device,'---------',connect_to_device.find_prompt())
    connect_to_device.disconnect()

username = ''
password = ''

def ssh_query(device):

    try:
        ssh(device,username,password)
        print (device, "Can_ssh")
        return "Successfull SSH"
        
    except Exception as e:
        print(device,'----------------',str(e))
        return str(e)
        
        

############################################### Ping function ################################################
def ping(device):
    status,result = sp.getstatusoutput("ping -n 2 -w 2 " + str(device))
                #print (result)

    if "unreachable" in result:
        ping_output = 'Unreachable'
        pass
    elif status == 0:
        ping_output = 'Success'
    elif "request timed out" in result:
        ping_output = 'request timed out'
    else:
        ping_output = 'Hostname Cannot be resolved'

    return (ping_output)

############################### write to file with filtered content, only failed config and added extra column for ping status to device #####################################################
devices_for_tuning = []
def write_to_output_file(Benchmark_file):

    if '-fpi-' in Benchmark_file or '-spi-' in Benchmark_file or '-rpi-' in Benchmark_file:
        if 'Failed' in Benchmark_file.split(',')[1]:
            devices_for_tuning.append(Benchmark_file.split(',')[0])
            device = Benchmark_file.split(',')[0]
            ping_output = ping(device)

            Benchmark_file = Benchmark_file.split(',')
            Benchmark_file[2] = str(ping_output)
            
            ssh_output = ssh_query(device)
            if ssh_output == "Successfull SSH":
                Benchmark_file[3] = "Successfull SSH"
            
            elif "Authentication" in ssh_output:
                Benchmark_file[3] = "Authentication error"
            
            elif "Socket" in ssh_output:
                Benchmark_file[3] = "Socket closed error"
                
            elif "timed-out" in ssh_output:
                Benchmark_file[3] = "Connection timed-out error"
                
            elif "prompt" in ssh_output:
                Benchmark_file[3] = "Cannot find prompt"
                
            else:
                Benchmark_file[3] = "Other issue"
                
            Benchmark_file = ','.join(Benchmark_file)
            f.write("{},\n".format(Benchmark_file))
            #f.write('\n')
        elif 'Hostname Changed' in Benchmark_file.split(',')[1]:
            #Note: need to add ping function in here :)
            f.write("{},\n".format(Benchmark_file))
        else:
            pass
    else:
        pass



def ping_range():

    num_threads = 100 * multiprocessing.cpu_count()
    p = multiprocessing.dummy.Pool(num_threads)
    p.map(write_to_output_file,Benchmark_file)
    #p.map(ssh_query, devices)

if __name__ == "__main__":

    ping_range()
    print('That took {} seconds'.format(time.time() - starttime))

def send_file_through_mail():

    email_user = 'your-email-id'
    email_password = passwordbox("email password: ")
    email_send = 'receivers-mail-id'

    subject = 'Benchmark_daily_task'

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject
    msg['Bcc'] = email_user

    body = 'Hi! \nI have attached the file with failed devices for benchmark task. These devices are under investigation. \n\nThank you, \n\nSincerely,\nRohit Kadam'
    msg.attach(MIMEText(body,'plain'))

    filename=Output_file
    attachment = open(filename,'rb')

    part = MIMEBase('application','octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= "+filename)

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp-server',25)
    server.starttls()
    server.login(email_user,email_password)


    server.sendmail(email_user,email_send,text)
    server.quit()

#send_file_through_mail()


