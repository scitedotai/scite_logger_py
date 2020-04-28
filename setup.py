from setuptools import setup

setup(name='scite_logger_py',
      version='0.1',
      description='Python logger for use in internal scite repos',
      url='https://github.com/scitedotai/scite_logger_py',
      author='Ashish Uppala',
      author_email='ashish@scite.ai',
      packages=['scite_logger_py'],
      install_requires=[
          'psutil',
          'python-json-logger'
      ],
      python_requires='>=3',
      zip_safe=False)
