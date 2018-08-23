import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eksauth",
    version="0.0.2",
    author="Marcelo Bartsch",
    author_email="marcelo@bartsch.cl",
    description="Class to authenticate agains EKS or iam-authenticator k8s clusters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mbartsch/eks-python-authenticator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    py_modules=['eksauth'],
    install_requires=[
      'boto3',
      'kubernetes==7.0.0b1',
    ],
)
