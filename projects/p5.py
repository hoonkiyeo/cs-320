# project: p5
# submitter: yeo9
# partner: none
# hours: 40

import csv
import sys
import netaddr
import time
import json
from zipfile import ZipFile
from io import TextIOWrapper
import re
import matplotlib.pyplot as plt
import geopandas
import pyproj
from shapely.geometry import box


#part1
def ip_to_int_ip(ip):
    return int(netaddr.IPAddress(ip))



def ZippedCSVReader(zip1):
    with ZipFile(zip1) as zf:
        with zf.open("rows.csv") as f:
            tio = TextIOWrapper(f)
            reader = csv.reader(tio)
            for row in reader:
                yield row
                
def ip_check(ips):
        file_name = "ip2location.csv"
        row_data = []
        ip_list = []
        index = 0

        with open(file_name, "rb") as f:
            csv_reader = csv.reader(TextIOWrapper(f)) #bytes to string
            header = next(csv_reader) #skip header
            for row in csv_reader:
                row_data.append(row)

        size = len(row_data)
        for ip in ips:
            start = time.time()
            int_ip = ip_to_int_ip(ip)
            if int_ip >= int(row_data[index][0]):
                for i in range(index, size):
                    if int(row_data[i][0]) <= int_ip and int(row_data[i][1]) >= int_ip:
                        end = time.time()
                        index = i
                        ms = (end-start) * 1e3
                        region = row_data[i][3]
                        info_dict = {
                            "ip" : ip,
                            "int_ip" : int_ip,
                            "region" : region,
                            "ms" : ms   
                        }
                        break
            else:
                for i in range(index, -1, -1):
                    if int(row_data[i][0]) <= int_ip and int(row_data[i][1]) >= int_ip:
                        end = time.time()
                        index = i
                        ms = (end-start) * 1e3
                        region = row_data[i][3]
                        info_dict = {
                            "ip" : ip,
                            "int_ip" : int_ip,
                            "region" : region,
                            "ms" : ms   
                        }
                        break

            ip_list.append(info_dict)

        return json.dumps(ip_list, sort_keys = 2, indent = 2)


def main():
    if len(sys.argv) < 2:
        print("usage: main.py <command> args...")
    elif sys.argv[1] == "ip_check":
        ips = sys.argv[2:]
        if len(ips) == 0:
            print("usage: main.py <command> args...")
        else:
            print(ip_check(ips))
        # TODO: call function(s) you write to do IP checking
    # TODO: other commands
    elif  sys.argv[1] == "region":
        def region(zip1, zip2):
            reader = ZippedCSVReader(zip1)
            header = next(reader) #list of headers
            header.append("region") #add region to the header

            ip_list = []
            row_list = []

            for row in reader:
                row[0] = re.sub(r"[a-zA-Z]", "0", row[0])
                ip_list.append(row[0])
                row[0] = ip_to_int_ip(row[0])
                row_list.append(row)

            row_list = sorted(row_list)
            ip_list = sorted(ip_list, key = ip_to_int_ip)

            check_ip = ip_check(ip_list)
            info_dic = json.loads(check_ip)

            for ip_dic, row in zip(info_dic, row_list):
                row.append(ip_dic['region'])

            #make rows.csv in server_log2.zip
            with ZipFile(zip2, "w") as zf:
                with zf.open("rows.csv", "w") as raw:
                    with TextIOWrapper(raw) as f:
                        writer = csv.writer(f, lineterminator = "\n")
                        writer.writerow(header)
                        for row in row_list:
                            writer.writerow(row)
        regions = sys.argv[2:]
        if len(regions) != 2:
            print("usage: main.py <command> args...")
        else:
            region(sys.argv[2], sys.argv[3])
    
    elif sys.argv[1] == "zipcode":
        def zipcode(zip_name):
            code_list = []
            with ZipFile(zip_name) as zf:
                for info in zf.infolist():
                    with zf.open(info.filename, "r") as f:
                        tio = TextIOWrapper(f)
                        txt = tio.read()
                        codes = re.findall(r"\b(CA|NY|WI|IL)\b(\s\d{5})([-]\d{4})?",txt)
                        for code in codes:
                            if not code in code_list:
                                code_list.append((code[1]+code[2]).strip())

            code_list = list(set(code_list))
            code_list = sorted(code_list)
            for i in code_list:
                print(i)
        
        zipcode(sys.argv[2])
        
    elif sys.argv[1] == "geo":

        def geo(epsg, svg):
            #create df
            world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
            world['count'] = 0
            world['colorname'] = ""

            reader = ZippedCSVReader("server_log2.zip")
            region_dic = {}

            for row in reader:
                region = row[-1]
                region_dic[region] = region_dic.get(region,0) + 1
            for i,j in region_dic.items():
                world.loc[world['name'] == i, 'count'] = j
            #define colors
            world.loc[world["count"] >= 1e3, "colorname"] = "red"
            world.loc[world["count"] < 1e3, "colorname"] = "orange"
            world.loc[world["count"] == 0, "colorname"] = "gray"

            #crs and window
            crs = pyproj.CRS.from_epsg(epsg)
            window = box(crs.area_of_use.west, crs.area_of_use.south, crs.area_of_use.east, crs.area_of_use.north)

            area = world.intersection(window)
            area = area[~area.is_empty]

            color_list = []
            for i in area.index:
                color_list.append(world.at[i,"colorname"])

            area2 = area.to_crs("EPSG:"+epsg)

            fig, ax = plt.subplots()
            area2.plot(ax=ax, color = color_list)
            plt.savefig(svg)
            plt.close()

        geo_args = sys.argv[2:]
        if len(geo_args) != 2:
            print("usage: main.py <command> args...")
        else:
            geo(sys.argv[2], sys.argv[3])
        
        
    else:
        print("unknown command: "+sys.argv[1])

if __name__ == '__main__':
     main()
