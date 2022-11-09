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
        'clld>=9.2.2',
        'clldmpg>=4.2.0',
        'clldutils>=3.9.0',
        'clld-glottologfamily-plugin>=4.0.0',
        'csvw>=1.11.0',
        'pyglottolog>=3.6.0',
        'pyconcepticon>=2.8.0',
        'pycldf>=1.23.0',
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
            'pytest>=6.2.5',
            'pytest-clld>=1.0.3',
            'pytest-mock>=3.6.1',
            'pytest-cov>=2.12.1',
            'coverage>=5.5',
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
