import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eksauth",
    version="0.0.1",
    author="Marcelo Bartsch",
    author_email="marcelo@bartsch.cl",
    description="Class to authenticate agains EKS or iam-authenticator k8s clusters",
    url="https://github.com/mbartsch/eks-python-authenticator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2 License",
        "Operating System :: OS Independent",
    ],
    py_modules=['eksauth'],
)