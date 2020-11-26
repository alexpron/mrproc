from mrproc.nodes.custom_nodes import tcksift
input_tracks ='/home/alex/recherche/tests/diffusion_pipeline/core_diffusion_pipeline' \
 '/tractogram_pipeline/tractography/tracked.tck'
wm_fod = '/home/alex/recherche/tests/diffusion_pipeline/core_diffusion_pipeline/msmt_csd/diffusion2fod/wm.mif'
filtered_tracks = '/home/alex/recherche/tests/nodes/default_filtered_tracks.tck'

tcksift(input_tracks, wm_fod, filtered_tracks)