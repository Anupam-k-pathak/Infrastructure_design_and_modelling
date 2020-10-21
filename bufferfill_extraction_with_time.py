import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-exp', type=str, dest='exp_name',
                     default='Display_priority_3',
                    help='test cases folder')
parser.add_argument('-u', type=str, dest='usecase_list',
                     default='40MP',
                    help='usecase list')
parser.add_argument('-s',type=str, dest='image_front_engine_signals',
                     default = "image_front_engine_01_writeBuffer.csv",
                    help='usecase list')
parser.add_argument('-t',type=str, dest='time',
                     default = 5.0,
                    help='usecase list')


args = parser.parse_args()
exp_name = args.exp_name
all_experiment_names = exp_name.split(",")
image_front_engine_signals = args.image_front_engine_signals
image_front_engine_signals_all = image_front_engine_signals.split(",")
time = args.time
all_time_instants = time.split(",")
usecase_list = args.usecase_list
all_usecaselist = usecase_list.split(",")

print("Usecase,Time(in us),Buffer fill")

transaction_level_output_path = "/prj/multimedia/camera/anupam/transaction_level_experiments/prototype/platform_1/"

def report_buffer_fill(file_name, experiments, usecase_names, time_to_capture):
    data = []
    with open(file_name, "r+") as f:
        reader = f.readlines()
        for element in reader:
            data.append(element)

        for i in range (len(data) - 1):
            time_in_us=float((data[i + 1].split(",")[0]))/1000000

            if time_in_us >= float(time_to_capture):
                print(usecase_names[9:-14] + "," +time_to_capture + "," + str(data[i].split(",")[1]))
                break
        f.close()
def get_all_csv(experiments,usecase_names,signal, time_to_capture):
    csv_file = os.path.join(transaction_level_output_path, experiments + "/platform_1_AllUC_Transient/"+ usecase_names, signal)
    report_buffer_fill(csv_file, experiments, usecase_names, time_to_capture)

if __name__ == "__main__":
    for i in range(len(all_experiment_names)):
        exp_by_exp = all_experiment_names[i]
        for j in range(len(all_usecaselist)):
            usecase_by_usecase = all_usecaselist[j]
            for k in range(len(image_front_engine_signals_all)):
                signal = image_front_engine_signals_all[k]
                for m in range(len(all_time_instants)):
                    time_to_capture = all_time_instants[m]
                    get_all_csv(exp_by_exp, usecase_by_usecase, signal, time_to_capture)

