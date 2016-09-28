
alias ssh='ssh -X'
eval `gdircolors`
alias ls='gls --color=auto'
alias gvim='~/bin/gvim-tabs.py'

# Leet Prompt
source ~/.bash_prompt

# Standard PATH things
export PATH=/usr/local/bin:/usr/local/sbin:$PATH

# NVM Stuff
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"  # This loads nvm

# GoLang Stuff
export GOPATH=$HOME/Development/go
export PATH=$HOME/bin:$GOPATH/bin:$PATH
export GO15VENDOREXPERIMENT=1

# RVM Stuff
export PATH="$PATH:$HOME/.rvm/bin" # Add RVM to PATH for scripting
[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm" # Load RVM into a shell session *as a function*

# For Selenium Firefox testing
export PATH=/Applications/Firefox.app/Contents/MacOS:$PATH

# Lunchy a better launchctl
LUNCHY_DIR=$(dirname `gem which lunchy 2> /dev/null` 2> /dev/null)/../extras
if [ -f $LUNCHY_DIR/lunchy-completion.bash ]; then
 . $LUNCHY_DIR/lunchy-completion.bash
fi

# Rackspace VPN Stuff
alias vpn-down='sudo pkill -SIGINT openconnect'
alias vpn-wat='curl -s icanhazip.com | xargs -n1 dig +short -x'
alias vpn-vidyo="sudo route -n add 174.143.224.224/27 $(netstat -nr | egrep '^default.*UGScI' | awk {'print $2'})"
alias vpn-up='sudo openconnect vpn.dfw1.rackspace.com -b'

# Because OSX
ulimit -n 8096

# For PyEnv
export VIRTUAL_ENV_DISABLE_PROMPT=1
export PYENV_ROOT=/usr/local/var/pyenv
if which pyenv > /dev/null; then
    eval "$(pyenv init -)"

    # virtualenvwrapper init
    export WORKON_HOME=/Users/thrawn/.virtualenvs
    source `pyenv which virtualenvwrapper.sh`
fi

# Case-insensitive globbing (used in pathname expansion)
shopt -s nocaseglob

# Append to the Bash history file, rather than overwriting it
shopt -s histappend

# Autocorrect typos in path names when using `cd`
shopt -s cdspell

# Enable some Bash 4 features when possible:
# * `autocd`, e.g. `**/qux` will enter `./foo/bar/baz/qux`
# * Recursive globbing, e.g. `echo **/*.txt`
for option in autocd globstar; do
    shopt -s "$option" 2> /dev/null
done

export ETCDCTL_API=3

