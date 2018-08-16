import glob
import setuptools

setuptools.setup(
    name='start_repair',
    version='0.0.1',
    description='Provides the automated repair component for START',
    author='Chris Timperley',
    author_email='christimperley@gmail.com',
    url='https://gitlab.eecs.umich.edu/ChrisTimperley/start-repair',
    install_requires=[
        'start-image',
        'start-core',
        'bugzoo',
        'darjeeling'
    ],
    python_requires='>=3.5',
    packages=['start_repair']
)
