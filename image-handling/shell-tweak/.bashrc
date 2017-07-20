#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return
#############################

color="--color=auto" # used in .aliases

source ~/.aliases
source ~/.exports
source ~/.bash-functions.sh

#color man
export LESS_TERMCAP_mb=$(printf '\e[01;31m') # enter blinking mode - red
export LESS_TERMCAP_md=$(printf '\e[01;35m') # enter double-bright mode - bold, magenta
export LESS_TERMCAP_me=$(printf '\e[0m') # turn off all appearance modes (mb, md, so, us)
export LESS_TERMCAP_se=$(printf '\e[0m') # leave standout mode    
export LESS_TERMCAP_so=$(printf '\e[01;33m') # enter standout mode - yellow
export LESS_TERMCAP_ue=$(printf '\e[0m') # leave underline mode
export LESS_TERMCAP_us=$(printf '\e[04;36m') # enter underline mode - cyan

shopt -s autocd
shopt -s extglob
shopt -s checkwinsize

GREEN="\[$(tput setaf 46)\]"
BLUE="\[$(tput setaf 26)\]"
RED="\[$(tput setaf 196)\]"
RESET="\[$(tput sgr0)\]"

exitstatus()
{
    if [[ $? == 0 ]]; then
        echo -en '\033[1;32m'":)"'\E(B\E[m'
    else
        echo -en '\033[1;31m'":("'\E(B\E[m'
    fi
}

if [[ $USER == 'root' ]]; then
	ucolor=${RED}
	last="#"
else 
	ucolor=${GREEN}
	last="$"
fi

PS1='$(exitstatus) '"$ucolor\u\[\e[m\]\[\e[m\]@$BLUE\h\[\e[m\]:$GREEN\W\[\e[m\]$last " 
# PS1='[\u@\h \W]\$ '