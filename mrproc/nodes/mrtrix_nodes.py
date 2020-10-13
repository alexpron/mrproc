"""
Usual Mrtrix3 Nipype nodes but with customized parameters
"""

import nipype.pipeline.engine as pe
from nipype.interfaces import mrtrix3


def create_tissue_classification_node():
    """
    Instanciate T1 volume tissue classification Nipype node
    :return: tissue_classif (Nipype Node)
    """
    # Tissue classification from T1 MRI data
    tissue_classif = pe.Node(interface=mrtrix3.Generate5tt(), name="tissue_classif")
    # rely on FSL for T1 tissue segmentation
    tissue_classif.inputs.algorithm = "fsl"
    tissue_classif.inputs.out_file = '5tt.mif'
    return tissue_classif


def create_tractography_node(n_tracks, min_length, max_length):
    """
    Generate whole brain probabilistic tractogram Nipype node
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
