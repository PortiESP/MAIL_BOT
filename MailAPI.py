import requests as req
import json, time


class MailAPI:

    def __init__(self):
        self.api_url = "https://api.mail.tm"

        self.reqHeaders = {"accept": "application/json", "Content-Type": "application/json"}

        self.creeds = {
            "address": None,
            "password": None
        }
        self.account = {} 
        self.token = None

        self.emailsList = []


# ----------------------[ Data operations ]----------------------
    # Print data
    def printAccountInfo(self):
        print("\n=======[ Account info ]=======")
        for k, v in self.account.items():
            print(f"\t{k} = {v}")
        print(f"\tConnected = {bool(self.queryAccount(me=True))}")

    # Save data to a file
    def saveData(self):
    # Save data to a file
        with open("saved_data.csv", "w") as fd:
            fd.write(f"{self.account['address']},{self.creeds['password']},{self.account['id']}")

        return 0

    # Load data from a file (CSV format: address,password,id)
    def loadData(self, path="saved_data.csv"):
        with open(path, "r") as fd:
            data = fd.read().split(",")

            self.creeds['email'] = data[0]
            self.creeds['password'] = data[1]
            self.account['id'] = data[2]

        return 0

    # Check api response status codes
    def checkResponse(self, res, msg):
        if res.status_code <= 201:
            return res.status_code
        elif res.status_code >= 400:
            raise Exception(msg, f"STATUS_CODE={res.status_code}; CONTENT={res.content}")

        return False

    # Print emails
    def printEmailsList(self, emailList=None):
        if not emailList: emailList = self.getAllEmails()

        print(f"\n\t/========================================[ Emails: {len(emailList)} ]=========================================\\")
        for i, email in enumerate(emailList):
            # Print headers
            print("""
        +==============================================================================================+
        | From: %-86s |
        | To: %-86s   |
        +----------------------------------------------------------------------------------------------+
        | Subject: %-82s  |
        +----------------------------------------------------------------------------------------------+
        | Message:                                                                                     |""" % (
                email['from']['address'], 
                email['to'][0]['address'],
                email['subject']
            ))

            content = self.getEmail(email['id'])['text']
            for i, line in enumerate(content.split('\n')):
                print(f"""\
        |   %-90s |""" % line)
            print("""\
        +----------------------------------------------------------------------------------------------+
        | Email ID: %-80s   |""" % email['id'])
            print("\t+==============================================================================================+")
    
    # Export all email in JSON format to a file
    def exportAllEmails(self, file=f"./export_{time.time()}.json"):
        emails = [ self.getEmail(email['id']) for email in self.getAllEmails()]
        emailsFormated = json.dumps(emails, indent=4)

        with open(file, 'w') as fd:
            fd.write(emailsFormated)
            
        return emailsFormated

    # Export a single mail in JSON format to a file
    def exportEmail(self, _id, file=None):
        if not file: file = f"./exportMail_{_id}.json"

        email = self.getEmail(_id)
        emailFormated = json.dumps(email, indent=4)

        with open(file, 'w') as fd:
            fd.write(emailFormated)
            
        return emailFormated

