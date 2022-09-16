from setuptools import setup, find_packages


setup(
    name='rankings_UI',
    version='1.0',
    license='MIT',
    author="Marina Meila",
    author_email='email@example.com',
    packages=find_packages('rankings_UI'),
    package_dir={'': 'rankings_UI'},
    url='https://github.com/mk322/Rankings-UI',
    keywords='GUI',
    install_requires=[
          'Tkinter',
          'pandas',
          'numpy'
      ],

)
