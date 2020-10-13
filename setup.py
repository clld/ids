from setuptools import setup, find_packages


setup(
    name='ids',
    version='0.0',
    description='ids',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'clld>=7.2',
        'clldmpg>=4.0',
        'clldutils>=3.5.4',
        'clld-glottologfamily-plugin>=4.0',
        'csvw>=1.8',
        'pyglottolog>=3.2.2',
        'pyconcepticon>=2.6',
        'pycldf>=1.15',
        'sqlalchemy>=1.3',
        'waitress>=1.4.4',
    ],
    extras_require={
        'dev': [
            'flake8',
            'tox',
        ],
        'test': [
            'psycopg2>=2.8.6',
            'pytest>=6.0',
            'pytest-clld>=1.0.2',
            'pytest-mock>=3.3.1',
            'pytest-cov>=2.10.1',
            'coverage>=5.3',
            'selenium>=3.141',
            'zope.component>=4.6.2',
        ],
    },
    test_suite="ids",
    entry_points="""\
    [paste.app_factory]
    main = ids:main
    """,
)
