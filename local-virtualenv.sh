# Clean up previous runs
rm -rf ~/.virtualenv 2> /dev/null
rm -rf ~/.virtualenv-temp 2> /dev/null
mkdir ~/.virtualenv-temp

# Copy the wheels so virtualenv.py can find them
cp wheelhouse/* ~/.virtualenv-temp

cd ~/.virtualenv-temp

echo " -- Fetching virtualenv.py"
curl -L -o virtualenv.py https://raw.github.com/pypa/virtualenv/master/virtualenv.py

echo " -- Create virtualenv-temp"
python virtualenv.py ~/.virtualenv-temp

echo " -- Activate the virtualenv-temp"
source ~/.virtualenv-temp/bin/activate

echo " -- Install virtualenv VIA pip"
pip install virtualenv

echo " -- Create the virtualenv"
virtualenv --no-site-packages ~/.virtualenv

echo " -- Activate the virtualenv"
source ~/.virtualenv-temp/bin/activate

# Clean temp environment
rm -rf ~/.virtualenv-temp

echo " -- Now Activiate the virtualenv"
echo "VIRTUAL_ENV_DISABLE_PROMPT=1"
echo "source ~/.virtualenv/bin/activate"
