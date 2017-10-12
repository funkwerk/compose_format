from setuptools import setup


def readme():
    with open('README.rst') as file:
        return file.read()


setup(
    name='compose_format',
    version='1.2.0',
    description='format docker-compose files',
    long_description=readme(),
    url='http://github.com/funkwerk/compose_format',
    author='Stefan Rohe',
    license='MIT',
    packages=['compose_format'],
    install_requires=['ruamel.yaml'],
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Environment :: Console',
        'Operating System :: OS Independent',
    ],
    keywords='docker-compose format docker yml',
    include_package_data=True,
    scripts=['bin/compose_format'])
