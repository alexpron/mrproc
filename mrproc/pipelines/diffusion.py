"""
Diffusion-weighted MRI data processing pipelines

The pipelines cover the following steps:
+ Bias field correction
+ Gross mask extraction
+ Tensor and FA computation
+ Multi-Tissue Multi-Shell Constrained Spherical Deconvolution
+ Whole brain probabilistic anatomicaly constrained tractography
+ Tractogram filtering (SIFT)
+ T1 tissue classification
+ diffusion to T1 registration
Pipelines rely on MRtrix3, FSL, Ants and Nipype package
"""


import nipype.pipeline.engine as pe
from nipype.interfaces import utility
from nipype.interfaces import mrtrix3
from nipype.interfaces import fsl

from mrproc.nodes.mrtrix_nodes import create_tractography_node
from mrproc.nodes.mrtrix_nodes import create_tissue_classification_node
from mrproc.nodes.fsl_nodes import create_rigid_registration_node
from mrproc.nodes.custom_nodes import create_sift_filtering_node



# Constants
N_TRACKS = 5000000
MIN_LENGTH = 10  # mm
MAX_LENGTH = 300  # mm


def create_preprocessing_pipeline():
    """
    Bias correction and gross masking of a distortion corrected diffusion weighted volume
    :return:
    """

    # Bias correction of the diffusion MRI data (for more quantitative approach)
    diffusionbiascorrect = pe.Node(
        interface=mrtrix3.preprocess.DWIBiasCorrect(), name="diffusionbiascorrect"
    )
    diffusionbiascorrect.inputs.use_fsl = True

    # gross brain mask stemming from diffusion data
    diffusion2mask = pe.Node(interface=mrtrix3.utils.BrainMask(), name="diffusion2mask")

    # input and output nodes
    inputnode = pe.Node(
        utility.IdentityInterface(fields=["diffusion_volume"], mandatory_inputs=False),
        name="inputnode",
    )
    outputnode = pe.Node(
        utility.IdentityInterface(
            fields=["corrected_diffusion_volume", "mask"], mandatory_inputs=False
        ),
        name="outputnode",
    )

    # pipeline structure
    preproc = pe.Workflow(name="preprocessing")
    preproc.connect(inputnode, "diffusion_volume", diffusionbiascorrect, "in_file")
    preproc.connect(diffusionbiascorrect, "out_file", diffusion2mask, "in_file")
    preproc.connect(
        diffusionbiascorrect, "out_file", outputnode, "corrected_diffusion_volume"
    )
    preproc.connect(diffusion2mask, "out_file", outputnode, "mask")

    return preproc


def create_tensor_pipeline():
    """
    Estimate diffusion tensor coefficient and compute FA
    :return:
    """
    # tensor coefficients estimation
    diffusion2tensor = pe.Node(
        interface=mrtrix3.reconst.FitTensor(), name="diffusion2tensor"
    )
    # derived FA contrast
    tensor2fa = pe.Node(interface=mrtrix3.TensorMetrics(), name="tensor2fa")
    # Small hack to handle the lack of default name (nifti format used as fa need to
    # be processed by FSL for registration
    tensor2fa.inputs.out_fa = 'fa.nii.gz'

    # input and output nodes
    inputnode = pe.Node(
        utility.IdentityInterface(
            fields=["diffusion_volume", "mask"], mandatory_inputs=False
        ),
        name="inputnode",
    )
    outputnode = pe.Node(
        utility.IdentityInterface(
            fields=["tensor_coeff", "fa"], mandatory_inputs=False
        ),
        name="outputnode",
    )

    # Workflow structure
    tensor = pe.Workflow(name="tensor")
    tensor.connect(inputnode, "diffusion_volume", diffusion2tensor, "in_file")
    tensor.connect(inputnode, "mask", diffusion2tensor, "in_mask")
    tensor.connect(diffusion2tensor, "out_file", tensor2fa, "in_file")
    tensor.connect(diffusion2tensor, "out_file", outputnode, "tensor_coeff")
    tensor.connect(tensor2fa, "out_fa", outputnode, "fa")

    return tensor





