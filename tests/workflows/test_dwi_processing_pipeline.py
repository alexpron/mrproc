"""
"""


from mrproc.workflows.dwi_processing import create_dwi_processing_pipeline


def test_create_dwi_processing_pipeline():

    diffusion_pipeline = create_dwi_processing_pipeline()
    # directory where the workflow is executed
    diffusion_pipeline.base_dir = '/home/alex/recherche/tests' #TO CHANGE
    inputnode = diffusion_pipeline.get_node('inputnode')
    inputnode.inputs.diffusion_volume = '/hpc/banco/Primavoice_Data_and_Analysis/DTI/cerimed/sub-04/dmri/default_acquisition/default_analysis/corrected_dwi_sub-04.nii.gz'
    inputnode.inputs.bvals = '/hpc/banco/Primavoice_Data_and_Analysis/DTI/cerimed/sub-04/dmri/default_acquisition/raw_bvals_sub-04.txt'
    inputnode.inputs.bvecs = '/hpc/banco/Primavoice_Data_and_Analysis/DTI/cerimed/sub-04/dmri/default_acquisition/default_analysis/corrected_bvecs_sub-04.txt'
    inputnode.inputs.t1_volume = '/hpc/banco/Primavoice_Data_and_Analysis/analysis_sub-04/anat/sub-04_ses-01_T1w_denoised_debiased_in-MNI152.nii.gz'
    inputnode.inputs.nb_tracks = 10000000
    inputnode.inputs.min_length = 30
    inputnode.inputs.max_length = 300
    diffusion_pipeline.write_graph(graph2use="colored", format="png")
    diffusion_pipeline.run()


if __name__ == "__main__":

    test_create_dwi_processing_pipeline()
