from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

with open("README.md") as f:
    long_description = f.read()

setup(
    name="erpnext-commerce",
    version="0.1.0",
    description="ERPNext customization for commercial/trading companies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aleph Tech JSC",
    author_email="dev@alephtech.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.10",
)
