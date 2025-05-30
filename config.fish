# Fish shell configuration adapted from ~/.zshrc

# Brew
fish_add_path /opt/homebrew/bin
fish_add_path /opt/homebrew/sbin

# Python
fish_add_path /opt/homebrew/opt/python@3/libexec/bin

#### Golang #####
# Uncomment if needed:
# set -gx GOPRIVATE github.com/mailgun

# The GOROOT directory for the 'go' installation which contains the Go toolchain
# and standard library.
set -gx GOROOT /Users/thrawn/go/go1.24.1

# The GOPATH variable is used for the following purposes
# - The 'go install' command installs binaries to $GOBIN, which defaults to $GOPATH/bin.
# - The 'go get' command caches downloaded modules in $GOMODCACHE, which defaults to $GOPATH/pkg/mod.
# - The 'go get' command caches downloaded checksum database state in $GOPATH/pkg/sumdb.
set -gx GOPATH /Users/thrawn/go

# Place both GOROOT and GOPATH in the PATH
fish_add_path $GOROOT/bin
fish_add_path $GOPATH/bin

# Home bin
fish_add_path /Users/thrawn/bin

# Zig
set -gx ZIGPATH /Users/thrawn/zig
fish_add_path $ZIGPATH

# Google Cloud SDK
if test -f '/Users/thrawn/Development/google-cloud-sdk/path.fish.inc'
    source '/Users/thrawn/Development/google-cloud-sdk/path.fish.inc'
end

# NVM support for fish shell
function nvm
    bash -c "source ~/.nvm/nvm.sh; nvm $argv"
end

# Set up node path from current nvm version
if test -f ~/.nvm/nvm.sh
    set -gx NVM_DIR ~/.nvm
    set -l node_version (bash -c "source ~/.nvm/nvm.sh; nvm current 2>/dev/null" | string trim)
    if test -n "$node_version"; and test "$node_version" != "system"
        set -gx PATH ~/.nvm/versions/node/$node_version/bin $PATH
    end
end

# Fix ls colors - use GNU ls with custom LS_COLORS
set -gx LS_COLORS 'ex=01;32:di=01;34:ln=01;36:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:*.tar=01;31'
alias ls 'gls --color=auto'

set -U tide_right_prompt_items cmd_duration
