# Libraries
from signal import signal, SIGINT
from random import randint
from os import path, remove, path
from argparse import ArgumentParser
from sys import exit, argv
from requests import get

# Tool modules
from API_module.MailAPI import MailAPI

# Handle Ctrl+C
def ctrl_c(sig, frame):
    print("\n[x] Exiting program...")
    exit(0)

signal(SIGINT, ctrl_c)

# ===========================================[ CLI tool Object ]===========================================
class MailCLI:
    """
        CLI CLient for the MailAPi tool module

        This program allow handle multiple emails and deeper analysis of data
    """

    def __init__(self):

        self.cacheAccounts = []

        self.cachePath = ".accounts_cache.csv"
        self.logged_in_accounts = []
        self.disableCache = False

        if path.exists(self.cachePath):
            self.loadCache()
        else:
            self.saveCache()

    # Receives:  credentials=(list tuples (address,passwd))
    def newEmailAccount(self, credentials):
        temp = []

        for cred in credentials:
            newAccount = MailAPI()
            newAccount.createAccount(cred[0], cred[1])
            newAccount.login()
            temp.append(newAccount)

        # Add temp accounts to cache
        [self.cacheAccounts.append(acc) for acc in temp]

        self.saveCache()

        # Return new accounts
        return temp
        
    # Delete accounts from a list of MailAPI objects and return the ones it couldnt delete
    def deleteEmailAccount(self, accounts):
        not_deleted = []
        for acc in list(accounts):
            acc.deleteAccount()
            if acc.queryAccount() != 'deleted':
                not_deleted.append(acc)
            else:
                self.cacheAccounts.pop(self.cacheAccounts.index(acc))
        
        self.saveCache()



        return not_deleted

    def saveCache(self):
        
        if self.disableCache:
            return False

        with open(self.cachePath, 'w') as fd:
            for line in self.cacheAccounts:
                fd.write(f"{line.creeds['address']},{line.creeds['password']},{line.account['id']},{line.token}\n")

    def loadCache(self):

        with open(self.cachePath, 'r') as fd:
            cachedAccounts = fd.readlines()

        for acc in cachedAccounts:
            acc = acc.strip().split(',')
            new = MailAPI()
            new.creeds = {"address": acc[0], "password": acc[1]}
            new.account['id'] = acc[2]
            new.token = acc[3]
            new.reqHeaders['Authorization'] = f"bearer {acc[3]}"

            self.cacheAccounts.append(new)

            
    def genRandomAccounts(self, n=1):

        temp = []

        for i in range(n):
            username = '_'.join([get("https://random-word-api.herokuapp.com/word").json()[0] for i in range(3)])
            domain = MailAPI().queryDomain()
            password = get("https://random-word-api.herokuapp.com/word").json()[0] + '_'
            # Generate password
            for i in range(randint(4,6)): 
                rand = randint(0,2)
                if rand == 0: password += chr(randint(65, 90))
                elif rand == 1: password += chr(randint(97, 122))
                else: password += chr(randint(48, 57))

            temp.append((f"{username}@{domain}", password))

        # Create email
        self.newEmailAccount(temp)
        # Accounts are added to cache in the newEmailAccount() funtion

        return temp

    # Read file lines with credentials
    def withFile(self, path, operation):
        with open(path, 'r') as fd:
            data = fd.readlines()

        accList = []

        for acc in data:
            if acc != '\n':
                address = acc.strip().split(":")[0]
                if len(acc.strip().split(":")) == 2:
                    password = acc.strip().split(":")[1]
                accList.append((address, password))
            
        if operation == 'create':
            self.newEmailAccount(accList)
        elif operation == "delete":
            # Look in list element cache
            for acc in accList:
                index = self.findInCache(acc[0])
                # If element is in cache
                if index: 
                    self.deleteEmailAccount((self.cacheAccounts[index],))
                    break
                # If element is not in cache
                else:
                    try:
                        api = MailAPI()
                        api.login(email=acc[0], password=acc[1])
                        api.deleteAccount()
                    except Exception as e:
                        pass

        elif operation == "login":
            for acc in accList:
                self.login(":".join(acc))
                    
        return accList
                
    # Find address in object list
    def findInCache(self, filter):
        
        for i,cache in enumerate(self.cacheAccounts):
            if filter in cache.creeds['address'] or filter in cache.account['id']:
                return self.cacheAccounts[i]
        else:
            return None


    def login(self, account):

        # Defining account MailAPI object
        if account == "cache":
            self.logged_in_accounts = self.cacheAccounts
        else:
            if account.isnumeric() :
                account = self.cacheAccounts[int(account)]
            else:
                data = account.split(":")
                index = self.findInCache(data[0])
                if index:
                    account = index
                else:
                    account = MailAPI()
                    account.login(email=data[0], password=data[1])
            
            self.logged_in_accounts.append(account)

            if account not in self.cacheAccounts:
                self.cacheAccounts.append(account)
                self.saveCache()
            
            return account
        
        return self.logged_in_accounts


    # Output format <address>:<passwd>
    def outputCache(self, path):
        with open(path, 'w') as fd:
            for acc in self.cacheAccounts:
                fd.write(f"{acc.creeds['address']}:{acc.creeds['password']}\n")


    # Print the inbox of all the logged-in accounts
    def inbox(self, showseen=True):
        for acc in self.logged_in_accounts:
            print("""
         ______________________________________________________________________________________________
        /                                                                                              \\
        |  Emails from: %-50s                             |
        \\______________________________________________________________________________________________/
            """ % acc.creeds['address'])
            acc.printEmailsList(seen=showseen)

    def mark(self, eid=None, acc=None):
        if eid:
            acc.markAsSeen(eid)

            return

        for acc in self.logged_in_accounts:
            for email in acc.getAllEmails():
                acc.markAsSeen(email['id'])


    def helpAdvanced(self):
        print(f"""
        
        usage: {path.basename(argv[0])} [-h] [-H] [-n <user>:<pass>] [-N <creeds.txt>] [-R <x>] [-d <account id>] [-D <creeds.txt>] [-l <user>:<pass>] [-L <creeds.txt>] [-i] [-I] [-m] [-o <creeds.txt>] [-q]

        This is the CLI from the API from -> https://api.mail.tm

        The main usage for this too is for manitoring multiple accounts simultaneously.

        The API has limited the requests to 8 per second so we cant go any faster than that, this is why it is recommended to use cache for credentials,
        this will prevent to make unnecesary requests to the API

        Optional arguments:
            Help:
                -h, --help            Show default help menu
                -H, --help-advanced   Show this help menu
                -q, --quiet           The program wont output anything to the stdout

            Output:
                # This is where the credentials stored in cache will be stored, format: <address>:<pass>
                -o <creeds.txt>, --output <creeds.txt>

            Cache:
                # Prevent the program to save cache data
                --disable-cache

        Account create & delete arguments:

            Create users:
                # Create a single user by providing an email (with a valid domain, Ex: @knowledgemd.com) and a password
                -n <user>:<pass>, --new-email <user>:<pass>
                                        
                # Create multiple users based on the credentials on a file, format: <address>:<pass>
                -N <creeds.txt>, --new-email-with-file <creeds.txt>
                
                # Create some number of valid credentials with random data, the credentials are formed the following way
                # Address: Takes 3 random words and then the domain, <word>_<word>_<word>@<domain>.com
                # Password: Takes one random word and then a random amount of alphanumeric characters
                -R <x>, --random <x>  Create X account with random credentials

            Delete users
                [*] Both options support full address or partial addresses

                # Delete account based on the address, must be logged in with '-l' or '-L' or credential being stored in cache
                # This option also allows passing the index in cache to select an account, start from 0
                -d <account id>, --delete <account id>

                # Delete all accounts based on the addresses of a file
                # *Index selection not supported
                -D <creeds.txt>, --delete-with-file <creeds.txt>
                                    

        Account login arguments:
            # Login into the account, this option can take as values: 
                # cache index from 0 
                # Address, if credentials are in cache
                # <address>:<passwd>
                # If we type 'cache' (without the collons), we will choose to loggin into all the accounts in cache
            -l <user>:<pass>, --login <user>:<pass>

            # Login into multiple accounts, should be combines with other arguments
            # Accepts full/partinal credentials if they are in cache
            # Dont accept cache index
            -L <creeds.txt>, --login-with-file <creeds.txt>

        Mail query arguments, must be logged in:
            # Output the NEW (not marked as seen) emails of the logged-in account(s)
            -i, --inbox
            
            # Output ALL the emails of the logged-in account(s)
            -I, --inbox-all
            
            # Mark an email as seen from the specified account, we can use partial email_id (just the first characters)
            # We can use this argument in 3 diferent ways
                # Pass only the email_id: This will take the fist account from the logged in ones
                # Pass an address and an email_id: This will look for the accout in cache to find te credentials, we can use partial emails
                # Pass the address, password and email_id: This way doesnt need to have credentials in cache or use logged-in flags but will
                        be slower since it will have to login with that credentials to retrieve a token 
            -m <addr>[:<pass>]:<email_id>, --mark <addr>[:<pass>]:<email_id>
            
            # Mark all emails as seen to all the logged-in accounts
            -M, --mark-all

        
        """)



