from setuptools import setup, find_packages

import lazy_lxd


def long_description():
    with open('README.md') as fl:
        return fl.read()


install_requires = [
    'colorama>=0.4.3',
    'coolname>=1.1.0',
    'cryptography>=2.9.2',
    'halo>=0.0.29',
    'humanize>=2.4.0',
    'PyInquirer>=1.0.3',
    'pylx>=2.2.11',
    'python-dateutil>=2.8.1',
    'python-hosts>=1.0.0'
]

package_dir = {
    'lib.ansible': 'lazy_lxd/lib/ansible',
    'lib.inquirer': 'lazy_lxd/lib/inquirer',
    'lib.keys': 'lazy_lxd/lib/keys',
    'lib.logger': 'lazy_lxd/lib/logger',
    'lib.lxd': 'lazy_lxd/lib/lxd',
    'bin': 'lazy_lxd/bin'
}

packages = [
    'lib.ansible',
    'lib.inquirer',
    'lib.keys',
    'lib.logger',
    'lib.lxd',
    'bin'
] + find_packages()


setup(
    name='lazy-lxd',
    version=lazy_lxd.__version__,
    author=lazy_lxd.__author__,
    author_email='gomilt@gmail.com',
    license=lazy_lxd.__license__,
    description='Easy creating LXD containers with included routine.',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/vladisnik/lazy-lxd',
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        'Topic :: Terminals',
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        'Environment :: Console',
    ],
    package_dir=package_dir,
    packages=packages,
    install_requires=install_requires,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'lazy-lxd=lazy_lxd.__main__:main'
        ]
    }
)
