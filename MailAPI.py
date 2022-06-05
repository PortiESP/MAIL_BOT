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


# ----------------------[ Data operations ]----------------------
    # Print data
    def printAccountInfo(self):
        print("\n\t=======[ Account info ]=======")
        for k, v in self.account.items():
            print(f"\t{k} = {v}")
        print(f"\tConnected = {bool(self.queryAccount())}")

    # Save data to a file
    def saveData(self, path="saved_data.csv"):
        # Add token if its set
        if self.token: extra = f",{self.token}"
        else: extra = ''

        with open(path, "w") as fd:
            fd.write(f"{self.creeds['address']},{self.creeds['password']},{self.account['id']}{extra}")

        return 0

    # Load data from a file (CSV format: address,password,id[,token])
    def loadData(self, path="saved_data.csv", index=0):

        with open(path, "r") as fd:
            data = fd.readlines()
            
        data = data[index].split(",")

        self.creeds['address'] = data[0]
        self.creeds['password'] = data[1]
        self.account['id'] = data[2]
        if len(data) == 4:
            self.token = data[3]
            self.reqHeaders['Authorization'] = f"Bearer {self.token}"

        return 0

    # Check api response status codes
    def checkResponse(self, res, msg, valid_codes=None):
        # Default valid codes
        if not valid_codes: valid_codes = [200,201,202,203,204,205]

        if res.status_code in valid_codes:
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
    def exportEmail(self, uid, file=None):
        if not file: file = f"./exportMail_{uid}.json"

        email = self.getEmail(uid)
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
        self.account = {}

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

        return False

    # Get account token
    def getToken(self):
        res = req.post(f"{self.api_url}/token", headers=self.reqHeaders, json=self.creeds)

        if self.checkResponse(res, "[!] Token has not been sent..."):
            self.reqHeaders['Authorization'] = f"Bearer {res.json()['token']}"
            self.token = res.json()['token']
            return True

        return res.status_code

    # Get account information based on the token(user) or other account based on the id and being autheticated
    def queryAccount(self, uid=None):
        if not uid:
            res = req.get(f"{self.api_url}/me", headers=self.reqHeaders)
        else:
            res = req.get(f"{self.api_url}/accounts/{uid}", headers=self.reqHeaders)

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
    def getEmail(self, eid):
        res = req.get(f"{self.api_url}/messages/{eid}", headers=self.reqHeaders)

        if self.checkResponse(res, "[!] Error getting email by id..."):
            return res.json()
    
    # Mark email as read
    def markAsRead(self, eid):
        customHeaders = dict(self.reqHeaders)
        customHeaders['Content-Type'] = "application/merge-patch+json"
        res = req.patch(f"{self.api_url}/messages/{eid}", headers=customHeaders, json={"seen": True})

        if self.checkResponse(res, "[!] Error marking email as read..."):
            if res.json()['seen'] == True:
                return True
            
            return False

    # Delete email from the inbox
    def deleteEmailMsg(self, eid):
        res = req.delete(f"{self.api_url}/messages/{eid}", headers=self.reqHeaders)

        if self.checkResponse(res, "[!] Error deleting email..."):
            return True
        else:
            return False



    
