from cv2 import add
from MailAPI import MailAPI
from random import randint
import requests

class MailCLI:
    """
        CLI CLient for the MailAPi tool module

        This program allow handle multiple emails and deeper analysis of data
    """

    def __init__(self):

        self.cacheAccounts = []

        self.cachePath = ".accounts_cache.csv"
        self.logged_in_accounts = []

        self.loadCache()

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
            username = '_'.join([requests.get("https://random-word-api.herokuapp.com/word").json()[0] for i in range(3)])
            domain = MailAPI().queryDomain()
            password = requests.get("https://random-word-api.herokuapp.com/word").json()[0] + '_'
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
    def findInCache(self, addr):
        for i,cache in enumerate(self.cacheAccounts):
            if addr in cache.creeds['address']:
                return i
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
                    account = self.cacheAccounts[index]
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
                fd.write(f"{acc.creeds['address']}:{acc.creeds['password']}")


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

    def mark(self):
        for acc in self.logged_in_accounts:
            for email in acc.getAllEmails():
                acc.markAsSeen(email['id'])