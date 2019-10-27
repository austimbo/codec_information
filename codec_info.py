#!/usr/bin/env python2

import requests
from requests.auth import HTTPBasicAuth
from requests import Timeout
from lxml import etree
import sys

userid="admin"
password="cisco"
headers={'content-type': 'text/xml'}
#Device_IP="192.168.0.42"
xml_get="/getxml?location="
#Codec_URL="http://"+Device_IP
network_xml_suffix="/status/network"
system_unit_suffix="/status/SystemUnit"
headers= {'content-type' : 'text/xml'}
codec_file="codecs.txt"
codec_info_file="codec_info.csv"

#Here are the commands that we need t send to the device
#xStatus Network 1 Ethernet MacAddress
#xStatus SystemUnit Hardware Module SerialNumber !


#Function to retreive at addrebut via HTTP GET
#make a basic get to retreive the codec information
#Retreive the network interface information
def get_from_codec(URL,userid, password):
    auth = HTTPBasicAuth(userid, password)
    try:
        response = requests.get(URL, timeout=(2, 5), verify=False, headers=headers, auth=auth)
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

# Main - Execute the main routing
if __name__ == "__main__":
  #Open an output file
 with open("codec_info.csv",'w+') as codec_info_f:
    #Write the Header row to the file. Thi is useful for Microspft Excel
    codec_info_f.write("IPv4_address, mac_address, serial_number, product_id\n")
    with open(codec_file) as codec_file_f:
        #for Codec_IP in codec_file_f:
        for Codec_csv in codec_file_f:
            #Split record from the CSV file into three fields
            Device_IP,userid,password=Codec_csv.split(",")
            Codec_URL = "http://" + Device_IP
            #Retreive the Network XML group
            response=get_from_codec(Codec_URL+xml_get+network_xml_suffix,userid, password)
            if response:
                #Retreive the MacAddress tag
                mac_address=extract_value_from_xml(response,"/Network/Ethernet/MacAddress")
                print('Mac address is: {}'.format(mac_address.text))
                #Retreive the IPV4 Network address
                IPv4_address=extract_value_from_xml(response,"/Network/IPv4/Address")
                print('IPv4 address is: {}'.format(IPv4_address.text))
            #Retreive the System unit XML group from the device
            response=get_from_codec(Codec_URL+xml_get+system_unit_suffix,userid, password)
            if response:
            #Retreive the serial number from the device
                serial_number=extract_value_from_xml(response,"/Hardware/Module/SerialNumber")
                print('Serial Number is: {}'.format(serial_number.text))
                product_id=extract_value_from_xml(response,"/ProductId")
                 #Retreive the product ID from the XL Object
                print('Product ID is: {}'.format(product_id.text))
                #Write the output to the CSV file
                codec_info_f.write("%s,%s,%s,%s\n" % (IPv4_address.text,mac_address.text,serial_number.text,product_id.text))
            else:
                #Write an Error message to the CSV file
                codec_info_f.write("%s, Error retreiving information,," % (Device_IP))



