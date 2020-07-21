"""
Diffusion-weighted MRI data processing pipeline:
In construction:
"""


# pipeline engine of nipype

# python interface to mrtrix3 (mrtrix3 need to be installed in your computer)
from mrproc.pipelines.diffusion import create_diffusion_pipeline


def test_create_diffusion_pipeline():

    diffusion_pipeline = create_diffusion_pipeline()
    diffusion_pipeline.write_graph(graph2use="colored",format="png")


if __name__ == "__main__":

    test_create_diffusion_pipeline()
