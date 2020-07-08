"""
Diffusion-weighted MRI data processing pipeline:



"""


# pipeline engine of nipype
import nipype.pipeline.engine as pe

# python interface to mrtrix3 (mrtrix3 need to be installed in your computer)
from nipype.interfaces import mrtrix3
from nipype.interfaces import mrtrix


# Elementary bricks

# Data conversion from .nii to .mif file (allows to embed diffusion bvals et bvecs)
mrconvert = pe.Node(interface=mrtrix3.MRConvert(), name="mrconvert")

# Bias correction of the diffusion MRI data (for more quantitative approach)
dwibiascorrect = pe.Node(
    interface=mrtrix3.preprocess.DWIBiasCorrect(), name="dwibiascorrect"
)
dwibiascorrect.use_ants = True

# gross brain mask stemming from DWI data
dwi2mask = pe.Node(interface=mrtrix3.utils.BrainMask(), name="dwi2mask")

# tensor coefficients estimation
dwi2tensor = pe.Node(interface=mrtrix3.reconst.FitTensor(), name="dwi2tensor")

# derived FA contrast for registration
tensor2fa = pe.Node(interface=mrtrix3.TensorMetrics(), name="tensor2fa")

# Tissue classification from T1 MRI data
tissue_classif = pe.Node(interface=mrtrix3.Generate5tt(), name="tissue_classif")
# rely on FSL for T1 tissue segmentation
tissue_classif.inputs.algorithm = "fsl"

# impulsionnal response estimation
dwi2response = pe.Node(interface=mrtrix3.preprocess.ResponseSD(), name="dwi2response")
dwi2response.inputs.algorithm = "msmt_5tt"

# Multi-shell multi tissue spherical deconvolution of the diffusion MRI data
dwi2fod = pe.Node(
    interface=mrtrix3.reconst.ConstrainedSphericalDeconvolution(), name="msmt-csd"
)

# Probabilistic and anatomically constrained whole brain local tractography
tractography = pe.Node(interface=mrtrix3.tracking.Tractography(), name="tckgen")
tractography.inputs.algorithm = "iFOD2"
tractography.inputs.n_tracks = 5000000
tractography.inputs.crop_at_gmwmi = True
tractography.inputs.backtrack = True
tractography.inputs.min_length = 10  # 10 mm to avoid spurious streamlines
tractography.inputs.max_length = 300  # 300 mm

# TODO create command line interface for tcksift
# TODO create command line interface for mrregister or use dipy
# TODO create function interface for tckconvert or use dipy


# Workflows corresponding to main steps (for the sake of modularity)

# pre-processing
preproc = pe.Workflow(name="preproc")
preproc.connect(mrconvert, "out_file", dwibiascorrect, "in_file")
preproc.connect(dwibiascorrect, "out_file", dwi2mask, "in_file")

# tensor: tensor estimation + derived metrics computation (FA)
tensor = pe.Workflow(name="tensor")
tensor.connect(dwi2tensor, "out_file", tensor2fa, "in_file")

# msmt-csd reconstruction
csd = pe.Workflow(name="msmt-csd")
csd.connect(
    [
        (
            dwi2response,
            dwi2fod,
            [("wm_file", "wm_txt"), ("gm_file", "gm_txt"), ("csf_file", "csf_txt"),],
        )
    ]
)

# main pipeline
diffusion_pipeline = pe.Workflow(name="diffusion_pipeline")
# inter nodes links
diffusion_pipeline.connect(
    preproc, "dwibiascorrect.out_file", tensor, "dwi2tensor.in_file"
)
diffusion_pipeline.connect(preproc, "dwi2mask.out_file", tensor, "dwi2tensor.in_mask")
diffusion_pipeline.connect(
    preproc, "dwibiascorrect.out_file", csd, "dwi2response.in_file"
)
diffusion_pipeline.connect(tissue_classif, "out_file", csd, "dwi2response.mtt_file")
diffusion_pipeline.connect(preproc, "dwibiascorrect.out_file", csd, "dwi2fod.in_file")
diffusion_pipeline.connect(preproc, "dwi2mask.out_file", csd, "dwi2response.in_mask")
diffusion_pipeline.connect(csd, "dwi2fod.wm_odf", tractography, "in_file")
diffusion_pipeline.connect(preproc, "dwi2mask.out_file", tractography, "seed_gmwmi")
diffusion_pipeline.connect(preproc, "dwi2mask.out_file", tractography, "roi_mask")
diffusion_pipeline.connect(tissue_classif, "out_file", tractography, "act_file")


if __name__ == "__main__":
    pass
