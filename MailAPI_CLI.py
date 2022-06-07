# Libraries
from signal import signal, SIGINT
from random import randint

from os import path, rmdir
from argparse import ArgumentParser
from sys import exit

# Tool modules
from MailAPIClientClass import MailCLI
from MailAPI import MailAPI
# from MailAPIClientClass import *

# Handle Ctrl+C
def ctrl_c(sig, frame):
    print("\n[x] Exiting program...")
    exit(0)

signal(SIGINT, ctrl_c)


# Argument parser setup
parser = ArgumentParser(description="""This is the CLI from the API from -> https://api.mail.tm"""
                        )

parser.add_argument("-H", "--help-advanced", action="store_true", help="Show extended help information")

# Account create/delete arguments
acc_cd = parser.add_argument_group("Account create & delete arguments")
acc_cd.add_argument("-n", "--new-email", metavar="<user>:<pass>", help="Type the user (not the @domain.com) and the password like this ")
acc_cd.add_argument("-N", "--new-email-with-file", metavar="<creeds.txt>", help="Create multiple accounts taking creadential from a file")
acc_cd.add_argument("-R", "--random", type=int, metavar='<x>', help="Create X account with random credentials")
acc_cd.add_argument("-d", "--delete", metavar="<address>", help="Delete account")
acc_cd.add_argument("-D", "--delete-with-file", metavar="<creeds.txt>", help="Delete multiple accounts taking account IDs from a file")
# Login
acc_login = parser.add_argument_group("Account login arguments")
acc_login.add_argument("-l", "--login", metavar="<user>:<pass>", help="Login into the account, this option can take as values: cache index from 0 or <address>:<passwd>")
acc_login.add_argument("-L", "--login-with-file", metavar="<creeds.txt>", help="Login into multiple accounts, should be combines with other arguments, accepts full/partinal credentials if they are in cache, not index")
# Get mails arguments
acc_mails = parser.add_argument_group("Mail query arguments, must be logged in")
acc_mails.add_argument("-i", "--inbox", action="store_true", help="Output all the emails of the logged-in account(s)")
acc_mails.add_argument("-I", "--inbox-all", action="store_true", help="Output the new emails of the logged-in account(s)")
acc_mails.add_argument("-m", "--mark", metavar="<addr>[:<pass>]:<email_id>", help="Mark an email as seen from the specified account")
acc_mails.add_argument("-M", "--mark-all", action="store_true", help="Mark all emails as seen to all the logged-in accounts")
# Cache & output
parser.add_argument("-o", "--output", metavar="<creeds.txt>", help="Path where to save credentials stored in cache as <address>:<passwd>")
parser.add_argument("--disable-cache", default=False, action="store_true", help="Prevent the program to save cache data")
parser.add_argument("--delete-cache", help="WARNING: This option will delete all the cached credential, this may affect the performance of the next requests")
parser.add_argument("-q", "--quiet", default=False, action="store_true", help="The program wont output anything to the stdout")

args = parser.parse_args()



cli = MailCLI()

# -------[ Configuration parameters ]--------
if args.help_advanced:
    cli.helpAdvanced()
    exit()

if args.disable_cache:
    cli.disableCache = True

if args.delete_cache:
    rmdir(cli.cachePath)


# -------[ Define actions ]--------
if args.new_email:
    cli.newEmailAccount((args.new_email.split(":"),))

    if not args.quiet:
        print("[+] New account created...")

elif args.new_email_with_file:
    ret = cli.withFile(args.new_email_with_file, "create")

    if not args.quiet:
        print(f"[+] Created {len(ret)} accounts...")

elif args.random:
    ret = cli.genRandomAccounts(args.random)

    if not args.quiet:
        print("[+] The following accounts have been created:")
        for i,acc in enumerate(ret):
            print(f"\t{i}.- ADDRESS: {acc[0]} - PASSWORD: {acc[1]}")

elif args.delete:
    index = cli.findInCache(args.delete)
    if index:
        accObj = cli.cacheAccounts[index]
    else:
        accObj = MailAPI()
        accObj.login(args.delete.split(":"))
    cli.deleteEmailAccount((accObj,))

    if not args.quiet:
        print("[-] Account deleted...")

elif args.delete_with_file:
    ret = cli.withFile(args.delete_with_file, "delete")

    if not args.quiet:
        print(f"[+] Deleted {len(ret)} accounts...")

elif args.login:
    cli.login(args.login)

    if not args.quiet:
        print(f"[+] Logged-in...")

elif args.login_with_file:
    ret = cli.withFile(args.login_with_file, "login")

    if not args.quiet:
        print(f"[+] Logged-in into {len(ret)} accounts...")

# -------[ Operation parameters ]-------- 
if args.inbox:
    cli.inbox(showseen=False)
elif args.inbox_all:
    cli.inbox(showseen=True)

if args.mark:
    data = args.mark.split(":")
    if len(data) == 1:      # Only id
        cli.mark(data[0]) 
    elif len(data) == 2:
        acc = cli.findInCache(data[0])
        cli.mark(eid=data[-1], acc=acc)
    else: 
        acc = MailAPI()
        acc.login(email=data[0], password=data[1])
        cli.mark(eid=data[2], acc=acc)

elif args.mark_all:
    cli.mark()

# -------[ Additional parameters ]-------- 
if args.output:
    cli.outputCache(args.output)


