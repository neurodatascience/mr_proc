#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: Vincent (Qing Wang)
# @Date:   2022-6-16
"""
======================================================
Get dataset subject session list (PPMI) for fMRIPrep preproc:
Input  dataset folder structure: PPMI_BIDS

Output file:  folder structure: ppmi_subject_session.csv
======================================================
"""
# libs and envs
from pathlib import Path
import pandas as pd
import os
import shutil

#QC image list
fMRIPrep_qc_dict = {'t1_image': 'desc-preproc_T1w.nii.gz',
                    't1_mask' : 'desc-brain_mask.nii.gz',
                    'aparcaseg' : 'desc-aparcaseg_dseg.nii.gz',
                    'aseg': 'desc-aseg_dseg.nii.gz',
                    'dseg': 'dseg.nii.gz',
                    'prob_csf': 'label-CSF_probseg.nii.gz',
                    'prob_gm' : 'label-GM_probseg.nii.gz', 
                    'prob_wm' : 'label-WM_probseg.nii.gz',
                    'mni_T1'  : 'space-MNI152NLin2009cAsym_res-2_desc-preproc_T1w.nii.gz',
                    'mni_mask': 'space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz', 
                    'mni_dseg': 'space-MNI152NLin2009cAsym_res-2_dseg.nii.gz',
                    'mni_csf' : 'space-MNI152NLin2009cAsym_res-2_label-CSF_probseg.nii.gz',
                    'mni_gm'  : 'space-MNI152NLin2009cAsym_res-2_label-GM_probseg.nii.gz', 
                    'mni_wm'  : 'space-MNI152NLin2009cAsym_res-2_label-WM_probseg.nii.gz'
                   }
Freesurfer_qc_dict = {'aseg'  : 'aseg.stats',
                      'wmparc':'wmparc.stats',
                      # left hemisphere
                      'lh.a2009s' : 'lh.aparc.a2009s.stats',
                      'lh.DKT'    : 'lh.aparc.DKTatlas.stats',
                      'lh.pial'   : 'lh.aparc.pial.stats',
                      'lh.aparc'  : 'lh.aparc.stats',
                      'lh.BA_exvivo': 'lh.BA_exvivo.stats',
                      'lh.BA_exvivo_th' : 'lh.BA_exvivo.thresh.stats', 
                      'lh.curv' : 'lh.curv.stats',
                      'lh.w-g.pct' : 'lh.w-g.pct.stats',
                      # right hemisphere
                      'rh.a2009s': 'rh.aparc.a2009s.stats', 
                      'rh.DKT'   : 'rh.aparc.DKTatlas.stats',
                      'rh.pial'  : 'rh.aparc.pial.stats',
                      'rh.aparc' : 'rh.aparc.stats',
                      'rh.BA_exvivo' : 'rh.BA_exvivo.stats',
                      'rh.BA_exvivo_th' : 'rh.BA_exvivo.thresh.stats', 
                      'rh.curv' : 'rh.curv.stats',
                      'rh.w-g.pct' : 'rh.w-g.pct.stats'
                     }

## functions
def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='Input of pamameters: ')
    parser.add_argument('--data', type=str, default = 'data')
    parser.add_argument('--report_dir', type=str, default = 'report_dir')
    parser.add_argument('--code_dir', type=str, default = 'code_dir')
    args = parser.parse_args()
    return args