# ===========================================[ Argument parser ]===========================================

# Argument parser setup
parser = ArgumentParser(description="This is the CLI from the API from -> https://api.mail.tm")

parser.add_argument("-H", "--help-advanced", action="store_true", help="Show extended help information")
parser.add_argument("--domains", action="store_true", help="Show available domains for the addresses")

# Account create/delete arguments
acc_cd = parser.add_argument_group("Account create & delete arguments")
acc_cd.add_argument("-n", "--new-email", metavar="<address>:<pass>", help="Type the address and the password like this ")
acc_cd.add_argument("-N", "--new-email-with-file", metavar="<creeds.txt>", help="Create multiple accounts taking creadential from a file")
acc_cd.add_argument("-R", "--random", type=int, metavar='<x>', help="Create X account with random credentials")
acc_cd.add_argument("-d", "--delete", metavar="<address>", help="Delete account")
acc_cd.add_argument("-D", "--delete-with-file", metavar="<creeds.txt>", help="Delete multiple accounts taking account IDs from a file")
# Login
acc_login = parser.add_argument_group("Account login arguments")
acc_login.add_argument("-l", "--login", metavar="<address>:<pass>", help="Login into the account, this option can take as values: cache index from 0 or <address>:<passwd>")
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
parser.add_argument("--delete-cache", action="store_true", help="WARNING: This option will delete all the cached credential, this may affect the performance of the next requests")
parser.add_argument("-q", "--quiet", default=False, action="store_true", help="The program wont output anything to the stdout")

args = parser.parse_args()



cli = MailCLI()

# -------[ Configuration parameters ]--------
if args.help_advanced:
    cli.helpAdvanced()
    exit()

if args.disable_cache:
    cli.disableCache = True
    print("[!] Cache disabled...")

if args.delete_cache:
    remove(cli.cachePath)
    print("[-] Cache deleted...")


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
    
elif args.domains:
    print(MailAPI().queryDomain())

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


