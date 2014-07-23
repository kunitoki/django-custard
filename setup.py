from setuptools import setup

from custard import VERSION

setup(
    name='django-custard',
    version=VERSION,
    license='MIT',
    url='https://github.com/kunitoki/django-custard',
    author='Lucio Asnaghi (aka kunitoki)',
    author_email='kunitoki@gmail.com',
    description='Django runtime generic customizable fields for any model.',
    long_description=open('README.rst').read(),
    packages=[
        'custard',
        'custard.tests',
    ],
    package_data={
        'custard': ['templates/custard/admin/*.html'],
    },
    install_requires=[
        "Django >= 1.6.5",
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
        'Environment :: Web Environment',
        'Topic :: Software Development',
    ]
)
