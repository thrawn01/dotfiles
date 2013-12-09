# ---------------------
# dev-tools/bashrc
# ---------------------

export PATH="$PATH:~/bin"
alias gvim='~/bin/gvim-tabs.py'

function current_branch() {
    git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/'
}

# Leet Promptness
C0="\[\e[0m\]"
C1="\[\e[1;30m\]" # <- subdued color
C2="\[\e[1;37m\]" # <- regular color
C3="\[\e[1;34m\]" # <- hostname color
C4="\[\e[1;34m\]" # <- seperator color (..[ ]..)
TAB='\033]0;\h\007'
PROMPT='>'
export PS1="$TAB$C3$C4..( $C2\u$C1@$C3\h$C1 ($C2\$(current_branch)$C1): $C2\w$C1$C1 : $C2   $C1 $C4)..
$C3$C2$PROMPT$C1$PROMPT$C0 "

export VIRTUAL_ENV_DISABLE_PROMPT=1
source ~/.virtualenv/bin/activate 2> /dev/null
