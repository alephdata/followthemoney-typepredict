from setuptools import setup, find_packages

setup(
    name="followthemoney-typepredict",
    version="0.1.0",
    long_description="Followthemoney Type Prediction",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords="",
    author="OCCRP",
    author_email="data@occrp.org",
    url="https://occrp.org",
    license="MIT",
    packages=find_packages(exclude=["ez_setup", "examples", "test"]),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "click >= 7.0",
        "orjson",
        "followthemoney",
        "alephclient",
        "normality",
        "tqdm",
        "fasttext",
    ],
    extras_require={
        "analysis": [
            "seaborn",
            "sklearn",
            "pandas",
        ]
    },
    entry_points={
        "console_scripts": [
            "ftm-typepredict =followthemoney_typepredict.cli:cli",
            "followthemoney-typepredict = followthemoney_typepredict.cli:cli",
        ],
    },
    test_suite="nose.collector",
    tests_require=["coverage", "nose"],
)