def create_spherical_deconvolution_pipeline():
    """
    Estimate impulsionnal response and derived multi-shell multi tissue fiber
    orientation distribution (FOD)
    :return:
    """
    diffusion2response = pe.Node(
        interface=mrtrix3.preprocess.ResponseSD(), name="diffusion2response"
    )
    diffusion2response.inputs.gm_file = 'gm.txt'
    diffusion2response.inputs.csf_file = 'csf.txt'
    diffusion2response.inputs.algorithm = "msmt_5tt"

    # Multi-shell multi tissue spherical deconvolution of the diffusion MRI data
    diffusion2fod = pe.Node(
        interface=mrtrix3.reconst.ConstrainedSphericalDeconvolution(),
        name="diffusion2fod",
    )
    diffusion2fod.inputs.algorithm = 'msmt_csd'
    diffusion2fod.inputs.csf_odf = 'csf.mif'
    diffusion2fod.inputs.gm_odf = 'gm.mif'

    # Input and output nodes
    inputnode = pe.Node(
        utility.IdentityInterface(
            fields=["diffusion_volume", "mask", "5tt_file"], mandatory_inputs=False
        ),
        name="inputnode",
    )
    outputnode = pe.Node(
        utility.IdentityInterface(fields=["wm_fod"], mandatory_inputs=False),
        name="outputnode",
    )

    # Workflow structure
    csd = pe.Workflow(name="msmt_csd")
    csd.connect(
        [
            (
                inputnode,
                diffusion2response,
                [
                    ("diffusion_volume", "in_file"),
                    ("mask", "in_mask"),
                    ("5tt_file", "mtt_file"),
                ],
            )
        ]
    )
    csd.connect(
        [
            (
                diffusion2response,
                diffusion2fod,
                [("wm_file", "wm_txt"), ("gm_file", "gm_txt"), ("csf_file", "csf_txt")],
            )
        ]
    )
    csd.connect(inputnode, "diffusion_volume", diffusion2fod, "in_file")
    csd.connect(diffusion2fod, "wm_odf", outputnode, "wm_fod")

    return csd


def create_tractogram_generation_pipeline(
    n_tracks=N_TRACKS, min_length=MIN_LENGTH, max_length=MAX_LENGTH
):
    """
    Whole brain probabilistic anatomically constrained tractogram generation and filtering
    :return:
    """

    tractography = create_tractography_node(
        n_tracks, min_length=MIN_LENGTH, max_length=MAX_LENGTH
    )
    sift_filtering = create_sift_filtering_node()

    # Input and output nodes
    inputnode = pe.Node(
        utility.IdentityInterface(
            fields=["wm_fod", "mask", "act_file"], mandatory_inputs=False
        ),
        name="inputnode",
    )
    outputnode = pe.Node(
        utility.IdentityInterface(fields=["tractogram"], mandatory_inputs=False),
        name="outputnode",
    )

    # Workflow structure
    tractogram_pipeline = pe.Workflow(name="tractogram_pipeline")
    tractogram_pipeline.connect(
        [
            (
                inputnode,
                tractography,
                [("wm_fod", "in_file"), ("mask", "roi_mask"), ("act_file", "act_file")],
            )
        ]
    )
    # brain mask is used to randomly draw seeds
    tractogram_pipeline.connect(inputnode, "mask", tractography, "seed_gmwmi")
    tractogram_pipeline.connect(
        tractography, "out_file", outputnode, "tractogram"
    )

    return tractogram_pipeline


