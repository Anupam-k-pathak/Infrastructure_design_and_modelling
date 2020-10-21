import csv
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('-exp', type=str, dest='exp_name',
                     default='200us_platform2_default_config',
                    help='test cases folder')
parser.add_argument('-u', type=str, dest='usecase_list',
                     default='single_cam_16MP@120fps',
                    help='usecase list')
parser.add_argument('-s',type=str, dest='transaction_analysis_signals',
                     default = "platform2_camera_NoC0_transaction.csv,platform2_camera_NoC1_transaction.csv",
                    help='usecase list')
parser.add_argument('-f',type=int, dest='filter',
                     default = 1,
                    help='usecase list')

parser.add_argument('-x',type=int, dest='x_axis',
                     default = 1000,
                    help='usecase list')


args = parser.parse_args()
exp_name = args.exp_name
all_experiment_names = exp_name.split(",")
transaction_analysis_signals = args.transaction_analysis_signals
transaction_analysis_signals_all = transaction_analysis_signals.split(",")
filter = args.filter
usecase_list = args.usecase_list
all_usecaselist = usecase_list.split(",")
x_axis = args.x_axis

print("\nMaxtime_NW_initiate_unit3(us),NW_initiate_unit0_buff_fill,NW_initiate_unit1_buff_fill,NW_initiate_unit3_buff_fill")

transaction_level_output_path = "/prj/multimedia/camera/anupam/transaction_level_experiments/platform2_experiments/prototype/"

def binaryTodecimal(binary):
    binary1 = binary
    decimal, i, n = 0, 0, 0
    while(binary !=0):
        dec = binary % 10
        decimal = decimal + dec*pow(2, i)
        binary = binary//10
        i+=1
    return decimal

def data_plot(x, y, legend):
    axes = plt.gca()
    axes.set_xlim([0,x_axis])
    plt.plot(x, y, label=legend)
    plt.legend()

def show_plot(xlabel, ylabel, title):
    plt.xlabel("Time in microsecond")
    plt.ylabel("Drain rate")
    plt.title("Transaction Analysis")
    plt.grid()
    plt.show()


def max_time_for_max_buffer_fill(csv_file1, csv_file2, filter, usecase_names, experiments, abs_path):
    file_name = abs_path + "/All_four_image_engine_front_writeBuffer.csv"
    with open(file_name, "r+")as f:
        max_buffer_fill0 = 0
        max_buffer_fill1 = 0
        max_buffer_fill3 = 0
        data = f.readlines()
        data = data[1:]
        for i in range(len(data)):
            NW_initiate_unit_buffer3 = data[i].split(",")[4].rstrip("\n")
            NW_initiate_unit_buffer3 = NW_initiate_unit_buffer3.replace("K", "e3")
            NW_initiate_unit_buffer1 = data[i].split(",")[2].rstrip("\n")
            NW_initiate_unit_buffer1 = NW_initiate_unit_buffer1.replace("K", "e3")
            NW_initiate_unit_buffer0 = data[i].split(",")[1].rstrip("\n")
            NW_initiate_unit_buffer0 = NW_initiate_unit_buffer0.replace("K", "e3")

            if (float(data[i].split(",")[0]) / 1000000) < 151:
                if (float(NW_initiate_unit_buffer3)) > max_buffer_fill3:
                    max_buffer_fill3 = float(NW_initiate_unit_buffer3)
                    max_time = int(float(data[i].split(",")[0]) / 1000000)

                if (float(NW_initiate_unit_buffer1)) > max_buffer_fill1:
                    max_buffer_fill1 = float(NW_initiate_unit_buffer1)

                if (float(NW_initiate_unit_buffer0)) > max_buffer_fill0:
                    max_buffer_fill0 = float(NW_initiate_unit_buffer0)
        print(str(max_time) + "," + str(max_buffer_fill0) + "," + str(max_buffer_fill1) + "," + str(max_buffer_fill3))
        priority_distribution_count(csv_file1, csv_file2, filter, usecase_names, experiments, abs_path, max_time)



