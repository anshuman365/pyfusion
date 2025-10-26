from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get absolute path to your logo
package_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(package_dir, "pyfusion_v1", "assets", "logo.jpg")

setup(
    name="pyfusion_v1",
    version="1.0.1",  # Increment version
    author="PyFusion Team",
    author_email="anshumansingh3697@gmail.com",  
    description="All-in-One Python Framework with built-in web, database, and utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        'pyfusion_v1': ['assets/*.jpg', 'assets/*.png'],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.25.0",
        "sqlalchemy>=1.4.0",
        "jinja2>=3.0.0",
    ],
    keywords="framework web database utilities flask requests",
    url="https://github.com/anshuman365/pyfusion",
    project_urls={
        "Bug Reports": "https://github.com/anshuman365/pyfusion/issues",
        "Source": "https://github.com/anshuman365/pyfusion",
        "Documentation": "https://github.com/anshuman365/pyfusion#readme",
    },
)