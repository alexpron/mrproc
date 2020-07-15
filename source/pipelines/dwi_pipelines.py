"""
Diffusion-weighted MRI data processing pipelines:

"""


import nipype.pipeline.engine as pe
from nipype.interfaces import utility

# mrtrix3 need to be installed in the computer
from nipype.interfaces import mrtrix3

from source.nodes.mrtrix_nodes import sift_filtering, rigid_registration

N_TRACKS = 5000000


def create_preprocessing_pipeline():
    """
    Bias correction and gross masking of a distorsion corrected diffusion weighted volume
    :return:
    """

    # Bias correction of the diffusion MRI data (for more quantitative approach)
    dwibiascorrect = pe.Node(
        interface=mrtrix3.preprocess.DWIBiasCorrect(), name="dwibiascorrect"
    )
    dwibiascorrect.use_ants = True

    # gross brain mask stemming from DWI data
    dwi2mask = pe.Node(interface=mrtrix3.utils.BrainMask(), name="dwi2mask")

    # input and output nodes
    inputnode = pe.Node(
        utility.IdentityInterface(fields=["dwi_volume"], mandatory_inputs=False)
    )
    outputnode = pe.Node(
        utility.IdentityInterface(
            fields=["corrected_dwi_volume", "mask"], mandatory_inputs=False
        )
    )

    # pipeline structure
    preproc = pe.Workflow(name="preprocessing")
    preproc.connect(inputnode, "dwi_volume", dwibiascorrect, "in_file")
    preproc.connect(dwibiascorrect, "out_file", dwi2mask, "in_file")
    preproc.connect(dwibiascorrect, "out_file", outputnode, "corrected_dwi_volume")
    preproc.connect(dwi2mask, "out_file", outputnode, "mask")

    return preproc


def create_tensor_pipeline():
    """
    Estimate diffusion tensor coefficient and compute FA
    :return:
    """
    # tensor coefficients estimation
    dwi2tensor = pe.Node(interface=mrtrix3.reconst.FitTensor(), name="dwi2tensor")

    # derived FA contrast
    tensor2fa = pe.Node(interface=mrtrix3.TensorMetrics(), name="tensor2fa")

    # input and output nodes
    inputnode = pe.Node(
        utility.IdentityInterface(fields=["dwi_volume", "mask"], mandatory_inputs=False)
    )
    outputnode = pe.Node(utility.IdentityInterface(fields=["tensor_coeff", "fa"]))

    # Workflow structure
    tensor = pe.Workflow(name="tensor")
    tensor.connect(inputnode, "dwi_volume", dwi2tensor, "in_file")
    tensor.connect(inputnode, "mask", dwi2tensor, "in_mask")
    tensor.connect(dwi2tensor, "out_file", tensor2fa, "in_file")
    tensor.connect(dwi2tensor, "out_file", outputnode, "tensor_coeff")
    tensor.connect(tensor2fa, "out_fa", outputnode, "fa")

    return tensor


def create_spherical_deconvolution_pipeline():
    """
    Estimate impulsionnal response and derived multi-shell multi
    :return:
    """
    dwi2response = pe.Node(
        interface=mrtrix3.preprocess.ResponseSD(), name="dwi2response"
    )
    dwi2response.inputs.algorithm = "msmt_5tt"

    # Multi-shell multi tissue spherical deconvolution of the diffusion MRI data
    dwi2fod = pe.Node(
        interface=mrtrix3.reconst.ConstrainedSphericalDeconvolution(), name="dwi2fod"
    )

    # Input and output nodes
    inputnode = pe.Node(
        utility.IdentityInterface(
            fields=["dwi_volume", "mask", "5tt_file"], mandatory_inputs=False
        )
    )
    outputnode = pe.Node(
        utility.IdentityInterface(fields=["wm_fod"], mandatory_inputs=False)
    )

    # Workflow structure
    csd = pe.Workflow(name="msmt_csd")
    csd.connect(
        [
            (
                inputnode,
                dwi2response,
                [
                    ("dwi_volume", "in_file"),
                    ("mask", "in_mask"),
                    ("5tt_file", "mtt_file"),
                ],
            )
        ]
    )
    csd.connect(
        [
            (
                dwi2response,
                dwi2fod,
                [("wm_txt", "wm_file"), ("gm_txt", "gm_file"), ("csf_txt", "csf_file")],
            )
        ]
    )
    csd.connect(inputnode, "wm_odf", outputnode, "wm_odf")

    return csd


def create_tractography_pipeline(n_tracks=N_TRACKS, min_length=10, max_length=300):
    """
    Generate whole brain probabilistic and anatomically constrained tractogram
    :param n_tracks:
    :param min_length:
    :param max_length:
    :return:
    """
    tractography = pe.Node(interface=mrtrix3.tracking.Tractography(), name="tckgen")
    tractography.inputs.algorithm = "iFOD2"
    tractography.inputs.n_tracks = n_tracks
    tractography.inputs.crop_at_gmwmi = True
    tractography.inputs.backtrack = True
    tractography.inputs.min_length = min_length
    tractography.inputs.max_length = max_length

    return tractography


