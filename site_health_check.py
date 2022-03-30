#!/usr/bin/env python3

# 20201020 - Add a function to add a single prefix to a local prefixlist - Dan
import cloudgenix
import argparse
from cloudgenix import jd, jd_detailed
import cloudgenix_settings
import sys
import logging
import os
import datetime
import collections
import csv
from csv import DictReader
import time
from datetime import datetime, timedelta
jdout = cloudgenix.jdout


# Global Vars
TIME_BETWEEN_API_UPDATES = 60       # seconds
REFRESH_LOGIN_TOKEN_INTERVAL = 7    # hours
SDK_VERSION = cloudgenix.version
SCRIPT_NAME = 'CloudGenix: Example script: Health Check'
SCRIPT_VERSION = "v1"

# Set NON-SYSLOG logging to use function name
logger = logging.getLogger(__name__)


####################################################################
# Read cloudgenix_settings file for auth token or username/password
####################################################################

sys.path.append(os.getcwd())
try:
    from cloudgenix_settings import CLOUDGENIX_AUTH_TOKEN

except ImportError:
    # Get AUTH_TOKEN/X_AUTH_TOKEN from env variable, if it exists. X_AUTH_TOKEN takes priority.
    if "X_AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('X_AUTH_TOKEN')
    elif "AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
    else:
        # not set
        CLOUDGENIX_AUTH_TOKEN = None

try:
    from cloudgenix_settings import CLOUDGENIX_USER, CLOUDGENIX_PASSWORD

except ImportError:
    # will get caught below
    CLOUDGENIX_USER = None
    CLOUDGENIX_PASSWORD = None

def health_check(cgx):
    
    
    site_check_list = []
    elem_id2n = {}
    elem_n2id = {}
    for site in cgx.get.sites().cgx_content['items']:
        site_data = {}
        site_data["Name"] = site["name"]
        site_id = site['id']
        if site["admin_state"] == "active":
            if site["element_cluster_role"] == "SPOKE":
                site_data["Type"] = "Branch"
                print("Checking site " + site["name"])
                end = datetime.utcnow()
                start = end - timedelta(days=7)
            
                end_time = end.isoformat()[:-3]+'Z'
                start_time = start.isoformat()[:-3]+'Z'
        
                data = {"start_time":start_time,"end_time":end_time,"interval":"1hour","metrics":[{"name":"TCPConcurrentFlows","statistics":["max"],"unit":"count"},{"name":"UDPConcurrentFlows","statistics":["max"],"unit":"count"}],"view":{},"filter":{"site":[site_id]}}
                resp = cgx.post.monitor_metrics(data=data)
                if resp:
                    metrics = resp.cgx_content.get("metrics", None)
                    flow_avg = 0
                    flow_max = 0

                    
                    
                    tcp_data = []
                    udp_data = []
                    for item in metrics:
                        series = item.get("series", None)
                        name = series[0]['name']
                    
                        data = series[0]['data'][0]['datapoints']
                        num = len(data)
                        if name == "TCPConcurrentFlows":
                            for item in data:
                                tcp_data.append(item)
                        elif name == "UDPConcurrentFlows":
                            for item in data:
                                udp_data.append(item)
                    for item_1 in tcp_data:
                        for item_2 in udp_data:
                            value = 0
                            if item_1["time"] == item_2["time"]:
                                value = item_1["value"] + item_2["value"]
                                if value > flow_max:
                                    flow_max = value
                                flow_avg += value
                                
                    average = flow_avg / num
                    site_data["Concurrent_AVG"] = round(average)
                    site_data["Concurrent_MAX"] = round(flow_max)     
                else:
                    site_data["Concurrent_AVG"] = "N/A"
                    site_data["Concurrent_MAX"] = "N/A"
            else:
                site_data["Type"] = "DC"
                site_data["Concurrent_AVG"] = "N/A"
                site_data["Concurrent_MAX"] = "N/A"
            
            ion_num = 0
            site_data["ION1-Image"] = "N/A"
            site_data["ION1-Platform"] = "N/A"
            site_data["ION1-CPU-AVG"] = "N/A"
            site_data["ION1-CPU-MAX"] = "N/A"
            site_data["ION1-MEM-AVG"] = "N/A"
            site_data["ION1-MEM-MAX"] = "N/A"
            site_data["ION2-Image"] = "N/A"
            site_data["ION2-Platform"] = "N/A"
            site_data["ION2-CPU-AVG"] = "N/A"
            site_data["ION2-CPU-MAX"] = "N/A"
            site_data["ION2-MEM-AVG"] = "N/A"
            site_data["ION2-MEM-MAX"] = "N/A"
            for element in cgx.get.elements().cgx_content["items"]:
                 if element['site_id'] == site_id:
                     ion_num += 1
                     site_data["ION" + str(ion_num) +"-Image"] = element["software_version"]
                     site_data["ION" + str(ion_num) +"-Platform"] = element["model_name"]
                     element_id = element["id"]
                     data = {"start_time":start_time,"end_time":end_time,"interval":"1hour","metrics":[{"name":"CPUUsage","statistics":["max"],"unit":"percentage"}],"filter":{"site":[site_id],"element":[element_id]}}
                     resp = cgx.post.monitor_sys_metrics(data=data)
                     if resp:
                        metrics = resp.cgx_content.get("metrics", None)
                        for item in metrics:
                            series = item.get("series", None)
                            data = series[0]['data'][0]['datapoints']
                            len_list = len(data)
                            total = 0
                            cpu_max = 0
                            for item in data:
                                if item["value"]:
                                    if item["value"] > cpu_max:
                                        cpu_max = item["value"]
                                    total += item["value"]
                                else:
                                    total += 0
                            cpu_avg = total / len_list
                            site_data["ION"+ str(ion_num) + "-CPU-AVG"] = str(round(cpu_avg)) + "%"
                            site_data["ION"+ str(ion_num) + "-CPU-MAX"] = str(round(cpu_max)) + "%"
                        
                     data = {"start_time":start_time,"end_time":end_time,"interval":"1hour","metrics":[{"name":"MemoryUsage","statistics":["max"],"unit":"percentage"}],"filter":{"site":[site_id],"element":[element_id]}}
                     resp = cgx.post.monitor_sys_metrics(data=data)
                     if resp:
                        metrics = resp.cgx_content.get("metrics", None)
                        for item in metrics:
                            series = item.get("series", None)
                            data = series[0]['data'][0]['datapoints']
                            len_list = len(data)
                            total = 0
                            mem_max = 0
                            for item in data:
                                if item["value"]:
                                    if item["value"] > mem_max:
                                        mem_max = item["value"]
                                    total += item["value"]
                                else:
                                    total += 0
                            mem_avg = total / len_list
                            site_data["ION"+ str(ion_num) + "-MEM-AVG"] = str(round(mem_avg)) + "%"
                            site_data["ION"+ str(ion_num) + "-MEM-MAX"] = str(round(mem_max)) + "%"
            time.sleep(.5)        
            site_check_list.append(site_data)
        
        
            
    
    csv_columns = []
    if site_check_list:
        for key in site_check_list[0].keys():
            csv_columns.append(key)
    csv_file = "site_health_check.csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in site_check_list:
                writer.writerow(data)
            print("Saved site_health_check.csv file")
    except IOError:
        print("CSV Write Failed")
        
    return    

                                          
