PATH_REPO='/home/alex/PycharmProjects/sctva'
PATH_SCRIPT=${PATH_REPO}/sctva/scripts/rigid_registration.py
# path to the chosen python (this python must contain the necessary package for the
# tested script to launch
PYTHON='/home/alex/softs/miniconda3/envs/test/bin/python'
# give the script file the right to be executed

FA='/home/alex/recherche/data/sctva/fa.mif'
T1='/hpc/banco/Primavoice_Data_and_Analysis/analysis_sub-04/anat/sub-04_ses-01_T1w_denoised_debiased_in-MNI152.nii.gz'
FUNC_T1='/hpc/banco/Primavoice_Data_and_Analysis/analysis_sub-04/spm_realign/results_8WM_9CSF_0mvt/In-MNI152_sub-04_res-8WM_9CSF_0mvt_human_vs_all_t.nii.gz'
DWI_TO_T1='/home/alex/recherche/data/sctva/test_dwi_to_t1'
T1_DWI='/home/alex/recherche/data/sctva/t1_dwi_space.mif'
FUNC_DWI='/home/alex/recherche/data/sctva/func_dwi_space.mif'

chmod u+x ${PATH_SCRIPT}
${PYTHON} ${PATH_SCRIPT} ${FA} ${T1} ${DWI_TO_T1} ${FUNC_T1} ${T1_DWI} ${FUNC_DWI}


