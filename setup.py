import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Andon Lights Network Monitoring",
    version="0.0.1",
    author="Eugene B. OCa",
    author_email="eugenebasiliscooca@gmail.com",
    description="Andon Lights Network Monitoring for EATON",
    url="https://github.com/eugeneoca/andon_lights.git",
    packages=setuptools.find_packages(),
    install_requires=[
        'mysql-connector'
    ],
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
    ),
)