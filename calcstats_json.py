#!/usr/bin/env python3
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
import csv
import argparse
import glob

###############################################################
# FUNCTIONS Begin
def parse_args():
    parser = argparse.ArgumentParser(\
            description='calculates variance statistics for systemd-analyze by \
                    parsing \'sa_time\' JSON object for startup section timings \
                    kernel, initrd, userspace, total \
                    Also parses \'sa_blame\' JSON object for systemd services')

    parser.add_argument(
            'json_file',
            nargs='+',
            help='files to calculate statistics' )

    parser.add_argument(
            '-o',
            '--output-file',
            choices=['csv', 'json'],
            help='output results in stdout, csv, json',
            required=False,
            )
    return parser.parse_args()

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

def calc_stats(data_dict, json_path,  precision = 2):
    # Initialize for calcs
    extract_list = []
    value_list = []

    extract_list = extract_json_element(data_dict, json_path)
    for value in extract_list:
        if type(value[0]) is float:
            value_list.append(value[0])
        else:
            pass

    stat_keys = [ 'name', 'samples', 'mean', 'std_dev', 'percent_sd' ]
    stat = dict.fromkeys(stat_keys)
    stat['name']= json_path[-1]
    # Check for a list with less than 2 values, if so skip it
    vl_length = len(value_list)
    stat['samples'] = vl_length
    if vl_length > 1:
        # Print MEAN, STDDEV and %SD aka co-efficient of variation
        mean = statistics.mean(value_list)
        std_dev = statistics.stdev(value_list)
        if mean == 0.0:
            percent_sd = 0.0  # avoid divide-by-zero
        else:
            percent_sd = ((std_dev / mean) * 100)

        stat.update({
            'mean': round(mean, precision),
            'std_dev': round(std_dev, precision),
            'percent_sd': round(percent_sd, precision)
            })

    return stat

def print_statistics(stats):
    for stat in stats:
        print("> % s  " %(stat['name']) +\
              "% s Samples  " %(stat['samples']) +\
              "MEAN: % s  " %(stat['mean']) +\
              "STD_DEV: % s  " %(stat['std_dev']) +\
              "PERCENT_SD: % s" %(stat['percent_sd']))

#def write_statistics(stats):


# Function to get the list of keys across multiple runs
def get_keys_list(data, path):
    keys_list = []

    # Extract values based on the specified key list
    for item in data:
        current_data = item
        for key in path:
            current_data = current_data.get(key, {})
        if not current_data:
            return None
        keys_list.extend(current_data.keys())

    unique_keys = list(dict.fromkeys(keys_list))
    return unique_keys

def calc_section_stats(section, data, precision = 2, sort_key=None, sort_reverse=None):
    stats = []
    result_list = get_keys_list(data, ["test_results", section])

    if not result_list:
        return None

    for key in result_list:
        path = ["test_results", section, key]

        if(sort_key):
            data = sorted(data, key=sort_key, reverse=sort_reverse)

        stats.append(
                calc_stats(data, path, precision)
                )
    return stats

# FUNCTIONS End
###############################################################



# Main function
def main():
    # Iterate over the JSON files
    ##dir = 'JSONs'
    # Parse command line args, environment, etc.
    dir = '.'

    args = parse_args()

    for filename in args.json_file:
        if fnmatch.fnmatch(filename, '*.json'):
            f = os.path.join(dir, filename)
            if os.path.isfile(f):
                # now open it, load JSON and print the stats
                with open(f, 'r') as file:
                    data = json.load(file)
                    all_stats = {}

                    print("## " + f)



                    stat_settings = {
                            'initramfs': { "precision": 4 },
                            'dklm': { "precision": 4 },
                            'earlyservice': { "precision": 4 },
                            'clktick': { "precision": 4 },
                            'sablame_stats': {
                                "sort_key": lambda x: (x['samples'], x['mean']),
                                "sort_reverse": True 
                                },
                            }

                    stats_list = get_keys_list(data, ['test_results'])
                    for stat in stats_list:

                        # Grab any special settings if they exist
                        setting = stat_settings.get(stat, {})
                        precision = setting.get("precision", 2)
                        key = setting.get("sort_key", None)
                        reverse = setting.get("sort_reverse", None)

                        all_stats[stat] = calc_section_stats(stat, data, precision, key, reverse)


                    # Print stats and output to a file if needed
                    filename_without_ext = os.path.splitext(filename)[0]
                    for key, stat in all_stats.items():
                        print(key + ":")
                        if not stat:
                            print("> N/A")
                            continue

                        print_statistics(stat)
                        if args.output_file == 'csv':
                            with open("stats_" + filename_without_ext + '_' + key + ".csv", 'w') as f:
                                headers = stat[0].keys()
                                writer = csv.DictWriter(f, headers)
                                writer.writeheader()
                                writer.writerows(stat)

                    if args.output_file == 'json':
                        with open("stats_" + filename, 'w') as f:
                            f.write(json.dumps(all_stats))

if __name__ == '__main__':
    main()
