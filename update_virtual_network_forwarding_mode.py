import argparse
import sys
from vnc_api.vnc_api import *
from vnc_api import vnc_api


parser = argparse.ArgumentParser(description='update virtual network forwarding mode')
parser.add_argument('--virtual_network_uuid', help='Virtual network uuid', required=True)
parser.add_argument('--forwarding_mode_type', help='Forwarding mode type for virtual network',choices=['l2','l3','l2_l3'], required=True)
parser.add_argument('--admin_user', help='optional admin username', default="admin")
parser.add_argument('--admin_password', help='optional admin password', default = "zaqwsx")
parser.add_argument('--admin_tenant_name', help='optional tenant name', default="admin")
args = parser.parse_args()

# GET vnc_lib
try:
    vnc_lib = vnc_api.VncApi(api_server_host="127.0.0.1",username=args.admin_user, password=args.admin_password, tenant_name=args.admin_tenant_name)
except:
    print("Unable to connect to vnc_lib")
    sys.exit(0)


#Get the virtual network
try:
    vn = vnc_lib.virtual_network_read(id=args.virtual_network_uuid)
except:
    print ("Unable to find the virtual network with the uuid "+str(args.virtual_network_uuid))
    sys.exit(0)

#update forwarding mode type
try:
    vn_prop = vn.get_virtual_network_properties()
    if vn_prop == None:
        vn_prop = VirtualNetworkType()
    vn_prop.forwarding_mode = args.forwarding_mode_type
    vn.set_virtual_network_properties(vn_prop)
    vn_updated = vnc_lib.virtual_network_update(vn)
except Exception as e:
    print ("Error while updating virtual network")
    print (str(e))
    sys.exit(0)
