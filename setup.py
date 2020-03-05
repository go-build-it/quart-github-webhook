from setuptools import setup

setup(
    name="quart-github-webhook",
    use_scm_version={
        'local_scheme': 'dirty-tag',
    },
    description="Very simple, but powerful, microframework for writing Github webhooks in Python",
    url="https://github.com/go-build-it/quart-github-webhook",
    author="Jamie Bliss",
    author_email="jamie@gobuild.it",
    license="Apache 2.0",
    packages=["quart_github_webhook"],
    install_requires=["quart"],
    classifiers=[
        "Development Status :: 4 - Beta",
        # "Framework :: Quart",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Version Control",
    ],
)
