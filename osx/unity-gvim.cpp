#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

/***********************************************
   Run the following command from the terminal
    $ gcc unity-gvim.cpp -o gvim-unity
 ***********************************************/

// Windows
// char* gvimPath = "C:\\Program Files (x86)\\vim\\vim73\\gvim.exe";

// OSX
//const char* gvimPath = "/Applications/MacVim.app/Contents/MacOS/MacVim";

// The the gvim tabs script
const char* gvimPath = "/Users/thrawn01/bin/gvim-tabs.py";

// Tells gvim to open a new tab
const char* arg1 = "--remote-tab-silent";

int main(int argc, char** argv) {
    char* arg2 = 0;

    // 1 argument passed, only the file name
    if (argc == 2) {
        arg2 = argv[1];
    }

    // 2 arguments passed, must include a line number
    if (argc == 3) {
        arg2 = (char*)malloc(strlen(argv[1]) + strlen(argv[2]) + 2);
        sprintf(arg2, "%s:%s", argv[1], argv[2]);
    }

    //printf( "%s %s %s\n", gvimPath, arg1, arg2 );
    return execl(gvimPath, arg1, arg2, NULL);
}