# ----------------------[ API Queries ]----------------------
    # Query API for a domain
    def queryDomain(self=None, index=1):
        if not self: url = "https://api.mail.tm"
        else: url = self.api_url
        res = req.get(f"{url}/domains", params={"page": index})

        if res.ok:
            return res.json()['hydra:member'][0]['domain']       

    # Create account
    def createAccount(self, email, password):
        self.creeds = {
            "address": email, 
            "password": password
        }

        res = req.post(f"{self.api_url}/accounts", headers=self.reqHeaders, json=self.creeds)
        if self.checkResponse(res, "[!] Address is already in use..."):
            resJSON = res.json()
            self.account['id'] = resJSON['id']
            return 0

        return 1

    # Fill class data 
    def login(self, email=None, password=None):
        
        if not email: email = self.creeds['address']
        if not password: password = self.creeds['password']

        self.creeds = {
            "address": email,
            "password": password
        }

        if self.getToken():
            self.syncAccountInfo()
            return True
        
        return False

    # Delete account
    def deleteAccount(self):
        res = req.delete(f"{self.api_url}/accounts/{self.account['id']}", headers=self.reqHeaders)

        if self.checkResponse(res, "[!] Account not found, nothing deleted...") == 204:
            return True

    # Get account token
    def getToken(self):
        res = req.post(f"{self.api_url}/token", headers=self.reqHeaders, json=self.creeds)

        if self.checkResponse(res, "[!] Token has not been sent..."):
            self.reqHeaders['Authorization'] = f"Bearer {res.json()['token']}"
            self.token = res.json()['token']
            return True

        return res.status_code

    # Get account information based on the token(user) or other account based on the id and being autheticated
    def queryAccount(self, me=False, _id=None):
        if not _id: _id = self.account['id']
        if me:
            res = req.get(f"{self.api_url}/me", headers=self.reqHeaders)
        else:
            res = req.get(f"{self.api_url}/accounts/{_id}", headers=self.reqHeaders)

        if self.checkResponse(res, "[!] Account not found..."):
            return res.json()

    # Update the data of 'self.account'
    def syncAccountInfo(self):
        res = req.get(f"{self.api_url}/me", headers=self.reqHeaders)

        if self.checkResponse(res, "[!] Account not found..."):
            self.account = res.json()

    # Make generic queries for any endpoint
    def genericQuery(self, endpoint, method='GET', params=None, body=None, json=True):
        if method == 'GET':
            return req.get(f"{self.api_url}/{endpoint}", headers=self.reqHeaders, params=params)
            
        elif method == 'POST':
            if json:
                return req.post(f"{self.api_url}/{endpoint}", headers=self.reqHeaders, body=body)
            else:
                return req.post(f"{self.api_url}/{endpoint}", headers=self.reqHeaders, json=body)

        elif method == 'DELETE':
            if json:
                return req.delete(f"{self.api_url}/{endpoint}", headers=self.reqHeaders, body=body)
            else:
                return req.delete(f"{self.api_url}/{endpoint}", headers=self.reqHeaders, json=body)

    # Gets all the emails received
    def getAllEmails(self):
        res = req.get(f"{self.api_url}/messages", headers=self.reqHeaders)

        if self.checkResponse(res, "[!] Error getting emails..."):
            return res.json()

    # Get specific email by id, retrieves more data except 'intro' turns into 'text'
    def getEmail(self, _id):
        res = req.get(f"{self.api_url}/messages/{_id}", headers=self.reqHeaders)

        if self.checkResponse(res, "[!] Error getting email by id..."):
            return res.json()
    
    # Mark email as read
    def markAsRead(self, _id):
        customHeaders = dict(self.reqHeaders)
        customHeaders['Content-Type'] = "application/merge-patch+json"
        res = req.patch(f"{self.api_url}/messages/{_id}", headers=customHeaders, json={"seen": True})

        if self.checkResponse(res, "[!] Error marking email as read..."):
            if res.json()['seen'] == True:
                return True
            
            return False

    # Delete email from the inbox
    def deleteEmailMsg(self, _id):
        res = req.delete(f"{self.api_url}/messages/{_id}", headers=self.reqHeaders)

        if self.checkResponse(res, "[!] Error deleting email..."):
            return True
        else:
            return False



        



# ================================[ Main Program ]================================
if __name__  == '__main__':

    print(MailAPI.queryDomain())

    bot = MailAPI()
    
    # bot.createAccount("pruebas16@knowledgemd.com", "1234")
    bot.login("pruebas16@knowledgemd.com", "1234")
    # bot.loadData()

    # bot.getToken()
    # bot.reqHeaders['Authorization'] = 'bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE2NTQyODU3MTUsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJ1c2VybmFtZSI6ImJ1cnB0ZXN0MUBrbm93bGVkZ2VtZC5jb20iLCJpZCI6IjYyOWE2NTg2YWU2MmI2YmRkODBjOWYzNyIsIm1lcmN1cmUiOnsic3Vic2NyaWJlIjpbIi9hY2NvdW50cy82MjlhNjU4NmFlNjJiNmJkZDgwYzlmMzciXX19.Zs656VZcPK5AmdtmKsn0KEHfMtDKro69nb__MKrWAixVbe5RdOtdUM0OfLc-BLDeFibuIZi0NbltuED4ftGVOw'

    # bot.saveData()
    # print(bot.genericQuery("accounts/629a61ba1902c6d08b04a847", method="DELETE"))

    bot.syncAccountInfo()
    bot.printAccountInfo()
    # print(bot.queryAccount(me=True))
    # print(bot.markAsRead("629a67b52083143007c8570d"))
    # print(bot.getEmail("629a72ca3f55f90a8e67deba"))
    # bot.printEmailsList()

    # print(bot.exportAllEmails())
    # print(bot.exportEmail("629a72ca3f55f90a8e67deba"))
    
