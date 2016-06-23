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
        'clld>=2.2.2',
        'clldmpg>=2.0.0',
        'clld-glottologfamily-plugin>=1.3',
        'pycldf>=0.3.0',
    ],
    tests_require=[
        'WebTest >= 1.3.1',  # py3 compat
        'mock',
        'psycopg2',
    ],
    test_suite="ids",
    entry_points="""\
    [paste.app_factory]
    main = ids:main
    """,
)
