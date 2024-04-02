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
        'clld>=11.0.1',
        'clldmpg>=4.3.0',
        'clldutils>=3.20.0',
        'clld-glottologfamily-plugin>=4.0.0',
        'cldfzenodo>=2.1.1'
        'csvw>=3.1.3',
        'pyglottolog>=3.12.0',
        'pyconcepticon>=3.0.0',
        'pycldf>=1.37.0',
        'sqlalchemy>=1.4.23',
        'waitress>=1.4.4',
    ],
    extras_require={
        'dev': [
            'flake8',
            'tox',
        ],
        'test': [
            'psycopg2>=2.8.6',
            'pytest>=7.4.2',
            'pytest-clld>=1.2.0',
            'pytest-mock>=3.10.0',
            'pytest-cov>=4.0.0',
            'coverage>=7.3.2',
            'selenium>=3.141.0',
            'zope.component>=5.0.1',
        ],
    },
    test_suite="ids",
    entry_points="""\
    [paste.app_factory]
    main = ids:main
    """,
)
