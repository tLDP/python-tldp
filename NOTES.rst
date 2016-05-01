Notes to future self
++++++++++++++++++++

To release a new version for different software consumers.

  * commit all of the changes you want
  * bump version in tldp/__init__.py
  * adjust debian/changelog in accordance with Debian policy
    N.B. the version must match what you put in tldp/__init__.py
  * run 'python contrib/rpm-release.py' which will regenerate a
    contrib/tldp.spec with the correct version
  * commit debian/changelog tldp/__init__.py and contrib/tldp.spec
  * tag the release
  * run 'git push origin master --tags'
  * run 'python setup.py sdist upload -r pypi'
  * run 'bash contrib/debian-release.py' (on a Debian-ish box)


