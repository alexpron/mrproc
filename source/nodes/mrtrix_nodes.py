"""
Dirty wrapping of the Mrtrix3 command necessary but not available in Nipype

Commands are wrapped using python function and the Function variant interface of nipype
TO DO : use the Mrtrix3Base or CommandLine class of Nipype to perform a cleaner wrap
"""

import nipype.pipeline.engine as pe
from nipype.interfaces.utility import Function


def mrregister_rigid(image, template, transform):
    """
    Dirty wrapping of the Mrtrix3 mrregister command that estimate rigid transformation between
    image and template (reference image)
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
    Dirty wrapping of the mrtransform command to apply linear transform to a volume
    :param input:
    :param output:
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
    :param input_tracks:
    :param wm_fod:
    :param filtered_tracks:
    :return:
    """
    import subprocess
    from distutils import spawn

    sift = spawn.find_executable("tcksift")
    cmd = sift + " " + input_tracks + " " + wm_fod + " " + filtered_tracks
    subprocess.run(cmd)
    pass


def select_between_spheres(input_tracks, sphere1, sphere2, output_tracks):
    """
    Select tracks whose extremities are located inside two spheres
    :param input_tracks: path to the tck file
    :param sphere1:tuple  (x1,y1,z1,r1)
    :param sphere2: tuple (x2,y2,z2,r2)
    :param output_tracks: path to output the selected tracks
    :return: None
    """
    import subprocess
    from distutils import spawn

    def sphere_to_string(sphere):
        return str(sphere)[1:-1]

    tckedit = spawn.find_executable("tckedit")
    cmd = (
        tckedit
        + " "
        + input_tracks
        + " "
        + "-include"
        + " "
        + sphere_to_string(sphere1)
        + " "
        + "-include"
        + sphere_to_string(sphere2)
        + output_tracks
    )
    subprocess.run(cmd)
    pass


# create Nipype nodes associated to previously defined functions

rigid_transform_estimation = pe.Node(
    name="rigid_transform_estimation",
    interface=Function(
        input_names=["image", "template"],
        output_names=["transform"],
        function=mrregister_rigid,
    ),
)
apply_linear_transform = pe.Node(
    name="apply_linear_transform",
    interface=Function(
        input_names=["in_file", "transform"],
        output_names=["out_file"],
        function=mrtransform_linear,
    ),
)

sift_filtering = pe.Node(
    name="sift_filtering",
    interface=Function(
        input_names=["input_tracks", "wm_fod"],
        output_names=["filtered_tracks"],
        function=tcksift,
    ),
)
tracks_selection = pe.Node(
    name="tracks_selection",
    interface=Function(
        input_names=["input_tracks", "sphere1", "sphere2"],
        output_names=["output_tracks"],
    ),
)

rigid_registration = pe.Workflow(name="rigid_registration")
# assume only the transform is identical, warped volume can be different
rigid_registration.connect(
    rigid_transform_estimation, "transform", apply_linear_transform, "transform"
)
