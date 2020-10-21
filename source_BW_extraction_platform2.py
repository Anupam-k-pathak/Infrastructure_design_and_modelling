import gzip
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-exp', type=str, dest='exp_name',
                     default='display_priority_3',
                    help='test cases folder')
parser.add_argument('-u', type=str, dest='usecase_list',
                     default='40MP',
                    help='usecase list')

parser.add_argument('-t', type=int, dest='time',
                     default=200,
                    help='usecase list')
parser.add_argument('-act', type=str, dest='action',
                     default='report_buffer',
                    help='usecase list')
parser.add_argument('-path', type=str, dest='path_for_exp',
                     default='/prj/camera/anupam/TLM_experiments/platform2_experiments/',
                    help='usecase list')

args = parser.parse_args()
exp_name = args.exp_name
all_experiment_names = exp_name.split(",")
usecase_list = args.usecase_list
all_usecaselist = usecase_list.split(",")
time = args.time
action = args.action
path_for_exp = args.path_for_exp

print("usecase_name,NW_initiate_unit0_SourceRate,NW_initiate_unit1_SourceRate,NW_initiate_unit2_SourceRate,NW_initiate_unit3_SourceRate")

def extract_source_BW(experiments, usecase_name):
    NW_initiate_unit0_buffer = 0
    NW_initiate_unit1_buffer = 0
    NW_initiate_unit3_buffer = 0
    NW_initiate_unit2_buffer = 0
    start = 0
    out_gz_file = os.path.join(path_for_exp, experiments + "/platform_CameraUC.Transient/" + usecase_name)
    with gzip.open(out_gz_file, "r+") as f:
        logs = f.readlines()


    for i in range(len(logs)):
        log=logs[i].decode()
        if "Statistics: image_engine_front0_hyp_config0_chroma" in log:
            start = 1
        if "image_engine_front0_display_chroma: Distibution Setting" in log:
            start = 0
            break
        if ("nBytesWr" in log) and (start == 1):
            if (("image_engine_front0" in log) and ("hyp_config0" in log)) or (("image_engine_front0" in log) and ("hyp_config5" in log)) or (("image_engine_front1" in log) and ("hyp_config0" in log)) or (("image_engine_front1" in log) and ("hyp_config5" in log)) or (("image_engine_front2" in log) and ("hyp_config0" in log)) or (("image_engine_front2" in log) and ("hyp_config5" in log)):
                log = log.split('=')
                hyp_config = log[0]
                log = log[1].split('//')
                a = log[0].rsplit()
                NW_initiate_unit0_buffer = NW_initiate_unit0_buffer + int(a[0])


            if (("image_engine_front0" in log) and ("hyp_config4" in log)) or (("image_engine_front0" in log) and ("hyp_config2" in log)) or (("image_engine_front0" in log) and ("hyp_config7" in log)) or (("image_engine_front1" in log) and ("hyp_config4" in log)) or (("image_engine_front1" in log) and ("hyp_config2" in log)) or (("image_engine_front1" in log) and ("hyp_config7" in log)) or (("image_engine_front2" in log) and ("hyp_config4" in log)) or (("image_engine_front2" in log) and ("hyp_config2" in log)) or (("image_engine_front2" in log) and ("hyp_config7" in log)):
                log = log.split('=')
                hyp_config = log[0]
                log = log[1].split('//')
                a = log[0].rsplit()
                NW_initiate_unit1_buffer = NW_initiate_unit1_buffer + int(a[0])


            if (("image_engine_front0" in log) and ("hyp_config8" in log)) or (("image_engine_front0" in log) and ("hyp_config3" in log)) or (("image_engine_front1" in log) and ("hyp_config8" in log)) or (("image_engine_front1" in log) and ("hyp_config3" in log)) or (("image_engine_front2" in log) and ("hyp_config8" in log)) or (("image_engine_front2" in log) and ("hyp_config3" in log)):
                log = log.split('=')
                hyp_config = log[0]
                log = log[1].split('//')
                a = log[0].rsplit()
                NW_initiate_unit3_buffer = NW_initiate_unit3_buffer + int(a[0])
    NW_initiate_unit0_SourceByte = NW_initiate_unit0_buffer/time
    NW_initiate_unit1_SourceByte = NW_initiate_unit1_buffer/time
    NW_initiate_unit3_SourceByte = NW_initiate_unit3_buffer/time
    print(str(usecase_name) +"," + str(NW_initiate_unit0_SourceByte) + "," + str(NW_initiate_unit1_SourceByte) + ",0," + str(NW_initiate_unit3_SourceByte))



if __name__ == "__main__":
    for i in range(len(all_experiment_names)):
        exp_by_exp = all_experiment_names[i]
        for j in range(len(all_usecaselist)):
            usecase_by_usecase = all_usecaselist[j]
            extract_source_BW(exp_by_exp, usecase_by_usecase)

