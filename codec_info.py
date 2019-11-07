#!/usr/bin/env python2

import requests
from requests.auth import HTTPBasicAuth
from requests import Timeout
from lxml import etree
from prettytable import PrettyTable
import sys

headers={'content-type': 'text/xml'}
xml_get="/getxml?location="
#Codec_URL="http://"+Device_IP
network_xml_suffix="/status/network"
system_unit_suffix="/status/SystemUnit"
user_interface_suffix="/status/UserInterface"
content_type= {'content-type' : 'text/xml'}
codec_file="codecs.txt"
codec_info_file="codec_info.csv"

#Set up Prettytable parameters to draw an ASCII-based table
MainSwTable = PrettyTable()

#Here are the commands that we need t send to the device
#xStatus Network 1 Ethernet MacAddress
#xStatus SystemUnit Hardware Module SerialNumber !


#Function to retreive at information via a via HTTP GET
#make a basic get to retreive the codec information
def get_from_codec(URL,userid, password):
    auth = HTTPBasicAuth(userid, password)
    try:
        response = requests.get(URL, timeout=(5, 5), verify=False, headers=headers, auth=auth)
        print('Status Code: {0} for {1}'.format(response.status_code,URL))
        return response

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("Error {0}".format(e))

    except:
        print("An Exception Occured {0}".format(sys.exc_info()[0]))

def extract_value_from_xml(xml_text,xml_path):
    # Change the response textr into an XML document/object
    response_xml_obj = etree.fromstring(xml_text.text)
    xml_text_value = response_xml_obj.find('./'+xml_path)
    return xml_text_value

def request_comms_error_report(message):
    codec_info_f.write("%s, Error retreiving information,%s," % (Device_IP,message))
    MainSwTable.add_row([format(Device_IP), format(message),format('Error'),format('Error'),format('Error')])


# Main - Execute the main routing
if __name__ == "__main__":
 print('Version2.0- Last Change Daniele, pretty print table')
  #Define Field names in the Pretty table MainSwTable
 MainSwTable.field_names = ['SYSTEM NAME', 'MAC ADDRESS', 'IP ADDRESS', 'SERIAL NUMBER', 'PRODUCT ID']
  # Open an output file
 with open("codec_info.csv",'w+') as codec_info_f:
    #Write the Header row to the file. Thi is useful for Microspft Excel
    codec_info_f.write("System Name, IPv4_address, mac_address, serial_number, product_id\n")
    with open(codec_file) as codec_file_f:
        for Codec_csv in codec_file_f:
            #Split record from the CSV file into three fields
            Device_IP,userid,password=Codec_csv.split(",")
            Codec_URL = "http://" + Device_IP
            #Retreive the Network XML group
            response=get_from_codec(Codec_URL+xml_get+network_xml_suffix,userid, password)
            if response:
                #Retreive the MacAddress tag
                mac_address=extract_value_from_xml(response,"/Network/Ethernet/MacAddress")
                #Retreive the IPV4 Network address
                IPv4_address=extract_value_from_xml(response,"/Network/IPv4/Address")
            else:
                request_comms_error_report('Network Stuff failed')
                continue
            #Retreive the System unit XML group from the device
            response=get_from_codec(Codec_URL+xml_get+system_unit_suffix,userid, password)
            if response:
            #Retreive the serial number from the device
                serial_number=extract_value_from_xml(response,"/Hardware/Module/SerialNumber")
            # Retreive the product ID from the XL Object
                product_id=extract_value_from_xml(response,"/ProductId")
            else:
                request_comms_error_report('Serial Number Stuff failed')
                continue
            #Retreive the system name from the device
            response = get_from_codec(Codec_URL + xml_get + user_interface_suffix, userid, password)
            if response:
                system_name=extract_value_from_xml(response,"/UserInterface/ContactInfo/Name")
                #Write the output to the CSV file
                codec_info_f.write("%s,%s,%s,%s,%s\n" % (system_name.text,IPv4_address.text,mac_address.text,serial_number.text,product_id.text))
                #Then write a record of all of the results to the PrettyTable
                MainSwTable.add_row([format(system_name.text), format(mac_address.text), format(IPv4_address.text),format(serial_number.text), format(product_id.text)])
                requests_comms_error = False
            else:
                request_comms_error_report('User Interface Stuff failed')
                continue
    #As one last thing, print the prettyprint table
    print(MainSwTable)


