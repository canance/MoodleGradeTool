from setuptools import setup, find_packages

setup(
    name='MoodleGradeTool',
    version='0.8',
    packages=find_packages(),
    url='',
    license='',
    author='Cory Nance, Phillip Wall',
    author_email='',
    description='A grading assist tool for Moodle program submissions',

    #Packaging information
    include_package_data=True,
    exclude_package_data={"": [".gitignore"]},

    #Requires
    setup_requires=["setuptools_git >= 0.3", ],
    install_requires=["lxml", "npyscreen", "enum34", "pexpect"],
    extra_requires=["pyside", ],

    #Entry points
    scripts=[""],
    entry_points={
        'console_scripts': ['moodlegradetool=moodlegradetool.grade:main'],
        'gui_scripts': ['qmoodlegradetool=moodlegradetool.qt.qgrade:main'],
        'moodlegradetool.testers': [
            'RegexTester=moodlegradetool.testing:RegexTester',
            'AdvancedRegexTester=moodlegradetool.testing:AdvancedRegexTester'
        ]
    }


)
