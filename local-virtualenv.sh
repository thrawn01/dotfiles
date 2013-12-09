rm -rf ~/.virtualenv 2> /dev/null
mkdir ~/.virtualenv
cd ~/.virtualenv

echo " -- Fetching virtualenv.py"
curl -L -o virtualenv.py https://raw.github.com/pypa/virtualenv/master/virtualenv.py

echo " -- Fetching git-pip.py"
curl -L -o get-pip.py https://raw.github.com/pypa/pip/master/contrib/get-pip.py

echo " -- Fetching ez_setup.py"
curl -L -o ez_setup.py https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py

echo " -- Create the virtualenv"
python virtualenv.py ~/.virtualenv

echo " -- Activate the virtualenv"
source ~/.virtualenv/bin/activate

echo " -- Run ez_setup.py"
python ez_setup.py

echo " -- Run get-pip.py"
python get-pip.py

echo " -- Now Activiate the virtualenv"
echo "VIRTUAL_ENV_DISABLE_PROMPT=1"
echo "source ~/.virtualenv/bin/activate"
