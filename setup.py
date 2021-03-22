from setuptools import setup

setup(
        name='GroundSystem',
        packages=['Subsystems','Subsystems.tlmGUI','Subsystems.cmdGui','Subsystems.cmdUtil'],
        include_package_data=True,
        version='0.0.0',
        entry_points={
            'console_scripts':[
                'startg=GroundSystem:main'
                ]
            },
        )
