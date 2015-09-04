import argparse
import sys
import traceback
from vnc_api.vnc_api import *
from vnc_api import vnc_api

def pair(s):
    try:
        a,b = s.split(',')
        return a,b
    except:
        raise argparse.ArgumentTypeError("Physical pairs must be in the form a1,b1 a2,b2 a3,b3 ...")

parser = argparse.ArgumentParser(description='Create service template and link PIs')
parser.add_argument('--service_template_name', help='service template name', required=True)
parser.add_argument('--physical_interface_pairs', nargs='*', type=pair, help='Physical pairs must be in the form a1,b1 a2,b2 a3,b3 ...)', required=True)
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


#create service appliance set
try:
    sa_set = ServiceApplianceSet("SA_set_script_"+str(args.service_template_name))
    sa_set_created = vnc_lib.service_appliance_set_create(sa_set)
except RefsExistError:
    sa_set_created = vnc_lib.service_appliance_set_update(sa_set)
except:
    print ("Unable to create Service Appliance set")
    sys.exit(0)



for idx,pair in enumerate(args.physical_interface_pairs):

    # read first PI from pair
    try:
        pi_pair_left= vnc_lib.physical_interface_read(id=pair[0])
    except:
        print ("Unable to read Physical Interface with uuid="+str(pair[0]))
        sys.exit(0)
    
    # read second PI from pair
    try:
        pi_pair_right= vnc_lib.physical_interface_read(id=pair[1])
    except:
        print ("Unable to read Physical Interface with uuid="+str(pair[1]))
        sys.exit(0)
    
    
    #create PR
    try:
        pr = PhysicalRouter("pr_script_"+str(args.service_template_name)+"_"+str(idx))
        pr_created = vnc_lib.physical_router_create(pr)
    except RefsExistError:
        pr_created = vnc_lib.physical_router_update(pr)
    except Exception as e:
        print ("Unable to create Physical Router")
        traceback.print_exc(e)
        sys.exit(0)
    
    # create two PIs connected to PR
    try:
        pi_1 = PhysicalInterface("pi_1_"+str(args.service_template_name)+"_script_"+str(idx),pr)
        pi_1_created = vnc_lib.physical_interface_create(pi_1)
    except RefsExistError:
        pi_1_created = vnc_lib.physical_interface_update(pi_1)
    except Exception as e:
        traceback.print_exc(e)
        print ("Unable to create PI 1")
        sys.exit(0)
    try:
        pi_2 = PhysicalInterface("pi_2_"+str(args.service_template_name)+"_script_"+str(idx),pr)
        pi_2_created = vnc_lib.physical_interface_create(pi_2)
    except RefsExistError:
        pi_2_created = vnc_lib.physical_interface_update(pi_2)
    except Exception as e:
        traceback.print_exc(e)
        print ("Unable to create PI 2")
        sys.exit(0)
    
    
    # create service appliance within SA_SET and link it to the 2PI:
    try:
        sa = ServiceAppliance("sa_script_"+str(args.service_template_name)+"_"+str(idx),sa_set)
        sa.add_physical_interface(pi_1)
        sa.add_physical_interface(pi_2)
        sa_created = vnc_lib.service_appliance_create(sa)
    except RefsExistError:
        sa_created = vnc_lib.service_appliance_update(sa)
    except Exception as e:
        traceback.print_exc(e)
        print ("Unable to create SA")
        sys.exit(0)
    
    
        
    #link pair PIs to SA/PR PIs
    #import pdb; pdb.set_trace()
    #sys.exit(0)
    pi_1.add_physical_interface(pi_pair_left)
    pi_2.add_physical_interface(pi_pair_right)
    try:
        vnc_lib.physical_interface_update(pi_1)
        vnc_lib.physical_interface_update(pi_2)
    except Exception as e:
        traceback.print_exc(e)
        print("Unable to link pair PIs to SA PIs")
        sys.exist(0)


#create service Template
try:
    st = ServiceTemplate(args.service_template_name)
    st_prop = ServiceTemplateType()
    st_prop.service_virtualization_type = "physical-device"
    st_prop.service_mode = "transparent"
    st_prop.service_type = "firewall"
    st_prop.image_name = "analyzer"
    #m = {"instance_data":"null", "availability_zone_enable": "false", "service_virtualization_type": "physical-device", "image_name": "analyzer", "service_mode": "transparent", "flavor": "m1.medium", "service_scaling": "false", "vrouter_instance_type": "docker", "ordered_interfaces": "true"}
    
    st.set_service_template_properties(st_prop)
    st_created= vnc_lib.service_template_create(st)
except RefsExistError:
    st_created = vnc_lib.service_template_update(st)
except Exception as e:
    traceback.print_exc(e)
    print ("Unable to create Service template")
    sys.exit(0)