from setuptools import setup


setup(
        name                = "ft_apy",
        version             = "0.0.2",
        description         = "42api Library for Python3",
        url                 = "https://github.com/taeng42/ft_apy.git",
        author              = "Hyundong",
        author_email        = "hyundong@42seoul.kr",
        license             = "mit",
        #packages            = find_packages(exclude = []),
        install_requires    = ["setuptools", "wheel", "urllib3"],
        packages            = ["ft_apy"],
        zip_safe            = False,
        python_requires     = '>=3',
        classifiers         = [
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            ],
        )
