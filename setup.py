# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

BASE_REQUIREMENTS = ["nipype"]
DEV_REQUIREMENTS = ["black", "flake8", "pytest", "pytest-cov", "codecov"]


setup(
    name="mrproc",
    version="0.0.0",
    packages=find_packages(),
    author="Alexandre Pron",
    description="Diffusion Weighted MRI processing pipelines",
    url="https://github.com/alexpron/mrproc",
    license="MIT",
    # python_requires='>=3.6',  # enforce Python 3.6 as minimum
    install_requires=BASE_REQUIREMENTS,
    extras_require={"dev": DEV_REQUIREMENTS},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
    ],
)
