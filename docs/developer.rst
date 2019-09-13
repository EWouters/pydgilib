Continuous Integration
======================

This project has been developed to include an extensive set of unit tests using
`pytest <https://pytest.org>`), as well as auto generated documentation using 
`Sphinx <https://www.sphinx-doc.org>`. Maintainers can push new releases to
`pip` using `twine`.

Update Documentation
--------------------

Make sure to set up a development installation of pydgilib as explained in the
readme before you start. Open a terminal in the root of the repository.

1. Navigate to the output folder of the documentation::

    $ cd docs/_build/html

2. If you have not cloned the `gh-pages` branch previously (otherwise switch to
the gh-pages branch)::

    $ git clone --branch gh-pages https://github.com/EWouters/pydgilib.git

3. Generate the docs::

    $ cd ../..
    $ make.bat html

4. Add the new docs to a commit and push to the live
`webpage <https://ewouters.github.io/pydgilib/>`::

    $ cd _build/html
    $ git add .
    $ git commit - m 'Update docs.'
    $ git push origin gh-pages


Push a new Release
------------------

This will update the package on pip. You will need to login to a pip account
with maintainers privileges to perform step 4. 

1. Set version tag in setup.py and docs/conf.py
2. Generate docs (as described above)
3. Generate new package::

    $ python setup.py sdist bdist_wheel

4. Push the package to pip::

    $ twine upload dist/*