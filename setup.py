from setuptools import setup, find_packages

setup(
    name='social-media-analytics-insights',
    version='0.1.0',
    description='Streamlit app for student social media analytics',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        'streamlit>=1.22.0',
        'pandas>=1.5.0',
        'plotly>=5.10.0',
        'seaborn>=0.12.0',
        'matplotlib>=3.5.0',
        'numpy>=1.23.0',
        'statsmodels>=0.14.0',
        'scikit-learn>=1.1.0'
    ],
    python_requires='>=3.8',
)
