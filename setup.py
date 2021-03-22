from setuptools import setup
from _version import __version__ as _version

setup(
        name='cFS-GroundSystem',
        packages=['Subsystems','Subsystems.tlmGUI','Subsystems.cmdGui','Subsystems.cmdUtil'],
        include_package_data=True,
        version=_version,
        entry_points={
            'console_scripts':[
                'cFS-GroundSystem=GroundSystem:main'
                ]
            },
        )
