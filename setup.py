from setuptools import setup, find_packages

setup(
    name='sip-server',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'opencv-python',
        'moviepy',
        'openai',
        # Add other dependencies from your requirements.txt
    ],
    entry_points={
        'console_scripts': [
            'server=my_project.server:main',  # Adjust this line to your entry point
        ],
    },
)
