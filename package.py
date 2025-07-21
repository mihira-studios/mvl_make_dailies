# -*- coding: utf-8 -*-

name = 'mvl_make_dailies'
version = '0.2.0'

description = 'A Python script package for generating movies using Nuke.'

authors = ['DEEPAK THAPLIYAL']
help = [['README', 'README.md']] # Optional: If you have a README file

requires = [
     '~python-3',
    "mvl_core_pipeline",
    "mvl_rezboot"
]

private_build_requires = [
    "python-3",
    "mvl_rez_package_builder",
    
]

# Optional: Define tools if your package has standalone executables
tools = [
    'generate_movie', # This refers to the alias or a script in 'bin'
]

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
