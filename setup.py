import setuptools
from setuptools import setup

setup(
    name="piranha-python",
    version="0.0.1.dev3",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=["libcst<1"],
    url="https://github.com/ffmmjj/piranha-python",
    license="MIT",
    author="Felipe Martins",
    author_email="ffmmjj@gmail.com",
    description="",
)
