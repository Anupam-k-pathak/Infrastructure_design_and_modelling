import gzip
import re
import os
import argparse
import csv
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--test', dest='test_name', 
                     default='all_test_rerun',
                    help='test cases folder')
parser.add_argument('--uc', dest='usecase_list', 
                     default='./usecase_list.txt',
                    help='usecase list')
parser.add_argument('--degree',type=int, dest='reg_degree', 
                     default=3,
                    help='usecase list')
parser.add_argument('--model',type=str, dest='reg_model', 
                     default="linear",
                    help='usecase list')

parser.add_argument('--action', dest='action', 
                     default='extract_BW',
                    help="options\n extarct_BW-> extracts dynamic BW\n convert_fsdb \n extract_buffer_signal-> extarct buffer fill level signal from fsdb\n max_buffer_analysis-> max buffer fill level to csv\n")
args = parser.parse_args()

test_name=args.test_name
transaction_level_output_path="../"+test_name+"/platform2_CameraUC.Transient/"

########################################################################################################################################################
def extract_BW(log):
    #print("extracting Dynamic BW")
    result=[]
    table=[]
    for i in range(len(log)):
        line=log[i].decode()
        if line=="printing bandwidth information table\n":
            table=log[i+2:i+32]
            break 
    for row in table:
        row=row.decode()
        data=re.findall("(\d+\.\d+)", row)
        BW_name=(row.split(" "))[0]
        
        if BW_name.endswith("_BW"):

            if len(data)<4:     # taking care if entry is nan
                result.append('0')
            else:
                result.append(data[3])
        if BW_name.startswith("DDR_Utilization"):
            result.append(data[-1])
    return result
def extract_source_BW(logs):
    num01 = 0
    num23 = 0
    start = 0
    for i in range(len(logs)):
        log=logs[i].decode()

        if "Statistics: ana_image_engine_front0_hyp_config0_msf_chroma" in log:
            start = 1
        if "image_engine_front0_video_chroma: Distibution Setting" in log:
            start = 0
            break
        if ("BytesWrite" in log) and (start == 1):
            if ("image_engine_front0" in log) or ("image_engine_front1" in log):
                log = log.split('=')
                hyp_config = log[0]
                log = log[1].split('//')
                a = log[0].rsplit()
                num01 = num01 + int(a[0])
            if ("image_engine_front2" in log) or ("image_engine_front3" in log):
                log = log.split('=')
                hyp_config = log[0]
                log = log[1].split('//')
                a = log[0].rsplit()
                num23 = num23 + int(a[0])
    return [str(num01),str(num23)]

def write_csv(filename,output,header=""):
    outfile = open(filename, 'w+')
    outfile.write(header)

    for out in output:
        outfile.write(",".join(out)+"\n")
    
    print("writing "+filename)
    outfile.close()

def read_csv(filename):
    
    data=[]
    with open(filename ,"r") as f:
        reader=csv.reader(f)
        
        for row in reader:
            data.append(row)
    data=np.array(data)
    print("reading "+filename)
    return data

def write_txt_file(filename,data):
    outfile = open(filename, 'w+')
    for out in data:
     outfile.write(out+"\n")
    
    print("writing "+filename)
    outfile.close()


def read_txt_file(filename):
    infile=open(filename,'r+')
    lines=infile.readlines()
    return lines

def extract_priority_lvl(log):
    print("extracting priority_lvl out")
    priority_lvl_output=[]
    table=[]
    for i in range(len(log)):
        line=log[i].decode()
        if line.startswith("priority_lvl_stats.Priority_lvl_Camera_NoC"):
            table=log[i:i+8]
            break

    for row in table:
        row=row.decode()
        data=re.findall("(\d+\.\d+)", row)
        priority_lvl_output.append(data[-1])
    return priority_lvl_output

def convert_vcd_to_fsdb(usecase_list):
    
    if not os.path.exists("./"+test_name+"_results/fsdb/"):
        os.makedirs("./"+test_name+"_results/fsdb/")
    for usecase in usecase_list:
        filename=transaction_level_output_path+usecase+"/Camera_NoC.vcd.gz"
        out_fsdb="./"+test_name+"_results/fsdb/"+usecase+"_Camera_NoC.vcd.gz.fsdb"
        command="Vcd2fsdb "+filename +" -o "+out_fsdb
        print("executing cammand "+command)
        os.system(command)

def extract_buffer_signal(buffer_name,usecase_list):
    if not os.path.exists("./"+test_name+"_results/output_csv/"):
        os.makedirs("./"+test_name+"_results/output_csv/")

    for usecase in usecase_list:
        fsdb_file="./"+test_name+"_results/fsdb/"+usecase+"_Camera_NoC.vcd.gz.fsdb"
        out_csv="./"+test_name+"_results/output_csv/"+usecase+buffer_name+".csv"
        command='Fsdbreport '+fsdb_file+' -s "/\platform1.multimedia.camera_1_Camera_NoC'+buffer_name+':Specification:camera_NoC_image_engine_front'+buffer_name+'::writeBuffer:level " -csv' + ' -o '+out_csv
        command = 'Fsdbreport ' + fsdb_file + """-s "/\platform2.camera_1_Camera_NoC_image_engine_front""" +buffer_name+""":camera_NoC.image_engine_front_NW_initiate_unit_0::writeBuffer:level " -csv""" + """ -o """ +out_csv
        print("executing cammand "+command)
        os.system(command)

