from setuptools import setup, find_packages

setup(
    name="dcat-metadata-analyzer",
    version="0.1.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "numpy",
        "pandas",
        "scikit-learn",
        "python-dotenv",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "isort",
            "mypy",
        ]
    },
)
