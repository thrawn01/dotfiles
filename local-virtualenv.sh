ENV_VER=virtualenv-13.1.0
ENV_SRC=$ENV_VER.tar.gz

# Clean up previous runs
rm -rf ~/.virtualenv 2> /dev/null
rm -rf ~/.virtualenv-temp 2> /dev/null
mkdir ~/.virtualenv-temp

cd ~/.virtualenv-temp

echo " -- Fetching virtualenv.py"
curl -O https://pypi.python.org/packages/source/v/virtualenv/$ENV_SRC

echo " -- Untar $ENV_SRC ..."
tar -vzxf $ENV_SRC
cd $ENV_VER

#echo " -- Create ~/.virtualenv"
python virtualenv.py ~/.virtualenv

# Clean temp environment
rm -rf ~/.virtualenv-temp

echo " -- Now Activiate the virtualenv"
echo "VIRTUAL_ENV_DISABLE_PROMPT=1"
echo "source ~/.virtualenv/bin/activate"
