from setuptools import setup, find_packages

setup(
    name="graphos",
    version="0.1.11",
    author="Edgardo Gutierrez Jr.",
    author_email="edgardogutierrezjr@gmail.com",
    description="Terminal graph visualization tool.",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
