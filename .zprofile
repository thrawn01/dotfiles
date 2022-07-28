# Install from https://github.com/romkatv/powerlevel10k
source /opt/homebrew/opt/powerlevel10k/powerlevel10k.zsh-theme

# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# Standard PATH things
export PATH=/usr/local/bin:/usr/local/sbin:$PATH

# Etcd Stuff
export ETCDCTL_API=3
export ETCDCTL_ENDPOINTS=localhost:2379

# Eventbus stuff
export ETCD_ENDPOINT=http://localhost:2379
export EVENTBUS_ENDPOINT=localhost:19091
export KAFKA_PIXY_ENDPOINT=localhost:19091

# === SEE 1Password for API KEYS ===

# mailgun-go stuff for runscope and travis ci testing
export MG_API_KEY=
export MG_DOMAIN=
export MG_URL=https://api.mailgun.net/v3

# mailgun-go stuff for mg.thrawn01.org
export MG_API_KEY=
export MG_DOMAIN=
export MG_URL=https://api.mailgun.net/v3

export SLACK_TOKEN=

# Colorize ls files (Goto https://geoff.greer.fm/lscolors/ to change colors)
export CLICOLOR=1
export LSCOLORS="exfxfxdxcxegedabagacad"
alias ls='ls -G'

export HOMEBREW_PREFIX="/opt/homebrew";
export HOMEBREW_CELLAR="/opt/homebrew/Cellar";
export HOMEBREW_REPOSITORY="/opt/homebrew";
export MANPATH="/opt/homebrew/share/man${MANPATH+:$MANPATH}:";
export INFOPATH="/opt/homebrew/share/info:${INFOPATH:-}";

# Added by Toolbox App
export PATH="$PATH:/Users/thrawn/Library/Application Support/JetBrains/Toolbox/scripts"

# Brew
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin${PATH+:$PATH}";

# Python
export PATH="/opt/homebrew/opt/python@3.9/libexec/bin${PATH+:$PATH}";

# Golang
export GOPRIVATE=github.com/mailgun
export GOPATH=/Users/thrawn/Development/go
export GOROOT=/usr/local/go
export GOBIN=$GOPATH/bin
export PATH=$GOBIN:$PATH

# # Mailgun Stuff
alias ssh='rewrite-args ssh -X'

# Home bin
export PATH=/Users/thrawn/bin:$PATH