def main(dataset_dir, report_dir, code_dir):
    root_str       = dataset_dir         # "/scratch/PPMI_ses-21_fmriprep_anat_20.2.7"
    out_report_dir = report_dir          # '/scratch' # CC
    out_csv_dir    = code_dir            # out_report_dir+'/mr_proc/workflow/fMRIPrep'
    #
    root_dir = Path(root_str)
    fmriprep_dir = root_dir / "fmriprep"
    fs_dir = root_dir / "freesurfer-6.0.1"
    ## general fMRIPrep info
    root_folder = root_str.split('/')[-1]
    [dataset_name, ses_full_str, software_name, proc_name, software_version]=root_folder.split('_')
    # Session info
    ses_name=ses_full_str.split('-')[-1]
    fs_ver = str(fs_dir).split('/')[-1].split('-')[-1]
    
    # Setting up outputs
    # QC report folder
    report_folder_name=root_folder+"_report"
    qc_report_out_dir = Path(out_report_dir+'/'+report_folder_name)
    if (not qc_report_out_dir.is_dir()): os.mkdir(qc_report_out_dir) 
    else: shutil.rmtree(qc_report_out_dir); os.mkdir(qc_report_out_dir) 
    # QC summary table file
    qc_tab_file = Path(out_csv_dir+'/'+root_folder+"_report.csv")
    
    # Get subjects list
    sub_withFolder=[x for x in next(os.walk(fmriprep_dir))[1] if "sub" in x]
    sub_withReport=[x.split('.')[0] for x in next(os.walk(fmriprep_dir))[2] if x.split('.')[-1]=="html"]
    sub_fsFolder=[x for x in next(os.walk(fs_dir))[1] if "sub" in x]
    sub_list=list(set(sub_withFolder) or set(sub_reported) or set(sub_fsFolder))
    n_sub=len(sub_list)
    print(str(n_sub)+" fMRIPreped (version "+software_version+") subjects found for Dataset -> "+dataset_name+" Session -> "+ses_name)
    
    # Creat basic output dataframe
    qc_df = pd.DataFrame({'dataset':[dataset_name]*n_sub,'session':[ses_name]*n_sub,'fmriprep_proc':[proc_name]*n_sub,'fMRIPrep_ver':[software_version]*n_sub}, index=sub_list)
    for x in sub_withFolder: qc_df.loc[x,'sub_fMRIPrep']=1
    for x in sub_withReport: qc_df.loc[x,'sub_report']=1
    for x in sub_fsFolder: qc_df.loc[x,'sub_Freesurfer']=1
    for x in sub_fsFolder: qc_df.loc[x,'Freesurfer_ver']=fs_ver
    
    # Setting run-1
    current_run_str = '_run-1_';
    
    # QC over subjects
    for sub_id_str in sub_list:
        # copy out fMRIPrep report
        shutil.copytree(fmriprep_dir/sub_id_str/"figures", qc_report_out_dir/sub_id_str/"figures", dirs_exist_ok=True)
        shutil.copytree(fmriprep_dir/sub_id_str/"log", qc_report_out_dir/sub_id_str/"figures", dirs_exist_ok=True)
        shutil.copy2(fmriprep_dir/(sub_id_str+'.html'), qc_report_out_dir/(sub_id_str+'.html'))
        
        ## qc fmriprep
        sub_img_dir = fmriprep_dir/sub_id_str/ses_full_str/'anat'
        for k, v in fMRIPrep_qc_dict.items():
            current_fmriprep_file_name = sub_id_str+'_'+ses_full_str+current_run_str+v
            current_fmriprep_file = sub_img_dir/current_fmriprep_file_name
            if current_fmriprep_file.is_file():
                qc_df.loc[sub_id_str, k]=int(1)
            else:
                qc_df.loc[sub_id_str, k]=int(0)
                print(sub_id_str+' missing fMRIPrep results: '+current_fmriprep_file_name)
                
        ## qc freesurfer
        sub_fs_dir = fs_dir/sub_id_str/'stats'
        for k, v in Freesurfer_qc_dict.items():
        #print(str(sub_img_dir/(sub_id_str+'_'+ses_full_str+current_run_str+v)))
            current_fmriprep_file = sub_fs_dir/v
            if current_fmriprep_file.is_file():
                qc_df.loc[sub_id_str, k]=int(1)
            else:
                qc_df.loc[sub_id_str, k]=int(0)
                print(sub_id_str+' missing Freesurfer results: '+v)
    
    ## zip and save results        
    shutil.make_archive(out_report_dir+'/'+report_folder_name, 'zip', str(qc_report_out_dir))
    # save QC report
    qc_df.loc['Total']= qc_df.sum(numeric_only=True, axis=0)
    qc_df.to_csv(qc_tab_file)
    print("QC finished!")
    return 1

if __name__ == '__main__':
    args=get_args()
    dataset_dir_ = args.data
    report_dir_  = args.report_dir
    code_dir_  = args.code_dir
    print("QCing fMRIPrep results in: "+dataset_dir_+", results saved in "+code_dir_)
    main(dataset_dir_, report_dir_, code_dir_)
    