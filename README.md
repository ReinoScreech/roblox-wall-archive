# Roblox Group Wall Archive
Welcome to the Roblox Group Wall Archive. This repository mainly contains the sources used for this service. Since group walls on Roblox are being phased out soon, this service has started up to attempt to preserve these walls for archival and memorable purposes.

## Programs
RGWA allows use of manual archiving or automated archiving. This repository alone contains a Python script that does automation process with ease by default, but other scripts can be used if necessary.

## Installation
### Releases
The releases tab will be added soon.

### Manual
Click the "Code" button at the top of the filesystem, and click ***"Download ZIP"***. Then, extract the ZIP and follow the usage instructions below.

## Usage
`automate.py`, the script that automatically does the archiving job, is a command-line script. To use it, you will need to [install Python](https://www.python.org/downloads/) if you don't already have it. Remember to check Add ***Python to PATH*** to use it in the command line, then run `pip install requests` to allow Python to use API requests.<br>
After that, you should now be ready to use the script. To use the script, you must go to the directory the script is hosted in, and run `python automate.py`. There are 4 arguments to this script. --groupid, to make requests, and --groupname, for folder names are required. The rest of the arguments are optional. For a full list of arguments, run -h or --help. 

Remember that by default, the script will run as if you are logged out of Roblox. If you want to run this script under your Roblox account, you'll have to use the --roblosecurity argument, which needs your .ROBLOSECURITY cookie. **PLEASE UNDERSTAND THE RISKS INVOLVED BEFORE YOU EVER USE THIS ARGUMENT, AS THIS COOKIE CAN ALLOW FULL ACCESS TO YOUR ACCOUNT.** When you do use this argument, it will run under your group rank, which should allow you to archive the content without issues or ratelimit problems.

## Files
Files created by the script are sorted under the Archives folder, which is automatically created if it does not already exist. Each file is inside its separate folder, with a summary of the CC-BY-ND-4.0 license, and the text file itself. Depending on the amount of content in a wall, these files may be very large in size.

## Notes
* Group walls with long group walls may take a long time to finish or not finish at all. Please remember to continuiously check the progress every few minutes.
* Due to API limits, you may experience multiple ratelimits during this process. These rate limits shouldn't take too long depending on what arguments you used when you first started the script.

## Licenses
The software provided in this repository is licensed under the [GNU General Public 3.0](LICENSE) license. (GPL)<br>
Any files this software generates are licensed under the [CC-BY-ND-4.0](FILE_LICENSE) license.

More information about these licenses are available under the [NOTICES.md](NOTICES.md)file.
