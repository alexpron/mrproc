# Magnetic Resonance Imaging Processing
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
This package regroups pipelines used to process Magnetic Resonance Imaging (MRI) data. 

# Dependencies
The proposed treatment chains leverage the following  neuroimaging software:
+ [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki) 
+ [Mrtrix3](https://www.mrtrix.org)
+ [Ants](https://github.com/ANTsX/ANTs)

 
# Installation
```bash
git clone https://github.com/alexpron/mrproc.git
```

## User 
```bash
pip install . 
```
## Developer
```bash
pip install -e .['dev']
```

# Current Diffusion pipeline 
![graph](tests/workflows/graph.png)
## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://www.int.univ-amu.fr/spip.php?page=auteur&id_auteur=809&lang=en"><img src="https://avatars1.githubusercontent.com/u/7290245?v=4" width="100px;" alt=""/><br /><sub><b>David Meunier</b></sub></a><br /><a href="https://github.com/alexpron/mrproc/commits?author=davidmeunier79" title="Code">💻</a> <a href="https://github.com/alexpron/mrproc/pulls?q=is%3Apr+reviewed-by%3Adavidmeunier79" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/alexpron/mrproc/commits?author=davidmeunier79" title="Tests">⚠️</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!