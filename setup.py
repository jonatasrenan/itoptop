from distutils.core import setup

setup(
    name="itoptop",
    version="1.0.7",
    description="iTOP API Python Lib",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/jonatasrenan/itoptop/",
    author="Jonatas Renan",
    author_email="jonatasrenan@gmail.com",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    keywords="itop api concurrent datamodel",
    packages=["itoptop"],
    install_requires=[
        "requests",
        "lxml"
    ]
)
