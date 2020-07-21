"""
Dirty wrapping of the Mrtrix3 command necessary but not available in Nipype

Commands are wrapped using python function and the Function variant interface of nipype
# TO DO : use the Mrtrix3Base or CommandLine class of Nipype to perform a cleaner wrap
"""

import nipype.pipeline.engine as pe
from nipype.interfaces import utility
from nipype.interfaces.utility import Function


def mrregister_rigid(image, template, transform):
    """
    Dirty wrapping of the Mrtrix3 mrregister command that estimate rigid transformation
    between a volume  and template volume

    See mrregister documentation for further details
    (https://mrtrix.readthedocs.io/en/latest/reference/commands/mrregister.html)

    :param image: path of the image to register
    :param template: path of the reference image
    :param transform: path of the text file containing the estimated transform
    :return:
    """
    import subprocess
    from distutils import spawn

    mrregister = spawn.find_executable("mrregister")
    cmd = (
            mrregister
            + " "
            + "-type rigid"
            + " "
            + "-rigid"
            + " "
            + transform
            + " "
            + image
            + " "
            + template
    )
    subprocess.run(cmd)
    pass


def mrtransform_linear(in_file, out_file, transform):
    """
    Dirty wrapping of the mrtransform command to apply linear transform to a volume.

    The transform is applied by modfying the affine transform in the header of the
    volume (see https://mrtrix.readthedocs.io/en/latest/reference/commands
    /mrtransform.html) for further details)

    :param in_file:
    :param out_file:
    :param transform:
    :return:
    """
    import subprocess
    from distutils import spawn

    mrtransform = spawn.find_executable("mrtransform")
    # inverse option is passed to take into account reverse convention (see Mrtrix doc)
    cmd = (
            mrtransform
            + " "
            + "-linear"
            + " "
            + transform
            + " "
            + "-inverse"
            + " "
            + in_file
            + " "
            + out_file
    )
    subprocess.run(cmd)
    pass


def tcksift(input_tracks, wm_fod, filtered_tracks):
    """
    Dirty wrapping of the tcksif filtering command (default options)
    :param input_tracks: path of the tractogram to filter
    :param wm_fod: path of the white matter fiber orientation distribution volume
    used to filter the tractogram
    :param filtered_tracks: path of the filtered tractogram
    :return:
    """
    import subprocess
    from distutils import spawn

    sift = spawn.find_executable("tcksift")
    cmd = sift + " " + input_tracks + " " + wm_fod + " " + filtered_tracks
    subprocess.run(cmd)
    pass


# Instantiate Nipype Nodes from the python wrappers (by default generic nodes are
# created)


def create_rigid_transform_est_node():
    """
    Instanciate a Nipype Node from mrregister python wrapper
    :return: rigid_transform_estimation (Node)
    """

    rigid_transform_estimation = pe.Node(
        name="rigid_transform_estimation",
        interface=Function(
            input_names=["image", "template"],
            output_names=["transform"],
            function=mrregister_rigid,
        ),
    )
    return rigid_transform_estimation


def create_apply_linear_transform_node():
    """
    Instanciate a Nipype Node  from mrtransform python wrapper
    :return: apply_linear_transform (Node)
    """
    apply_linear_transform = pe.Node(
        name="apply_linear_transform",
        interface=Function(
            input_names=["in_file", "transform"],
            output_names=["out_file"],
            function=mrtransform_linear,
        ),
    )
    return apply_linear_transform


def create_sift_filtering_node():
    """

    :return:
    """
    sift_filtering = pe.Node(
        name="sift_filtering",
        interface=Function(
            input_names=["input_tracks", "wm_fod"],
            output_names=["filtered_tracks"],
            function=tcksift,
        ),
    )
    return sift_filtering