def create_tractogram_generation_pipeline(n_tracks=N_TRACKS):
    """
    Whole brain probabilistic anatomically constrained tractogram generation and filtering
    :return:
    """

    from source.nodes.mrtrix_nodes import sift_filtering

    tractography = create_tractography_pipeline(n_tracks)

    # Input and output nodes
    inputnode = pe.Node(
        utility.IdentityInterface(
            fields=["wm_fod", "mask", "act_file"], mandatory_inputs=False
        )
    )
    outputnode = pe.Node(
        utility.IdentityInterface(fields=["tractogram"], mandatory_inputs=False)
    )

    # Workflow structure
    tractogram_pipeline = pe.Workflow(name="tractogram")
    tractogram_pipeline.connect(
        [
            (
                inputnode,
                tractography,
                [("wm_fod", "in_file"), ("mask", "roi_mask"), ("act_file", "act_file")],
            )
        ]
    )
    tractogram_pipeline.connect(inputnode, "wm_fod", sift_filtering, "wm_fod")
    # brain mask is used to randomly draw seeds
    tractogram_pipeline.connect(inputnode, "mask", tractography, "seed_gmwmi")
    tractogram_pipeline.connect(
        tractography, "out_file", sift_filtering, "input_tracks"
    )
    tractogram_pipeline.connect(
        sift_filtering, "filtered_tracks", outputnode, "tractogram"
    )
    return tractogram_pipeline


def create_tissue_classification_pipeline():
    """
    :return:
    """
    # Tissue classification from T1 MRI data
    tissue_classif = pe.Node(interface=mrtrix3.Generate5tt(), name="tissue_classif")
    # rely on FSL for T1 tissue segmentation
    tissue_classif.inputs.algorithm = "fsl"
    return tissue_classif


def create_core_pipeline():
    """

    :return:
    """
    preprocessing = create_preprocessing_pipeline()
    tensor = create_tensor_pipeline()
    tissue_classif = create_tissue_classification_pipeline()
    csd = create_spherical_deconvolution_pipeline()
    tractogram_generation = create_tractogram_generation_pipeline()
    # Input and output nodes
    inputnode = pe.Node(
        utility.IdentityInterface(
            fields=["dwi_volume", "t1_volume"], mandatory_inputs=False
        )
    )
    outputnode = pe.Node(
        utility.IdentityInterface(
            fields=["corrected_dwi_volume", "wm_fod", "tractogram"],
            mandatory_inputs=False,
        )
    )
    # mandatory steps of the diffusion pipeline (for the sake of modularity)
    core_pipeline = pe.Workflow(name="core_diffusion_pipeline")
    core_pipeline.connect(
        inputnode, "dwi_volume", preprocessing, "inputnode.dwi_volume"
    )
    core_pipeline.connect(
        preprocessing, "outputnode.corrected_dwi_volume", tensor, "inputnode.dwi_volume"
    )
    core_pipeline.connect(preprocessing, "outputnode.mask", tensor, "inputnode.mask")
    core_pipeline.connect(
        preprocessing, "outputnode.corrected_dwi_volume", csd, "inputnode.dwi_volume"
    )
    core_pipeline.connect(
        tensor, "outputnode.fa", rigid_registration, "rigid_transform_estimation.image"
    )
    core_pipeline.connect(inputnode, "t1_volume", tissue_classif, "in_file")
    core_pipeline.connect(
        tissue_classif, "out_file", rigid_registration, "apply_linear_transform.in_file"
    )
    core_pipeline.connect(
        rigid_registration,
        "apply_linear_transform.out_file",
        csd,
        "dwi2response.mtt_file",
    )
    core_pipeline.connect(
        preprocessing, "outputnode.corrected_dwi_volume", csd, "inputnode.dwi_volume"
    )
    core_pipeline.connect(preprocessing, "outputnode.mask", csd, "inputnode.mask")
    core_pipeline.connect(csd, "outputnode.wm_fod", tractogram_generation, "wm_fod")
    core_pipeline.connect(
        preprocessing, "outputnode.mask", tractogram_generation, "seed_gmwmi"
    )
    core_pipeline.connect(preproc, "dwi2mask.out_file", tractography, "roi_mask")
    core_pipeline.connect(
        rigid_registration, "apply_linear_transform.out_file", tractography, "act_file"
    )


def create_diffusion_pipeline():

    # Data conversion from .nii to .mif file (allows to embed diffusion bvals et bvecs)
    mrconvert = pe.Node(interface=mrtrix3.MRConvert(), name="mrconvert")
    core_pipeline = create_core_pipeline()
    # input and output node
    inputnode = pe.Node(
        utility.IdentityInterface(
            fields=["dwi_volume", "bvals", "bvecs", "t1_volume"], mandatory_inputs=False
        )
    )
    outputnode = pe.Node(
        utility.IdentityInterface(fields=["tractogram"], mandatory_inputs=False)
    )

    diffusion_pipeline = pe.Workflow(name="diffusion_pipeline")
    diffusion_pipeline.connect([(inputnode, mrconvert, [("dwi_volume",)])])

    return diffusion_pipeline


if __name__ == "__main__":
    pass
