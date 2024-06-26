from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "3.0.0"

long_description = (
    f"{Path('README.rst').read_text()}\n{Path('CHANGES.rst').read_text()}"
)

setup(
    name="plone.app.textfield",
    version=version,
    description="Text field with MIME type support",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone schema field",
    author="Martin Aspeli",
    author_email="optilude@gmail.com",
    url="https://pypi.org/project/plone.app.textfield",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "plone.base",
        "Zope",
    ],
    extras_require={
        "portaltransforms": ["Products.PortalTransforms"],
        "supermodel": ["plone.supermodel"],
        "widget": ["z3c.form"],
        "marshaler": ["plone.rfc822"],
        "editor": ["plone.schemaeditor"],
        "tests": [
            "lxml",
            "plone.app.testing",
            "plone.supermodel [test]",
            "plone.testing",
        ],
    },
    entry_points="""
      """,
)
