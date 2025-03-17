#! env python3

from subprocess import call, check_output
from os import path
import os
import sys
import re


def get_user_input(msg, default=None, validate=None):
    while True:
        choice = input(msg)

        # Did we pass in a default
        if default:
            if choice == "":
                return default

        # Did we ask to validate the input
        if not validate:
            return choice
        if re.search(validate, choice):
            return choice
        print("Invalid entry, Try again")


def yes_no(msg, default=None):
    while True:
        result = get_user_input(msg, default)
        if re.match("^(Y|y)$", result):
            return True
        if re.match("^(N|n)$", result):
            return False


def rename(file, rename_list):
    for old, new in rename_list.items():
        # print ("Rename: '%s' '%s'" % (old, new))
        if file == old:
            return new
    return file


def skipable(file, skip_regex):
    for regex in skip_regex:
        # print ("regex: '%s' '%s'" % (regex, file))
        if re.search(regex, file):
            return True
    return False


def search(file, needle):
    try:
        with open(file, 'r') as haystack:
            for line in haystack:
                if re.search(needle, line):
                    return True
        return False
    except IOError as e:
        return False


def append(target, source):
    # If the target file already has the appends
    if search(target, '# dev-tools'):
        return

    with open(source, 'r') as src:
        with open(target, "a") as dest:
            for line in src:
                dest.write(line)


def edit(file, regex, replace):
    output = []
    found = False
    replace = "%s\n" % replace

    # Open the file and search for the regex
    with open(file, 'r') as src:
        for line in src:
            if re.search(regex, line):
                output.append(replace)
                found = True
            else:
                output.append(line)

    # If the regex was found in the file, write out the new file
    if found:
        with open(file, 'w') as src:
            src.truncate()
            for line in output:
                src.write(line)


if __name__ == "__main__":

    # Get my name
    prog_name = sys.argv[0].lstrip("./")

    # Ensure we don't get run on shared user accounts!
    user = os.environ.get('USER', '')
    if user != 'thrawn':
        question = "\n-- Current user '%s' != 'thrawn' Continue (Y/N) ? " % user
        if not yes_no(question, "Y"):
            sys.exit(-1)

    # Default install directory to ~/bin
    home_dir = os.environ.get('HOME', '')
    if home_dir == '':
        print("-- Could not determine your home directory")
        sys.exit(-1)

    bin_path = os.path.join(home_dir, "bin")

    # If the user supplied a dest directory, use that instead
    if len(sys.argv) > 1:
        print("-- Installing into %s" % sys.argv[1])
        bin_path = sys.argv[1]

    if not path.exists(bin_path):
        question = "\n-- '%s' doesn't exist, create it (Y/N) ? " % bin_path
        if not yes_no(question, "Y"):
            sys.exit(-1)
        os.makedirs(bin_path)

    # Get a listing of all the programs in the bin/ directory
    list = os.listdir(os.getcwd() + "/bin")
    for file_name in list:

        # Skip some files
        if skipable(file_name, ['.swp', '^\.']):
            continue

        cmd = "ln -s %s/%s %s/%s" % (os.getcwd() + "/bin",
                                     file_name, bin_path, file_name)
        print(" -- ", cmd)
        call(cmd, shell=True)

    # Copy the dotfiles
    cwd = os.getcwd()
    call('mkdir -p ~/.vim', shell=True)
    call('mkdir -p ~/.vimswap', shell=True)
    call('cd vim; tar -vcf - . | $( cd ~/.vim; tar -vxf - )', shell=True)
    call('ln -s %s/.vimrc ~/.vimrc' % cwd, shell=True)
    call('ln -s %s/.gvimrc ~/.gvimrc' % cwd, shell=True)

    # SSH
    call('mkdir -p ~/.ssh', shell=True)
    call('cd ssh; cp config ~/.ssh', shell=True)
    call('chmod u+rwx,go-rwx ~/.ssh', shell=True)

    if path.exists("/Library"):
        call('chown -R %s:staff ~/.ssh' % user, shell=True)
    else:
        call('chown %s.%s -R ~/.ssh' % (user, user), shell=True)

    call('cp .bash_profile ~/.bash_profile', shell=True)
    call('cp .bash_prompt ~/.bash_prompt', shell=True)

    call('git config --global color.diff auto', shell=True)
    call('git config --global color.status auto', shell=True)
    call('git config --global color.branch auto', shell=True)
    call('git config --global user.name "Derrick J. Wippler"', shell=True)
    call('git config --global user.email thrawn01@gmail.com', shell=True)
    call('git config --global push.default current', shell=True)
    # Add this so go mod will pull without `unknown revision` errors
    call('git config --global url."git@github.com:".insteadOf https://github.com/', shell=True)

    bashprompt = os.path.join(home_dir, ".bash_prompt")
    bashrc = os.path.join(home_dir, ".bash_profile")
    # Setup .bashrc
    if path.exists("/Library"):
        # OSX
        os.chdir(check_output(["git", "--exec-path"]).rstrip(b'\n'))
        os.system('sudo ln -s %s/bin/git-* .' % home_dir)
        os.chdir(cwd)
        print("--- OSX only ---")
        print("-- brew install coreutils && brew install git && brew doctor")
        print("-- Fix the paths by modifying /etc/paths")

    # print("\n\n")
    # print("Choose a color for the bash prompt hostname")
    # print(" 1 = Red, 2 = Green, 3 = Yellow, 4 = Blue ")
    # print(" 5 = Pink, 6 = Cyan, 7 = White, 8 = Black ")
    # color = get_user_input("Color (default=4) > ", '3', '^\d$')
    # edit(bashprompt, "^hostStyle=", "hostStyle=\"\e[1;3%sm\";" % color)

    # print("Choose a name to report in iterm tabs")
    # tab = get_user_input("Tab (default=\h) > ", '\h')
    # edit(bashrc, "^title=", "title='\\033]0;%s\\007'" % tab)
