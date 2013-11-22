rm -rf ~/.virtualenv-setup 2> /dev/null
mkdir ~/.virtualenv-setup
cd ~/.virtualenv-setup

echo " -- Fetching virtualenv.py"
curl -L -o virtualenv.py https://raw.github.com/pypa/virtualenv/master/virtualenv.py

echo " -- Fetching git-pip.py"
curl -L https://raw.github.com/pypa/pip/master/contrib/get-pip.py

echo " -- Fetching ez_setup.py"
curl -L -o ez_setup.py https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py

echo " -- Create the virtualenv"
python virtualenv.py .virtualenv

echo " -- Activate the virtualenv"
source .virtualenv/bin/activate

echo " -- Run ez_setup.py"
python ez_setup.py

echo " -- Run get-pip.py"
python get-pip.py