def create_core_pipeline():
    """

    :return:
    """
    # Pipeline Nodes
    # Inputs params
    inputnode = pe.Node(
        utility.IdentityInterface(
            fields=["diffusion_volume", "t1_volume"], mandatory_inputs=False
        ),
        name="inputnode",
    )
    # Processing steps
    preprocessing = create_preprocessing_pipeline()
    # tensor and derived metrics (FA)
    tensor = create_tensor_pipeline()
    #t1 brain extraction
    bet = pe.Node(fsl.preprocess.BET(robust=True), name="bet")
    # tissue classification (T1 volume)
    tissue_classif = create_tissue_classification_node()
    # rigid registration between diffusion and structural space
    rigid_registration = create_rigid_registration_node()
    # fa (dwi space) upsampling to 1mm ease registration
    resample_fa = pe.Node(fsl.preprocess.FLIRT(apply_isoxfm=1),
                          name="resample_fa")
    # apply rigid transformation
    applyxfm = pe.Node(fsl.preprocess.ApplyXFM(), name="applyxfm")
    # inverse rigid transformation
    invxfm = pe.Node(fsl.utils.ConvertXFM(invert_xfm=True), name="invxfm")

    # apply rigid transformation
    applyxfm = pe.Node(fsl.preprocess.ApplyXFM(), name="applyxfm")
    # inverse rigid transformation
    invxfm = pe.Node(fsl.utils.ConvertXFM(invert_xfm=True), name="invxfm")
  
    # Multi shell multi tissue spherical deconvolution
    csd = create_spherical_deconvolution_pipeline()
    # Whole brain anatomically constrained probabilistic tractogram
    tractogram_pipeline = create_tractogram_generation_pipeline()
    # Outputs params
    outputnode = pe.Node(
        utility.IdentityInterface(
            fields=["corrected_diffusion_volume", "wm_fod", "tractogram",
                    "diffusion_to_t1_transform"],
            mandatory_inputs=False,
        ),
        name="outputnode",
    )
    # mandatory steps of the diffusion pipeline (for the sake of modularity)
    core_pipeline = pe.Workflow(name="core_diffusion_pipeline")
    core_pipeline.connect(
        inputnode, "diffusion_volume", preprocessing, "inputnode.diffusion_volume"
    )
    core_pipeline.connect(
        preprocessing,
        "outputnode.corrected_diffusion_volume",
        tensor,
        "inputnode.diffusion_volume",
    )
    core_pipeline.connect(preprocessing, "outputnode.mask", tensor, "inputnode.mask")
    core_pipeline.connect(
        preprocessing,
        "outputnode.corrected_diffusion_volume",
        csd,
        "inputnode.diffusion_volume",
    )
    # Upsample FA to 1mm which is roughly the T1 resolution
    core_pipeline.connect(tensor,"outputnode.fa", resample_fa, "in_file")
    core_pipeline.connect(tensor, "outputnode.fa", resample_fa, "reference")
    # Estimate rigid transform (FA --> T1), invert it and apply it to tissue
    # brain masked T1 volume
    core_pipeline.connect(inputnode, "t1_volume", bet, "in_file")
    core_pipeline.connect(bet, "out_file", rigid_registration, "reference")

    core_pipeline.connect(tensor, "outputnode.fa", rigid_registration, "in_file")
    core_pipeline.connect(rigid_registration,"out_matrix_file", invxfm, "in_file")
    # transform is applied directly to T1 not to 5TT
    core_pipeline.connect(inputnode, "t1_volume", applyxfm, "in_file")
    core_pipeline.connect(invxfm, "out_file", applyxfm, "in_matrix_file")
    core_pipeline.connect(resample_fa, "out_file", applyxfm, "reference")
    core_pipeline.connect(applyxfm, "out_file", tissue_classif, "in_file")

    core_pipeline.connect(preprocessing, "outputnode.mask", csd, "inputnode.mask")
    core_pipeline.connect(tissue_classif, "out_file", csd, "inputnode.5tt_file" )
    core_pipeline.connect(
        csd, "outputnode.wm_fod", tractogram_pipeline, "inputnode.wm_fod"
    )
    core_pipeline.connect(tissue_classif, "out_file", tractogram_pipeline,
                          "inputnode.act_file")
    core_pipeline.connect(
        preprocessing, "outputnode.mask", tractogram_pipeline, "inputnode.mask"
    )

    core_pipeline.connect(
        tractogram_pipeline, "outputnode.tractogram", outputnode, "tractogram"
    )
    core_pipeline.connect(csd, "outputnode.wm_fod", outputnode, "wm_fod")
    core_pipeline.connect(
        preprocessing,
        "outputnode.corrected_diffusion_volume",
        outputnode,
        "corrected_diffusion_volume",
    )

    return core_pipeline


def create_diffusion_pipeline():


    # Nodes
    # Input params
    inputnode = pe.Node(
        utility.IdentityInterface(
            fields=["diffusion_volume", "bvals", "bvecs", "t1_volume"],
            mandatory_inputs=False,
        ),
        name="inputnode",
    )
    # Data conversion from .nii to .mif file (allows to embed diffusion bvals et bvecs)
    mrconvert = pe.Node(interface=mrtrix3.MRConvert(), name="mrconvert")
    # Main processing steps
    core_pipeline = create_core_pipeline()
    # Outputs params
    outputnode = pe.Node(
        utility.IdentityInterface(
            fields=["corrected_diffusion_volume", "wm_fod", "tractogram",
                    "diffusion_to_t1_transform"],
            mandatory_inputs=False,
        ),
        name="outputnode",
    )

    diffusion_pipeline = pe.Workflow(name="diffusion_pipeline")
    diffusion_pipeline.connect(
        [
            (
                inputnode,
                mrconvert,
                [
                    ("diffusion_volume", "in_file"),
                    ("bvals", "in_bval"),
                    ("bvecs", "in_bvec"),
                ],
            )
        ]
    )
    diffusion_pipeline.connect(
        mrconvert, "out_file", core_pipeline, "inputnode.diffusion_volume"
    )
    diffusion_pipeline.connect(
        inputnode, "t1_volume", core_pipeline, "inputnode.t1_volume"
    )
    diffusion_pipeline.connect(
        core_pipeline,
        "outputnode.corrected_diffusion_volume",
        outputnode,
        "corrected_diffusion_volume",
    )
    diffusion_pipeline.connect(core_pipeline, "outputnode.wm_fod", outputnode, "wm_fod")
    diffusion_pipeline.connect(
        core_pipeline, "outputnode.tractogram", outputnode, "tractogram"
    )
    diffusion_pipeline.connect(
        core_pipeline,"outputnode.diffusion_to_t1_transform", outputnode,
        "diffusion_to_t1_transform"
    )

    return diffusion_pipeline


if __name__ == "__main__":
    pass