def go():
    ############################################################################
    # Begin Script, parse arguments.
    ############################################################################

    # Parse arguments
    parser = argparse.ArgumentParser(description="{0}.".format(SCRIPT_NAME))

    # Allow Controller modification and debug level sets.
    controller_group = parser.add_argument_group('API', 'These options change how this program connects to the API.')
    controller_group.add_argument("--controller", "-C",
                                  help="Controller URI, ex. "
                                       "Alpha: https://api-alpha.elcapitan.cloudgenix.com"
                                       "C-Prod: https://api.elcapitan.cloudgenix.com",
                                  default=None)
    controller_group.add_argument("--insecure", "-I", help="Disable SSL certificate and hostname verification",
                                  dest='verify', action='store_false', default=True)
    login_group = parser.add_argument_group('Login', 'These options allow skipping of interactive login')
    login_group.add_argument("--email", "-E", help="Use this email as User Name instead of prompting",
                             default=None)
    login_group.add_argument("--pass", "-PW", help="Use this Password instead of prompting",
                             default=None)
    debug_group = parser.add_argument_group('Debug', 'These options enable debugging output')
    debug_group.add_argument("--debug", "-D", help="Verbose Debug info, levels 0-2", type=int,
                             default=0)
    
    args = vars(parser.parse_args())
                             
    ############################################################################
    # Instantiate API
    ############################################################################
    cgx_session = cloudgenix.API(controller=args["controller"], ssl_verify=args["verify"])

    # set debug
    cgx_session.set_debug(args["debug"])

    ##
    # ##########################################################################
    # Draw Interactive login banner, run interactive login including args above.
    ############################################################################
    print("{0} v{1} ({2})\n".format(SCRIPT_NAME, SCRIPT_VERSION, cgx_session.controller))

    # login logic. Use cmdline if set, use AUTH_TOKEN next, finally user/pass from config file, then prompt.
    # figure out user
    if args["email"]:
        user_email = args["email"]
    elif CLOUDGENIX_USER:
        user_email = CLOUDGENIX_USER
    else:
        user_email = None

    # figure out password
    if args["pass"]:
        user_password = args["pass"]
    elif CLOUDGENIX_PASSWORD:
        user_password = CLOUDGENIX_PASSWORD
    else:
        user_password = None

    # check for token
    if CLOUDGENIX_AUTH_TOKEN and not args["email"] and not args["pass"]:
        cgx_session.interactive.use_token(CLOUDGENIX_AUTH_TOKEN)
        if cgx_session.tenant_id is None:
            print("AUTH_TOKEN login failure, please check token.")
            sys.exit()

    else:
        while cgx_session.tenant_id is None:
            cgx_session.interactive.login(user_email, user_password)
            # clear after one failed login, force relogin.
            if not cgx_session.tenant_id:
                user_email = None
                user_password = None

    ############################################################################
    # End Login handling, begin script..
    ############################################################################

    # get time now.
    curtime_str = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')

    # create file-system friendly tenant str.
    tenant_str = "".join(x for x in cgx_session.tenant_name if x.isalnum()).lower()
    cgx = cgx_session
    
    health_check(cgx)
    
    # end of script, run logout to clear session.
    cgx_session.get.logout()

if __name__ == "__main__":
    go()