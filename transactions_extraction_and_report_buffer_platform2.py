import os
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-exp', type=str, dest='exp_name',
                     default='200us_platform2_default_config',
                    help='test cases folder')
parser.add_argument('-u', type=str, dest='usecase_list',
                     default= ‘single_cam_16MP@120fps',
                    help='usecase list')
parser.add_argument('-act', type=str, dest='action',
                     default='report_buffer',
                    help='usecase list')
parser.add_argument('-tlm', type=str, dest='path_for_exp',
                     default='/prj/multimedia/camera/anupam/transaction_level_experiments/with_VCD/platform2_experiments/',
                    help='usecase list')

args = parser.parse_args()
exp_name = args.exp_name
all_experiment_names = exp_name.split(",")
transaction_analysis_signals = ['camera_NoC.trace.vcd.gz', 'camera_NoC.stat.vcd.gz', 'platform2.mm.trace.vcd.gz']
usecase_list = args.usecase_list
all_usecaselist = usecase_list.split(",")
action = args.action
path_for_exp = args.path_for_exp

def generate_fsdb(experiments, usecase_name, signal):
    vcd_file = os.path.join(path_for_exp, experiments + "/platform2_Camera_UseCase.Transient/" + usecase_name, signal)
    out_fsdb = vcd_file + ".fsdb"
    command = 'bsub -P 10355.04.mm -Ip -q short -R "select[type==LINUX64] rusage[mem=4000]" Vcd2fsdb ' + vcd_file + " -o " + out_fsdb + " & "
    print("Executing command :" + command)
    subprocess.call(command, shell=True)


def fsdbreport_buffer_outfile(experiments, usecase_names):
    buffer_report_out_path = os.path.join(path_for_exp, experiments + "/platform2_Camera_UseCase.Transient/"+ usecase_names)
    image_engine_front_csv = buffer_report_out_path + "/All_four_image_engine_front_writeBuffer.csv"
    command = 'bsub -P 10355.04.mm -Ip -q short -R "select[type==LINUX64] rusage[mem=4000]" Fsdbreport ' + buffer_report_out_path + """/camera_NoC.stat.vcd.gz.fsdb -s "/\platform2.camera_1.arch.camera_NoC_NW_initiate_unit_0:writeBuffer:level " "/\ platform2.camera_1.arch.camera_NoC_NW_initiate_unit_1:writeBuffer:level " "/\ platform2.camera_1.arch.camera_NoC_NW_initiate_unit_2:writeBuffer:level " "/\ platform2.camera_1.arch.camera_NoC_NW_initiate_unit_3:writeBuffer:level " -o """ + image_engine_front_csv + " -csv &"
    print("Executing command :" + command)
    subprocess.call(command, shell=True)


def fsdbreport_CameraNoC_csv(experiments, usecase_names):
    out_path = os.path.join(path_for_exp, experiments + "/platform2_Camera_UseCase.Transient/"+ usecase_names)
    CameraNoC_csvs_files = ["CameraNoC_hf0_ReqPrio.csv", "CameraNoC_hf1_ReqPrio.csv"]
    for i in range (len(CameraNoC_csvs_files)):
        command = 'bsub -P 10355.04.mm -Ip -q short -R "select[type==LINUX64] rusage[mem=4000]" Fsdbreport ' + out_path + """/platform2_multimediaNoC.trace.vcd.gz.fsdb -s "/SystemC/_CameraNoC_hf""" + str(i) + """_vld_req" -exp "/SystemC/_CameraNoC_hf""" + str(i) + """_vld_req == 1 & /SystemC/_bm_CameraNoC_hf""" + str(i) + """_Clk == 0 & /SystemC/_CameraNoC_hf""" + str(i) + """_Rdy_Req == 1" -o """ + out_path + """/platform2_CameraNoC_hf""" + str(i) + """_transaction.csv -csv &"""

        print("Executing command :" + command)
        subprocess.call(command, shell=True)


def fsdbreport_display_csv(experiments, usecase_names):
    out_path = os.path.join(path_for_exp, experiments + "/platform2_Camera_UseCase.Transient/"+ usecase_names)
    display_csvs_files = ["display0_ReqPrio.csv", "display1_ReqPrio.csv"]
    for i in range (len(display_csvs_files)):
        command = 'bsub -P 10355.04.mm -Ip -q short -R "select[type==LINUX64] rusage[mem=4000]" Fsdbreport ' + out_path + """/platform2.multimediaNoC.trace.vcd.gz.fsdb -s "/SystemC/_s_qm_display""" + str(i) + """_vld" -exp "/SystemC/_s_qm_display""" + str(i) + """_vld == 1 & /SystemC/_s_qm_display""" + str(i) + """_rdy == 1 & /SystemC/_bfm_qxm_display""" + str(i) + """_Clk == 0" -o """ + out_path + """/platform2_display""" + str(i) + """_transaction.csv -csv &"""

        print("Executing command :" + command)
        subprocess.call(command, shell=True)


def delete_header(image_engine_front01_csv):
    with open(image_engine_front01_csv, "r") as f:
        lines = f.readlines()
    lines= lines[1:]
    with open(image_engine_front01_csv, "w") as f:
        f.writelines(lines)


if __name__ == "__main__":

    if action == "vcd2fsdb":
        for i in range(len(all_experiment_names)):
            exp_by_exp = all_experiment_names[i]
            for j in range(len(all_usecaselist)):
                usecase_by_usecase = all_usecaselist[j]
                for k in range(len(transaction_analysis_signals)):
                    signal = transaction_analysis_signals[k]
                    generate_fsdb(exp_by_exp, usecase_by_usecase, signal)

    elif action == "report_buffer":
        for i in range(len(all_experiment_names)):
            exp_by_exp = all_experiment_names[i]
            for j in range(len(all_usecaselist)):
                usecase_by_usecase = all_usecaselist[j]
                fsdbreport_buffer_outfile(exp_by_exp, usecase_by_usecase)

    elif action == "report_CameraNoC":
        for i in range(len(all_experiment_names)):
            exp_by_exp = all_experiment_names[i]
            for j in range(len(all_usecaselist)):
                usecase_by_usecase = all_usecaselist[j]
                fsdbreport_CameraNoC_csv(exp_by_exp, usecase_by_usecase)

    elif action == "report_display":
        for i in range(len(all_experiment_names)):
            exp_by_exp = all_experiment_names[i]
            for j in range(len(all_usecaselist)):
                usecase_by_usecase = all_usecaselist[j]
                fsdbreport_display_csv(exp_by_exp, usecase_by_usecase)
    else:
        pass

