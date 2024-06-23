WATCH_INPUT = {
    "search": {
        "request": {
            "body": {
                "size": 0,
                "query": {}
            },
            "indices": []
        }
    }
}

WATCH_CONDITION = {
    "compare": {}
}

WATCH_TRIGGER = {
    "schedule": {
        "interval": ""
    }
}

WATCHER_TEMPLATE = {
    "name": "",
    "type": "json",
    "isNew": True,
    "isActive": True,
    "watch": {
        "trigger": {},
        "input": {},
        "condition": {},
        "actions": {}
    }
}

CREATE_WATCHER_API = '/api/watcher/watch/'

CHECK_WATCHER_API = '/api/watcher/watches'

ELASTIC_URL = 'https://elastic_instance_name.kb.us-east-1.aws.found.io:'

PORT = 9243

ELASTIC_HEADER = {
    "kbn-xsrf": "True",
    "Authorization": "Basic SOME_AUTH",
    "Content-Type": "application/json"
}

WEBHOOK_TEMP = {
        "webhook": {
        "scheme": "https",
        "host": "p9xg4onue6.execute-apsi.us-east-1.amazonaws.com",
        "port": PORT,
        "method": "post",
        "path": "", #user gives path
        "params": {}, # user gives param 
        "headers": {},# user gives header
        "auth": {
          "basic": {
            "username": "itaap-api-user",
            "password": "::es_redacted::"
          }
        },
        "body": "" #user gives webhook body
    }
}



MAIL_TEMP = { 'email': {
      "profile": "standard",
      "from": "",
      "to": [],
      "subject": "",
      "body": {
        "text": "" #user gives email body
      }
    }
}

INPUT_FILE = 'INPUT/watcher_automation_input copy.xlsm'

CONDITION = {
            "ctx.payload.hits.total" : {}
          }

COMPARATOR = {
'equals to': 'eq' ,
'greater than': 'gt',
'greater than equals to': 'gte',
'less than': 'lt',
'less than equals to': 'lte',
'not equals to': 'not_eq'
}

RESPONSE_SHEET = 'response/'

MASTER_SHEET = 'master/elastic_watcher_master.xlsx'

INPUT_FILE_MASTER_COPY = 'input_copy/watcher_automation_input.xlsm'
