import setuptools

with open('README.md', 'r') as f:
    long_desc = f.read()

setuptools.setup(
    name='lofar-h5plot',
    version='2.4.0',
    scripts=['h5plot'],
    author='Frits Sweijen',
    author_email='frits.sweijen@gmail.com',
    description='The spiritual successor to ParmDBplot for quickly reviewing gain solutions generated by NDPPP.',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    url='https://github.com/tikk3r/lofar-h5plot',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'PyQt5',
        'matplotlib',
        'numpy',
    ],
)
