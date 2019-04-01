echo "'pydgilib' folder:"
sphinx-apidoc -f -o source/ ../pydgilib

echo ""
echo "'pydgilib_extra' folder:"
sphinx-apidoc -f -o source/ ../pydgilib_extra

echo ""
echo "'tests' folder:"
sphinx-apidoc -f -o source/ ../tests

echo ""
echo "'atprogram' folder:"
sphinx-apidoc -f -o source/ ../atprogram
echo "Done! Now run 'make html'"

