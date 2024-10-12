import setuptools


def get_readme():
    with open("README.rst") as f:
        return f.read()


setuptools.setup(
    # the first three fields are a must according to the documentation
    name="pygooglecloud",
    version="0.0.3",
    packages=[
        "pygooglecloud",
    ],
    # from here all is optional
    description="pygooglecloud helps you with command line interaction with gcp",
    long_description=get_readme(),
    long_description_content_type="text/x-rst",
    author="Mark Veltzer",
    author_email="mark.veltzer@gmail.com",
    maintainer="Mark Veltzer",
    maintainer_email="mark.veltzer@gmail.com",
    keywords=[
        "gcp",
        "gae",
        "python",
        "shell",
        "utilities",
    ],
    url="https://veltzer.github.io/pygooglecloud",
    download_url="https://github.com/veltzer/pygooglecloud",
    license="MIT",
    platforms=[
        "python3",
    ],
    install_requires=[
        "pylogconf",
        "pytconf",
        "google-auth",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={"console_scripts": [
        "pygooglecloud=pygooglecloud.main:main",
    ]},
)
