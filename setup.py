from setuptools import setup, find_packages


setup(
    name='grocery-tallies',
    version='0.0.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'pyside2',
        'pint',
        'sqlalchemy',
    ],
    entry_points='''
    [console_scripts]
    grocery_tallies=grocery_tallies.__main__:__main__
    '''
)
