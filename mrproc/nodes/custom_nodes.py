"""
Dirty wrapping of the Mrtrix3 command necessary but not available in Nipype

Quick and dirty wrappings using python function and  nipype's Function interface of
Mrtrix3 commands
"""
# TO DO: implement clean wrappings by forking nipype

import nipype.pipeline.engine as pe
from nipype.interfaces.utility import Function


def tcksift(input_tracks, wm_fod, act, filtered_tracks):
    """Wrapping of the tcksift command

    Default options and stopping criteria with processing mask derived from act tissue file
    :param input_tracks: path of the tractogram to filter
    :param wm_fod: path of the white matter fiber orientation distribution volume
    used to filter the tractogram
    :param filtered_tracks: path of the filtered tractogram
    :return:
    """
    import subprocess
    from distutils import spawn

    sift = spawn.find_executable("tcksift")
    print(sift)
    cmd = [sift, "-act", act, input_tracks, wm_fod, filtered_tracks]
    subprocess.run(cmd)
    pass


def create_sift_filtering_node():
    """

    :return:
    """
    sift_filtering = pe.Node(
        name="sift_filtering",
        interface=Function(
            input_names=["input_tracks", "wm_fod", "act", "filtered_tracks"],
            output_names=["filtered_tracks"],
            function=tcksift,
        ),
    )
    sift_filtering.inputs.filtered_tracks = 'filtered.tck'
    return sift_filtering