def priority_distribution_count(file_name1, file_name2, time_variable, mp, exp_name, abs_path, max_time):
    data1=[]
    data2=[]

    with open(file_name1, "r+") as f:
        reader1 = f.readlines()
        for element in reader1:
            data1.append(element)
        data1 = data1[1:]
        count_3 = 0
        count_4 = 0
        count_5 = 0
        count_6 = 0
        current_us=0
        previous_us=0
        bin_priority = 0
        priority_sum = 0
        transaction_sum1=0
        transactions_count=np.zeros(1001)
        count_3= np.zeros(1001)
        count_4 = np.zeros(1001)
        count_5 = np.zeros(1001)
        count_6 = np.zeros(1001)

        for i in range (len(data1) - 1):
            current_time = int((data1[i + 1].split(",")[0]))
            bin_priority = int((data1[i + 1].split(",")[1]))
            current_us = int((current_time/(time_variable*1000000))+1)
            transactions_count[current_us]+=1
            decimal_equiv = binaryTodecimal(bin_priority)

            if decimal_equiv == 3:
                count_3[current_us] = count_3[current_us] + 1
            elif decimal_equiv == 4:
                count_4[current_us] = count_4[current_us] + 1
            elif decimal_equiv == 5:
                count_5[current_us] = count_5[current_us] + 1
            elif decimal_equiv == 6:
                count_6[current_us] = count_6[current_us] + 1
            previous_us = current_us

    tmpdata="Microsecond_count,Transactions_count,Count_3,Count_4,Count_5,Count_6"+ "\n"
    graph_data1 = []
    for i in range(transactions_count.shape[0]):
        if (i*time_variable) <= max_time:
            transaction_sum1 += transactions_count[i]
            tmpdata += str(i * time_variable) + "," + str(int(transactions_count[i])) + "," + str(count_3[i]) + "," + str(count_4[i]) + "," + str(count_5[i]) + "," + str(count_6[i])
        else:
            graph_data1.append([int(i * time_variable),0])
    for i in range(max_time):
        graph_data1.append([i, (int(transaction_sum1)*256)/max_time])

    with open(file_name2, "r+") as f:
        reader2 = f.readlines()
        for element in reader2:
            data2.append(element)
        data2 = data2[1:]
        count_3 = 0
        count_4 = 0
        count_5 = 0
        count_6 = 0
        current_us=0
        previous_us=0
        bin_priority = 0
        priority_sum = 0
        transaction_sum2=0
        transaction_count=0
        transactions_count=np.zeros(1001)
        count_3= np.zeros(1001)
        count_4 = np.zeros(1001)
        count_5 = np.zeros(1001)
        count_6 = np.zeros(1001)

        for i in range (len(data2) - 1):
            current_time=int((data2[i + 1].split(",")[0]))
            bin_priority=int((data2[i + 1].split(",")[1]))
            current_us=int((current_time/(time_variable*1000000))+1)
            transactions_count[current_us]+=1
            decimal_equiv = binaryTodecimal(bin_priority)

            if decimal_equiv == 3:
                count_3[current_us] = count_3[current_us] + 1
            elif decimal_equiv == 4:
                count_4[current_us] = count_4[current_us] + 1
            elif decimal_equiv == 5:
                count_5[current_us] = count_5[current_us] + 1
            elif decimal_equiv == 6:
                count_6[current_us] = count_6[current_us] + 1
            previous_us = current_us

    tmpdata="Microsecond_count,Transactions_count,Count_3,Count_4,Count_5,Count_6"+ "\n"
    graph_data2 = []
    for i in range(transactions_count.shape[0]):
        if (i * time_variable) <= max_time:
            transaction_sum2 += transactions_count[i]
            tmpdata += str(i * time_variable) + "," + str(int(transactions_count[i])) + "," + str(count_3[i]) + "," + str(count_4[i]) + "," + str(count_5[i]) + "," + str(count_6[i])
        else:
            graph_data2.append([int(i * time_variable), 0])
    for i in range(max_time):
        graph_data2.append([i, (int(transaction_sum2)*256)/max_time]) 
    x_axis = []
    y_axis = []

    for i in range(min(len(graph_data1),len(graph_data2))):
        x_axis.append(graph_data1[i][0])
        y_axis.append(graph_data1[i][1] + graph_data2[i][1])
    legend = mp

def csv_writer(x_axis, y_axis,legend, abs_path):
    with open(str(legend)+".csv", 'w') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerow(['Microsecond_count', 'Drain rate'])
        for i in range (len(x_axis)):
            filewriter.writerow([str(x_axis[i]),str(y_axis[i])])

def get_all_csv(experiments,usecase_names,signal1, signal2):
    csv_file1 = os.path.join(transaction_level_output_path, experiments + "/platform2_CameraUseCase_Transient/"+ usecase_names, signal1)
    csv_file2 = os.path.join(transaction_level_output_path, experiments + "/ platform2_CameraUseCase_Transient/"+ usecase_names, signal2)
    abs_path =  os.path.join(transaction_level_output_path, experiments + "/ platform2_CameraUseCase_Transient/"+ usecase_names)
    max_time_for_max_buffer_fill(csv_file1, csv_file2, filter, usecase_names, experiments, abs_path)

if __name__ == "__main__":
    for i in range(len(all_experiment_names)):
        exp_by_exp = all_experiment_names[i]
        for j in range(len(all_usecaselist)):
            usecase_by_usecase = all_usecaselist[j]
            signal1 = transaction_analysis_signals_all[0]
            signal2 = transaction_analysis_signals_all[1]
            get_all_csv(exp_by_exp, usecase_by_usecase, signal1, signal2)

