from setuptools import setup, find_packages

from custard import __author__, __version__, __license__, __email__

setup(
    name='django-custard',
    version=__version__,
    license=__license__,
    url='https://github.com/kunitoki/django-custard',
    download_url='https://pypi.python.org/pypi/django-custard',
    author=__author__,
    author_email=__email__,
    description='Django runtime typed custom fields for any model.',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django >= 1.7",
    ],
    keywords=[
        'django',
        'models',
        'fields',
        'custom',
        'admin',
        'content types'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Environment :: Web Environment',
        'Topic :: Software Development',
    ]
)
