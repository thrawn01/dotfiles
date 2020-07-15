# Install from https://github.com/romkatv/powerlevel10k
source /usr/local/opt/powerlevel10k/powerlevel10k.zsh-theme

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
