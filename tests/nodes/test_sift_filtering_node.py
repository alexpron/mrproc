from mrproc.nodes.custom_nodes import create_sift_filtering_node

sift_node = create_sift_filtering_node()
sift_node.inputs.input_tracks = "/home/alex/recherche/tests/diffusion_pipeline/core_diffusion_pipeline/tractogram_pipeline/tractography/tracked.tck"
sift_node.inputs.wm_fod = "/home/alex/recherche/tests/diffusion_pipeline/core_diffusion_pipeline/msmt_csd/diffusion2fod/wm.mif"
sift_node.inputs.filtered_tracks = (
    "/home/alex/recherche/tests/nodes/default_filtered_tracks_node.tck"
)

sift_node.run()
