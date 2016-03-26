from distutils.core import setup

setup(name='ypotf',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Mailing list software that runs as an IMAP and SMTP client.',
      url='http://dada.pink/ypotf/',
      packages=['ypotf'],
      install_requires = [
          'horetu',
      ],
      tests_require = [
          'pytest>=2.6.4',
      ],
      version='0.0.0',
      license='AGPL',
      entry_points = {'console_scripts': ['ypotf = ypotf:cli']},
)
