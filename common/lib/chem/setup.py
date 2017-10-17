from setuptools import setup

setup(
    name="chem",
    version="0.1.2",
    packages=["chem"],
    install_requires=[
        "pyparsing==2.0.7",
        "numpy==1.6.2",
        "scipy==0.14.0",
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        "nltk==3.2.5",
=======
        "nltk==3.2.2",
>>>>>>> updating nltk
=======
        "nltk==2.0.6",
>>>>>>> FIX: nltk update, version conlicting badly due to edx changes and forking
=======
        "nltk==3.2.2",
>>>>>>> reverting nltk change
=======
        "nltk==2.0.6",
>>>>>>> reverting nltk back to v2.0.6
    ],
)
