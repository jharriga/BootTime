#!/usr/bin/python3
#--------------------------------------------------------------
# post processes sut_boottest.py JSON files
# Opens all '.json' files in the current directory (line 134)
# calculates variance statistics for systemd-analyze by 
# parsing 'sa_time' JSON object for startup section timings
#     kernel, initrd, userspace, total
# Also parses 'sa_blame' JSON object for systemd services
# Edit 'sblame_list' (line #148) to select which systemd
#  services are searched for
#-------------------------------------------------------------

import json
import statistics
import os
import fnmatch

###############################################################
# FUNCTIONS Begin
def extract_json_element(obj, path):
    '''
    Extracts an element from a nested dictionary or
    a list of nested dictionaries along a specified path.
    If the input is a dictionary, a list is returned.
    If the input is a list of dictionary, a list of lists is returned.
    obj - list or dict - input dictionary or list of dictionaries
    path - list - list of strings that form the path to the desired element
    '''
    def extract(obj, path, ind, arr):
        '''
            Extracts an element from a nested dictionary
            along a specified path and returns a list.
            obj - dict - input dictionary
            path - list - list of strings that form the JSON path
            ind - int - starting index
            arr - list - output list
        '''
        key = path[ind]
        if ind + 1 < len(path):
            if isinstance(obj, dict):
                if key in obj.keys():
                    extract(obj.get(key), path, ind + 1, arr)
                else:
                    arr.append(None)
            elif isinstance(obj, list):
                if not obj:
                    arr.append(None)
                else:
                    for item in obj:
                        extract(item, path, ind, arr)
            else:
                arr.append(None)
        if ind + 1 == len(path):
            if isinstance(obj, list):
                if not obj:
                    arr.append(None)
                else:
                    for item in obj:
                        arr.append(item.get(key, None))
            elif isinstance(obj, dict):
                arr.append(obj.get(key, None))
            else:
                arr.append(None)
        return arr
    if isinstance(obj, dict):
        return extract(obj, path, 0, [])
    elif isinstance(obj, list):
        outer_arr = []
        for item in obj:
            outer_arr.append(extract(item, path, 0, []))
        return outer_arr

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

'''
# original implementation, now unused
# does not work with nested json
def item_generator(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == lookup_key:
                yield v
            else:
                yield from item_generator(v, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from item_generator(item, lookup_key)
'''

def print_stats(data_dict, json_path, fname):
    # Initialize for calcs
    extract_list = []
    value_list = []

    extract_list = extract_json_element(data_dict, json_path)
    for value in extract_list:
        if type(value[0]) is float:
            value_list.append(value[0])
        else:
            pass

    # Check for empty list, if so skip it
    vl_length = len(value_list)
    if vl_length:
        # Print MEAN, STDDEV and %SD aka co-efficient of variation
        mean = statistics.mean(value_list)
        std_dev = statistics.stdev(value_list)
        if mean == 0.0:
            percent_sd = 0.0  # avoid divide-by-zero
        else:
            percent_sd = ((std_dev / mean) * 100)
        print("> % s  " %(json_path[-1]) +\
              "% s Samples  " %(vl_length) +\
              "MEAN: % s  " %(round(mean, 2)) +\
              "STD_DEV: % s  " %(round(std_dev, 2)) +\
              "PERCENT_SD: % s" %(round(percent_sd, 1)))
    else:
        print("> % s  " %(json_path[-1]) +\
              "% s Samples - SKIPPED" %(vl_length)) 

# FUNCTIONS End
###############################################################

# Iterate over the JSON files
##dir = 'JSONs'
dir = '.'

for filename in os.listdir(dir):
    if fnmatch.fnmatch(filename, '*.json'):
##    if fnmatch.fnmatch(filename, 'ride4ER3*.json'):
        f = os.path.join(dir, filename)
        if os.path.isfile(f):
            # now open it, load JSON and print the stats
            with open(f, 'r') as file:
                data = json.load(file)
                print("## " + f)
                print("systemd-analyze time:")
                satime_list = ["kernel", "initrd", "userspace", "total"]
                for key1 in satime_list:
                    print_stats(data,\
                      ["test_results", "satime", key1], filename)

                print("systemd-analyze blame:")
                sablame_list = ["NetworkManager-wait-online.service", \
                        "initrd-switch-root.service", \
                        "initrd-cleanup.service", \
                        "NetworkManager.service", \
                        "auditd.service", \
                        "systemd-tmpfiles-setup.service", \
                        "dbus-broker.service", \
                        "user@0.service", \
                        "chronyd.service", \
                        "systemd-logind.service", \
                        "systemd-udevd.service"]
                for key2 in sablame_list:
                    print_stats(data,\
                      ["test_results", "sablame", key2], filename)

                print("DMESG link-is-up:")
                print_stats(data,\
                  ["test_results", "reboot", "link_is_up"], filename)

                print()
