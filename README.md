
# The MailAPI Documentation

> This the documentation for the tool MailAPI
> 
> This tool works over [Mail.tm](https://api.mail.tm/) API

-----------------------------------------------
## Module usage

### Connect
First instance the class

```python
mail = MailAPI()
```
*Note that we have instanced the class as `mail`, this variable will be used in the following examples*  

If we **dont** have an account or we want to create a new one

```python
domain = MailAPI.queryDomain()
mail.createAccount(f"example@{domain}", "password123")
```

Then you will have to login to setup the module attributes and request the JTW token, this step will use the credentials from *`self.creeds`* to retrieve the token so you must add valid credentials there, credentials are automaticaly filled when the following methods are called
* `createAccount()`
* `loadData()`
* `login(*email, password*)`  (*passing the credentias as  parameters*)

```python
mail.login(f"example@{domain}", "password123")
```
*In the example above if we had used the `createAccount()` method before we could have not passed the credential as parameters, but we have passed as an example for the ones that have already created one in a previous execution*

### Save & Load credentials

We can save our credentials in a file to use them later, we can save our current credentials by:

```python
mail.saveData()
```

Then we can load our credentials like this:

```python
mail.loadData()
```
> This method only loads the credentials but not the token, to execute queries we will have to call `mail.login()` without parameters to query for a token, and now we are able to query the API

### Query

Module calls examples

```python
# This is how we print all the emails in a formated way
mail.printEmailslist()
# This is how we get evary email basic data like: from, id, suject, etc...
mail.getAllEmails()

# Get most recent email ID
mail.getAllEmails()[0]['id']

# Add custom headers
mail.reqHeaders['User-Agent'] = "Mozilla 5.0 ..."

# Update account information
mail.syncAccountInfo()

# Query for specific email
mail.getEmail("568g72cb3f567f90a34lgdeba")

# Export all emails
mail.exportAllEmails()
```

--------------------------------------------------------

## API objects

### Account object
 ```json
 {
  "@context": "string",
  "@id": "string",
  "@type": "string",
  "id": "string",
  "address": "user@example.com",
  "quota": 0,
  "used": 0,
  "isDisabled": true,
  "isDeleted": true,
  "createdAt": "2022-04-01T00:00:00.000Z",
  "updatedAt": "2022-04-01T00:00:00.000Z"
 } 
 ```

### Email object (*from `getEmail()`*)

```json
{
  "@context": "string",
  "@id": "string",
  "@type": "string",
  "id": "string",
  "accountId": "string",
  "msgid": "string",
    "from": {
        "name": "string",
      "address": "string"
  },
  "to": [
        {
            "name": "string",
            "address": "string"
        }
    ],
  "cc": [
    "string"
  ],
  "bcc": [
    "string"
  ],
  "subject": "string",
  "seen": true,
  "flagged": true,
  "isDeleted": true,
  "verifications": [
    "string"
  ],
  "retention": true,
  "retentionDate": "2022-04-01T00:00:00.000Z",
  "text": "string",
  "html": [
    "string"
  ],
  "hasAttachments": true,
  "attachments": [
    {
      "id": "string",
      "filename": "string",
      "contentType": "string",
      "disposition": "string",
      "transferEncoding": "string",
      "related": true,
      "size": 0,
      "downloadUrl": "string"
    }
  ],
  "size": 0,
  "downloadUrl": "string",
  "createdAt": "2022-04-01T00:00:00.000Z",
  "updatedAt": "2022-04-01T00:00:00.000Z"
}
```

### Email object (*from ``getAllEmails()``*)

```json
{
  "hydra:member": [
    {
      "@id": "string",
      "@type": "string",
      "@context": "string",
      "id": "string",
      "accountId": "string",
      "msgid": "string",
      "from": {
          "name": "string",
          "address": "string"
      },
      "to": [
        {
            "name": "string",
            "address": "string"
        }
      ],
      "subject": "string",
      "intro": "string",
      "seen": true,
      "isDeleted": true,
      "hasAttachments": true,
      "size": 0,
      "downloadUrl": "string",
      "createdAt": "2022-04-01T00:00:00.000Z",
      "updatedAt": "2022-04-01T00:00:00.000Z"
    }
  ],
  "hydra:totalItems": 0,
  "hydra:view": {
    "@id": "string",
    "@type": "string",
    "hydra:first": "string",
    "hydra:last": "string",
    "hydra:previous": "string",
    "hydra:next": "string"
  },
  "hydra:search": {
    "@type": "string",
    "hydra:template": "string",
    "hydra:variableRepresentation": "string",
    "hydra:mapping": [
      {
        "@type": "string",
        "variable": "string",
        "property": "string",
        "required": true
      }
    ]
  }
}
```
-----------------------------------------------
### Attributes list
1. [`api_url`](#1-apiurl)
2. [`reqHeaders`](#2-reqheaders)
3. [`creeds`](#3-creeds)
4. [`account`](#4-account)
5. [`token`](#5-token)

### Query realted methods list

1. [`queryDomain()`](#1-querydomainindex1)
2. [`createAccount()`](#2-createaccountemail-password)
3. [`login()`](#3-loginemail-password)
4. [`deleteAccount()`](#4-deleteaccountid)
5. [`getToken()`](#5-gettoken)
6. [`queryAccount()`](#6-queryaccountmefalse-headersselfheaders)
7. [`syncAccountInfo()`](#7-syncaccountinfo)
8. [`genericQuery()`](#8-genericqueryendpoint-methodget-paramsnone-bodynone-jsontrue)
9. [`getAllEmails()`](#9-getallemails)
10. [`getEmail()`](#10-getemailid)
11. [`markAsRead()`](#11-markasreadid)
12. [`deleteEmailMsg()`](#12-deleteemailmsgid)

### Data related methods list

1. [`printAccountInfo()`](#1-printaccountinfo)
2. [`saveData()`](#2-savedata)
3. [`loadData()`](#3-loaddatafile)
4. [`checkResponse()`](#4-checkresponseres-msg)
5. [`printEmailList()`](#5-printemailslist)
6. [`exportAllEmails()`](#6-exportallemailsfilepath)
7. [`exportMail()`](#7-exportemailid-file)

--------------------------------------------------------

## [Attributes](#attributes-list)


### 1. `api_url`

> This is the url of the API used to access the email data: [API_URL](https://api.mail.tm)

### 2. `reqHeaders` 

> Here we can get/set the hearders that will be sent with the API queries

### 3. `creeds` 

> This are the email and password used to log into the email server  
> ```json
> {
>     "address": "example@domain.com",
>     "password": "somepassword"
> }
> ```
> *This data is automaticaly filled when instancing the class*

### 4. `account` 

> This is the account information just lline is retrieved fron */me* endpoint
> ```json
> {
>  "@context": "string",
>  "@id": "string",
>  "@type": "string",
>  "id": "string",
>  "address": "user@example.com",
>  "quota": 0,
>  "used": 0,
>  "isDisabled": true,
>  "isDeleted": true,
>  "createdAt": "2022-04-01T00:00:00.000Z",
>  "updatedAt": "2022-04-01T00:00:00.000Z"
> } 
> ```

### 5. `token`

> This one is the API JWT token

## [Query realted methods](#query-realted-methods-list)

**This ones are methods related to the data querying to the API**

### 1. `queryDomain(index=1)`

> Queries the API for a valid domain
> 
> **Parameters**
>
> - `index` *(default=1)*, This is the index of the domain to use, *currently only supports index=1*

### 2. `createAccount(email, password)`

> Create an account based on the with the values passed as parameters and save it into *`self.creeds`* , it also saves the *account ID* in *`self.account['id']`*
> 
> **Parameters**
> 
> - `email` Email used to login, this email must have a valid domain
> - `password` Password we want to set to the account

### 3. `login(email=None, password=None)`

> Log into the account using the credentias passes as parameters and it will fill the corresponding attributes of the object and request a token, if any of this values are not passes it will be replaced with the corresponding value in `self.creeds`
> 
> **Parameters**
> 
> - `email` Email used to login
> - `password` Password of the account

### 4. `deleteAccount(id)`

> Delete the account based on the *account ID*

### 5. `getToken()`

> Request the API a token based on the credentials set to *`self.creeds`* , this step is already done by the *`self.login()`* method when called, this method will add the token into the *`self.reqHeaders['Authorization']`* and the *`self.account['token']`* object

### 6. `queryAccount(me=False, headers=self.headers)`

> Requets data of an specific account based on the *account ID*, to do this we **must** have a token set
> 
> **Parameters**
> 
> - `me` *(defautl=False)* Query the current logged-in account, *based on the id at `self.account`*
> - `headers` Custom headers for the query, *must add: accept and Content-Type = application/json*

### 7. `syncAccountInfo()`

> Updates the values of the *self.account* attribute with the ones retrieved from the *`/me`* endpoint

### 8. `genericQuery(endpoint, method='GET', params=None, body=None, json=True)`

> Make a custom query to any endpoint and provide custom parameters or body
> 
> **Parameters**
> 
> - `endpoint` The endpoint we want to query (*without the initial slash* '/')
> - `method` The HTTP method to use for our query (*uppercase*)
> - `params` Parameter of our query (*url parameters, only GET method*)
> - `body` Content of the body of our query (*not used when usign GET method*)
> - `json` Tell if the *body* parameter is JSON formated

### 9. `getAllEmails()`

> Get all the emails of the current logged-in account in JSON format

### 10. `getEmail(id)`

> Get specific email based on the *email ID* in JSON format
> 
> **Parameters**
> 
> - `id` ID of the email we want to get data

### 11. `markAsRead(id)`

> Mark as read an specific email based on the *email ID*
> 
> **Parameters**
> 
> - `id` ID of the email we want to mark as read

### 12. `deleteEmailMsg(id)`

> Delete an specific email based on the *email ID*
> 
> **Parameters**
> 
> - `id` ID of the email we want to delete



## [Data related methods](#data-related-methods-list)

**This methods are related to the data formatting/representation operations**


### 1. `printAccountInfo()`

> Print the account information stored at *`self.account`* object

### 2. `saveData()`

> Save the credentials and the *account ID* in a CSV file as *'saved_data.csv'*, the data is formatted like *`email,password,id`*

### 3. `loadData(file)`

> Load the credentials and the *account ID* from a CSV file as *'saved_data.csv'* by default, the data must be formatted this way: *`email,password,id`*
> 
> **Parameters**
> 
> - `file` *(default='./saved_data.csv')* The name of the CSV file used to load the data

### 4. `checkResponse(res, msg)`

> Checks the *status_code* of a HTML response and raise an exception if status code is above **400**, if the status code is currently not handled it will return *False* but wont raise any exception
> 
> **Parameters**
> 
> - `res` Response object from the `requests` module
> - `msg` Custom message to print if the module raises an exception

### 5. `printEmailsList()`

> Print all the emails in a formatted way

### 6. `exportAllEmails(file='path')`

> Export all the emails to a JSON file with the name as *expot_* + **{timestamp}** by default
> 
> **Parameters**
> 
> - `file` Name of the output file, *Default: 'export_{timestamp}.json'*

### 7. `exportEmail(id, file=)`

> Exports a single email to a file named as *export_* + **{id}**
> **Parameters**
> - `id` ID of the email we want to export
> - `file` Name of the output file, *Default: 'export_{id}.json'*