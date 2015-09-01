import argparse
import sys
from vnc_api.vnc_api import *
from vnc_api import vnc_api

def pair(s):
    try:
        a,b = s.split(',')
        return a,b
    except:
        raise argparse.ArgumentTypeError("Physical pairs must be in the form a1,b1 a2,b2 a3,b3 ...")

parser = argparse.ArgumentParser(description='Create service template and link PIs')
parser.add_argument('--st_name', help='service template name', required=True)
parser.add_argument('--physical_pairs', nargs='*', type=pair, help='Physical pairs must be in the form a1,b1 a2,b2 a3,b3 ...)', required=True)
args = parser.parse_args()



# GET vnc_lib
try:
    vnc_lib = vnc_api.VncApi(api_server_host="127.0.0.1",username="admin",password="zaqwsx",tenant_name="admin")
except:
    print("Unable to connect to vnc_lib")
    sys.exit(0)


#create service appliance set
try:
    sa_set = ServiceApplianceSet("SA_set_script")
    sa_set_created = vnc_lib.service_appliance_set_create(sa_set)
except RefsExistError:
    sa_set_created = vnc_lib.service_appliance_set_update(sa_set)
except:
    print ("Unable to create Service Appliance set")
    sys.exit(0)



for idx,pair in enumerate(args.physical_pairs):

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
        pr = PhysicalRouter("pr_script_"+str(idx))
        pr_created = vnc_lib.physical_router_create(pr)
    except RefsExistError:
        pr_created = vnc_lib.physical_router_update(pr)
    except:
        print ("Unable to create Physical Router")
        sys.exit(0)

    # create two PIs connected to PR
    try:
        pi_left = PhysicalInterface("pi_left_script_"+str(idx),pr)
        pi_left_created = vnc_lib.physical_interface_create(pi_left)
    except RefsExistError:
        pi_left_created = vnc_lib.physical_interface_update(pi_left)
    except:
        print ("Unable to create left PI")
        sys.exit(0)
    try:
        pi_right = PhysicalInterface("pi_right_script_"+str(idx),pr)
        pi_right_created = vnc_lib.physical_interface_create(pi_right)
    except RefsExistError:
        pi_right_created = vnc_lib.physical_interface_update(pi_right)
    except:
        print ("Unable to create right PI")
        sys.exit(0)


    # create service appliance within SA_SET and link it to the 2PI:
    try:
        service_appliance_interface_type_left = ServiceApplianceInterfaceType()
        service_appliance_interface_type_left.type = "left"
        service_appliance_interface_type_right = ServiceApplianceInterfaceType()
        service_appliance_interface_type_right.type = "right"
        sa = ServiceAppliance("sa_script_"+str(idx),sa_set)
        sa.add_physical_interface(pi_left,service_appliance_interface_type_left)
        sa.add_physical_interface(pi_right,service_appliance_interface_type_right)
        sa_created = vnc_lib.service_appliance_create(sa)
    except RefsExistError:
        sa_created = vnc_lib.service_appliance_update(sa)
    except:
        print ("Unable to create SA")
        sys.exit(0)



    #link pair PIs to SA/PR PIs
    import pdb; pdb.set_trace()
    sys.exit(0)
    pi_left.add_physical_interface(pi_pair_left)
    pi_right.add_physical_interface(pi_pair_right)
    try:
        vnc_lib.physical_interface_update(pi_left)
        vnc_lib.physical_interface_update(pi_right)
    except:
        print("Unable to link pair PIs to SA PIs")
        sys.exist(0)


#create service Template
try:
    st = ServiceTemplate(args.st_name)
    m = {"instance_data":"null", "availability_zone_enable": "false", "service_virtualization_type": "physical-device", "image_name": "analyzer", "service_mode": "transparent", "flavor": "m1.medium", "service_scaling": "false", "vrouter_instance_type": "docker", "ordered_interfaces": "true"}

    st.service_template_properties = m
    st_created= vnc_lib.service_template_create(st)
except RefsExistError:
    st_created = vnc_lib.service_template_update(st)
except:
    print ("Unable to create Service template")
    sys.exit(0)