def read_usecase_list():
    usecase_list=read_txt_file(args.usecase_list)
    modified_list=[]
    for usecase in usecase_list:
        usecase=usecase.rstrip()
        if not(usecase.startswith("#") or usecase.startswith("//")):
            modified_list.append(usecase)
    
    usecase_list=modified_list

    return usecase_list



def search(stri, h):
    search_result=[]
    if (re.findall(stri, str(h))):
        abc = stri
        d = h.split("writeBufferAllocation")
        search_result = re.findall('([\d\.\d]+[eE]?[-+]?\d+)', d[1])
        if (search_result==[]):
            search_result=['0','0','0','0','0','0','0']
        if(len(search_result)==6):
            search_result.append('0')
    return search_result

def extract_buffer(log):
    print("extracting bufffer stats")
    buff_data=[]
    for i in range(len(log)):
        m = log[i]
        search_result=search("image_engine_front.*writeBuffer", str(m))
        if len(search_result)!=0:
            buff_data.append(search_result)
    return buff_data[0]+buff_data[1]
############################################################################################################################

if args.action=="extract_BW":
    usecase_list=read_usecase_list()
    output=[]
    
    if not os.path.exists("./"+test_name+"_results/"):
        os.makedirs("./"+test_name+"_results/")
    for usecase in usecase_list:
    
        usecase=usecase.rstrip()
        print("usecase "+usecase)
        report_file=transaction_level_output_path+"/"+usecase+".out.gz"
    
        with gzip.open(report_file,'r') as f:
            log=f.readlines()

        buffer_file=transaction_level_output_path+"/"+usecase+"/image_engine_front_buffer_stats.txt"
        with open(buffer_file, 'r') as f:
            buffer_log = f.readlines()

        temp_output=extract_BW(log)
        temp_output+=extract_buffer(buffer_log)
        temp_output+=extract_source_BW(log)
        temp_output.insert(0,usecase)
 
        output.append(temp_output)

    header="Usecase,BW1,BW2, BW3,BW4, BW5,BW6, BW7,BW8, BW9,BW10, BW11,BW12, BW13,BW14, BW15,BW16, BW17,BW18, BW19,BW20, BW21,BW22, BW23,BW24, BW25,BW26, BW27,BW28, BW29,BW30, BW31,BW32, BW33,BW34, BW35, BW36, , , , , ,Source_Bytes_buff01,Source_Bytes_buff23 \n"

    write_csv("./"+test_name+"_results/BW.out.csv",output,header) 
elif(args.action=="convert_fsdb"):
    usecase_list=read_usecase_list()
    convert_vcd_to_fsdb(usecase_list)

elif(args.action=="extract_buffer"):
    print("extracting buffer signals")
    usecase_list=read_usecase_list()
    extract_buffer_signal("01",usecase_list)
    extract_buffer_signal("23",usecase_list)

elif args.action=="buffer_analysis":
    usecase_list=read_usecase_list()
    buffer_name=["01","23"]
    csv_dir_path="./"+test_name+"_results/output_csv/"
    output_file="./"+test_name+"_results/buffer_fill.csv" 
    output=[]
    for uc in usecase_list:
        temp_output=[uc]
        for buf in buffer_name:
            data=read_csv(csv_dir_path+uc+buf+".csv")
            data=data[1:,:]
            data=data.astype(float)
            max_level=np.max(data[:,1])
            max_time=np.argmax(data[:,1])
            temp_output.append(str(max_level)+","+str(max_time/len(data[:,1])))
        output.append(temp_output)
    
    write_csv(output_file,output,"usecase, max_buff_01,time,max_buff_23,time\n")

elif(args.action=="regression"):

    if args.reg_model=="linear":
        sub_model= linear_model.LinearRegression(fit_intercept=False)
    elif args.reg_model=="lasso":
        sub_model=linear_model.Lasso(alpha=0.01)
    model = Pipeline([('poly', PolynomialFeatures(degree=args.reg_degree)),
                  ('linear', sub_model)])
    BW_file="./"+test_name+"_results/BW.out.csv"
    buff_fill_file="./"+test_name+"_results/buffer_fill.csv"

    x_data=read_csv(BW_file)
    y_data=read_csv(buff_fill_file)

    x=x_data[1:,2]      # extract Video front engine BW
    y=y_data[1:,1]
    x=x.astype(float)
    y=y.astype(float)
    plt.scatter(x,y)
    
    model = model.fit(x[:, np.newaxis],y)
    coef=model.named_steps['linear'].coef_
    x=np.arange(np.min(x),np.max(x))
    y_reg=np.zeros(len(x))

    for i in range(1,len(coef)):
        y_reg+=coef[i]*x**i
    plt.plot(x,y_reg)
    plt.show()
    print(coef)
elif args.action=="create_usecaselist":
    dir_list = [directory for directory in os.listdir(transaction_level_output_path) if os.path.isdir(transaction_level_output_path+directory) and directory.startswith('Cam')]

    write_txt_file(args.usecase_list,dir_list)
else:
    print("invalid action")

