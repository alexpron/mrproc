"""
Dirty wrapping of the Mrtrix3 command necessary but not available in Nipype

Commands are wrapped using python function and the Function variant interface of nipype
# TO DO : use the Mrtrix3Base or CommandLine class of Nipype to perform a cleaner wrap
"""

import nipype.pipeline.engine as pe
from nipype.interfaces import utility
from nipype.interfaces.utility import Function



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



def create_sift_filtering_node():
    """

    :return:
    """
    sift_filtering = pe.Node(
        name="sift_filtering",
        interface=Function(
            input_names=["input_tracks", "wm_fod", "filtered_tracks"],
            output_names=["filtered_tracks"],
            function=tcksift,
        ),
    )
    sift_filtering.inputs.filtered_tracks='filtered_tracks.tck'
    return sift_filtering



