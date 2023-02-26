import os
from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__),
                                       os.pardir)))

requirements = [
    'django>=1.5',
    'django-import-export>=1.2.0',
    'tablib>=3.1.0'
]

extras_require = {
    'test': [],
}

setup(
    name='django-web-sheets',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    license='BSD License',
    description='A Django Extension to view/edit models on dynamkc web spreadsheet.',
    long_description=README,
    url='https://github.com/omarbenhamod/django-web-sheets',
    author='Omar BENHAMID',
    author_email='contact@obenhamid.me',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)