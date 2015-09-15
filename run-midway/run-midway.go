package main

import (
	"github.com/jessevdk/go-flags"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

var version = "0.1.0"

// Holds the Stats of a file
type FileStats struct {
	name     string
	fileInfo os.FileInfo
}

// Command line argument definition
var opts struct {
	Verbose        bool   `short:"v" long:"verbose" description:"Show verbose debug information"`
	ProtractorBin  string `short:"p" long:"protractor-bin" description:"path to protractor binary" env:"MIDWAY_PROTRACTOR_BIN" required:"true"`
	ProtractorConf string `short:"c" long:"protractor-conf" description:"path to protractor config" env:"MIDWAY_PROTRACTOR_CONF" required:"true"`

	Args struct {
		Path string `positional-arg-name:"PATH"`
	} `positional-args:"yes" required:"yes"`
}

// Walks the path provided and return a slice of fileStat structs
func walkpath(rootPath string) []FileStats {
	var results []FileStats

	// Walk the rootPath
	filepath.Walk(rootPath, func(path string, fileInfo os.FileInfo, err error) error {
		if err != nil {
			log.Fatal(err)
		}
		// Skip the dot file
		if path == "." {
			return nil
		}
		// Only include javascript files
		if path[len(path)-3:] == ".js" {
			// Create a new FileStats struct and add it to the list
			results = append(results, FileStats{name: path, fileInfo: fileInfo})
		}
		return nil
	})
	return results
}

/*
First define where your protractor binary is, and the config is stored
	export MIDWAY_PROTRACTOR_BIN=YOUR-ROOT/encore-cloud-ui/node_modules/protractor/bin/protractor
	export MIDWAY_PROTRACTOR_CONF=YOUR-ROOT/encore-cloud-ui/test/conf/protractor.midway.conf.js

Now you can run all the Cloud Block Storage tests like this
	$ cd YOUR-ROOT/encore-cloud-ui
	$ run-midway tests/cbs
*/
func main() {
	// Parse command line arguments
	_, err := flags.Parse(&opts)
	if err != nil {
		os.Exit(-1)
	}

	// Collect all the javascript files found in the path the user specified
	files := walkpath(opts.Args.Path)
	if len(files) == 0 {
		abs, err := filepath.Abs(opts.Args.Path)
		if err != nil {
			log.Fatal(err)
		}
		log.Fatalf("Unable to find any '.js' files in given path '%s'", abs)
	}

	// For each of the files we found, run the protractor command
	for i := range files {
		cmdArgs := []string{"--specs", files[i].name, opts.ProtractorConf}
		log.Println("==============================================")
		log.Printf("-- Running '%s'\n", files[i].name)
		log.Println("==============================================")
		log.Printf("-- Executing '%s %s'\n", opts.ProtractorBin, strings.Join(cmdArgs, " "))
		cmd := exec.Command(opts.ProtractorBin, cmdArgs...)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		err := cmd.Run()
		if err != nil {
			log.Fatal(err)
		}
	}
}
