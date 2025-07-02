# -*- coding: utf-8 -*-
import os
import sys

name = 'mvl_make_dailies'
version = '0.1.0'

description = 'A Python script package for generating movies using Nuke.'

authors = ['DEEPAK THAPLIYAL']
help = [['README', 'README.md']] # Optional: If you have a README file

requires = [
    'nuke',  
    "mvl_core_pipeline",
    '~python-3',    
                     
    # Add other Python dependencies here if your script uses them:
    # 'pyside2-5.15+', # Example if your script has a PySide2 UI
    # 'ocio-2.1+',     # Example if your script uses OpenColorIO Python bindings
]

private_build_requires = [
    "python-3",
    "mvl_rez_package_builder",
    
]

# Optional: Define tools if your package has standalone executables
tools = [
    'generate_movie', # This refers to the alias or a script in 'bin'
]

# If your script needs specific Nuke environments variables set, add them here.
# For example, if it expects a custom Nuke plugin path:
# env.NUKE_PATH.append('{root}/nuke/plugins')

def commands():
    # Add the 'python' subdirectory of this package to PYTHONPATH
    # This makes 'import nuke_movie_generator' work
    env.PYTHONPATH.append(os.path.join('{root}', 'python'))

    # Optional: If you have a 'bin' directory with executable scripts
    env.PATH.append(os.path.join('{root}', 'bin'))

    # Set up an alias to run your script easily
    # This assumes 'run_movie_generator.py' is in your 'bin' directory
    # or you have a main entry point in your python package.
    # Using 'command:' allows you to execute a Python script directly via Rez.
    #alias('generate_movie', 'python -m nuke_movie_generator.generate_movie')
    # Or, if you have a wrapper script in 'bin':
    # alias('generate_movie', 'run_movie_generator.py')


build_command = 'python {root}/build.py {install}'

def commands():
    env.PYTHONPATH.append("{root}/python")
    env.PATH.append("{root}/bin")


tests = {
    "unit":{
        "command": "python -m unittest discover -s tests",
        "requires": ["python-3"],
    }
}



# Optional: Add any specific Nuke menu or init.py hooks here if needed
# This might require more advanced Rez setup, potentially including a 'nuke_hooks'
# package that this package could then 'implements'.
# For simpler cases, your script itself might modify Nuke's menus.