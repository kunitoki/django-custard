from setuptools import setup

VERSION = __import__('custard').VERSION

setup(
    name='django-custard',
    version=VERSION,
    description='Django runtime generic customizable fields for any model.',
    author='Lucio Asnaghi (aka kunitoki)',
    author_email='kunitoki@gmail.com',
    url='https://github.com/kunitoki/django-custard',
    download_url='https://github.com/kunitoki/django-custard/releases/tag/%s' % VERSION,
    keywords=['django', 'models', 'fields', 'custom', 'admin', 'content types'],
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

