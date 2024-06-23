from datetime import datetime
import requests
import json
import pandas as pd
import os
import shutil

from watcher_config import *


class WatcherGenerator:

    def __init__(self):
        self.base_template = WATCHER_TEMPLATE
        self.watcher_name_list = ''

    def fill_schedular(self, row):
        #filling the schedular for watcher
        trigger = WATCH_TRIGGER
        try:
            trigger['schedule']['interval'] = str(row['INTERVAL']
                                              ) + row['UNIT'][0]
        except KeyError as key_error:
            # hit the exception and print key_value error in case of missing values
            print(f'key error: {key_error} \n', '-'*60, sep='')
        return trigger

    def fill_input(self, row):
        # filling watcher inputs
        input = WATCH_INPUT
        try:
          # convert the query input in json format
          if pd.isna(row['QUERY']):
                # Handle NaN values (modify this part based on your needs)
                print("No query available")
                input['search']['request']['body']['query'] = ''
          else:
              input['search']['request']['body']['query'] = json.loads(
                  row['QUERY'])
          # fill the search type
          input['search']['request']['search_type'] = row['SEARCH_TYPE']
          # fill the array of indices
          input['search']['request']['indices'] = [
              index.strip() for index in row['INDICES'].split(',')]
          # print the query
          print('query = {} \n'.format(json.loads(row['QUERY'])
                                       ), '-'*60, sep='')
          # fill the body size
          input['search']['request']['body']['size'] = row['SIZE']
        except KeyError as key_error:
            # hit key error for missing values
            input['search']['request']['body']['query'] = ''
            print(f'Key Error: {key_error} \n', '-'*60, sep='')
        except Exception as exp:
            print(f'Key Error: {exp} \n', '-'*60, sep='')
        return input

    def fill_condition(self, row):
        condition = WATCH_CONDITION
        try:
            # filling the conditions
            condition['compare']['ctx.payload.hits.total'] = {COMPARATOR[row[
                'CONDITION_COMPARATOR']]: row['CONDITION_VALUE']}
        except KeyError as key_error:
            # hit the key error for missing values
            print(f'Key Error: {key_error} \n', '-'*60, sep='')
        # print the conditions set for watcher
        print("condition  = {}\n".format(condition), '-'*60, sep='')
        return condition

    def fill_actions(self, row):
        # filling the action inputs in the action parameter of watcher
        actions = {}
        mail = MAIL_TEMP
        webhook = WEBHOOK_TEMP
        try:
            # filling the parameters for email
            print(row['ACTION'])
            if row['ACTION'] == 'mail' or row['ACTION'] == 'both':
                mail['email']['from'] = row['MAIL_SENDER']
                mail['email']['to'] = [email.strip() for email in row[
                    'MAIL_RECEIVER'].split(',')]
                mail['email']['subject'] = row['MAIL_SUBJECT']
                mail['email']['body']['text'] = row['MAIL_BODY']
                actions['email_admin'] = mail
            if row['ACTION'] == 'webhook' or row['ACTION'] == 'both':
                # filling the parameters for webhook
                print('cntl in action-webhook \n', '-'*60, sep='')
                webhook['webhook']['path'] = row['WEBHOOK_PATH']
                webhook['webhook']['params'] = row['WEBHOOK_PARAMS']
                webhook['webhook']['headers'] = row['WEBHOOK_HEADERS']
                webhook['webhook']['body'] = row['WEBHOOK_BODY']
                actions['my_webhook']['webhook'] = webhook['webhook']
        except KeyError as key_error:
            # hit the exception for missing action rows
            print(f'Key Error: {key_error} \n', '-'*60, sep='')
        return actions
        

    def send_request(self, base_temp, name):
        # PRINT STATEMENT
        print("send payload request to fill rules\n", "-"*60, sep='')

        # convert rule input to json
        payload = json.dumps(base_temp)

        # PRINT PAYLOAD
        print("payload \n", "-"*60, "\n", payload, "\n", "-"*60, sep='')

        # create url for sending create request
        url = ELASTIC_URL + str(PORT) + CREATE_WATCHER_API + name
        # send rule creation request to elastic
        print("url = {} \n".format(url), '-'*60, sep='')
        response = requests.put(url, headers=ELASTIC_HEADER, json=payload)
        
        # PRINT response code and message
        print("create rule \n", "-"*60, sep='')
        print("Response Status Code = {0} Response Status message = {1}\n".
              format(response.status_code, response.text), "-"*60, sep='')
        return response

    def read_input(self):
        # reading input excel sheet
        print('reading the input file = {} \n'.format(
            INPUT_FILE.split("/")[-1]), '-'*60, sep='')
        # converting input rows to data frame
        watcher_df = pd.read_excel(INPUT_FILE)
        return watcher_df

    def watcher_creation(self):
        # creating the watchers
        print('watcher generations started \n', '-'*60, sep='')

        # get the input data frames from input sheet
        watcher_df = self.read_input()
        
        # create data frames for successful and failed requests
        watcher_df_pass = pd.DataFrame(columns=watcher_df.columns)
        watcher_df_fail = pd.DataFrame(columns=watcher_df.columns)

        # get all watchers list
        self.watcher_name_list = self.get_watcher_name_list()

        #iterating through input rows and send rule creation request
        for cnt, row in watcher_df.iterrows():
            print('count = {} watcher name = {} \n'.format(cnt, row['NAME']
                                                           ), '-'*60, sep='')
            #check for empty rows
            if pd.isna(row['NAME']):
                # Handle NaN values (modify this part based on your needs)
                print("Skipping row due to NaN values")
                continue
            name = row['NAME']
            #check if watcher exits
            if (any(name in d.get('name', '') or name in d.get(
                'id', '') for d in self.watcher_name_list)):
                row_index = len(watcher_df_fail)
                watcher_df_fail.loc[row_index] = row
                watcher_df_fail.at[row_index, 'STATUS'
                                   ] = 'pre exsiting watcher name'
                continue

            base_temp = self.base_template.copy()
        
            base_temp['watch']['actions'] = self.fill_actions(row)   
            base_temp['watch']['condition'] = self.fill_condition(row)
            base_temp['watch']['trigger'] = self.fill_schedular(row)
            base_temp['watch']['input'] = self.fill_input(row)
            base_temp['name'] = row['NAME']
            # send create request
            print('name = {0} \n base_temp = \n{1}\n'.format(
                row['NAME'], base_temp), '-'*60)
            resp = self.send_request(base_temp, row['NAME'])
            if resp.status_code == 200:
                watcher_df_pass.loc[len(watcher_df_pass)] = row
                watcher_df_pass['STATUS'] = "Success [Resp code: "+ str(
                    resp.status_code) + " ]"
                # PRINT STATEMENT
                print("rule name = {0} \n status = {1}".format(
                    row['NAME'], watcher_df_pass['STATUS']))
            else:
                row_index = len(watcher_df_fail)
                watcher_df_fail.loc[row_index] = row
                watcher_df_fail.at[row_index, 'STATUS'] = resp.text
              
                # PRINT STATEMENT
                print("rule name = {0} status = {1}".format(
                    row['NAME'], watcher_df_fail['STATUS']))
            
        # update master sheet
        self.update_master(watcher_df_pass, watcher_df_fail)
        
        # update response sheet:
        self.update_response(watcher_df_pass, watcher_df_fail)
        #replace input file with master copy
        print("replace input file with master copy")
        self.replace_input_file()

                
    def update_response(self, watcher_df_pass, watcher_df_fail):
        # create the file name of response using current datetime
        # concat the name with response folder path
        sheet_name = datetime.now().strftime(
                     "%Y-%m-%dT%H-%M-%S") + '.xlsx'
        # RECORDS/ELASTIC_ALERT_RULES_MASTER.xlsx
        resp_sheet = RESPONSE_SHEET + sheet_name
        print("updating resposne sheet {}\n".format(sheet_name
                                                    ), "-"*60, sep=" ")
        # merge failed and passed request dataframe
        merged_df_reqst = pd.concat([watcher_df_pass, watcher_df_fail], 
                                   ignore_index=True)
        # write to response sheet
        with pd.ExcelWriter(resp_sheet, engine='openpyxl') as writer:
            merged_df_reqst.to_excel(writer, index=False)

    def get_watcher_name_list(self):
        # create url for sending wtacher names get request
        url = ELASTIC_URL + str(PORT) + CHECK_WATCHER_API
        response = json.loads(requests.get(url, headers=ELASTIC_HEADER
                                           ).text)['watches']
        # refine the response data for only watcher name and id
        extracted_data = [{'id': item['id'], 'name': item['name']
                           } if 'name' in item else {'id': item['id']
                                                     } for item in response]
        return extracted_data

    def update_master(self, watcher_df_pass, watcher_df_fail):
        # PRINT MASTER SHEET NAME 
        print("updating master sheet = {}\n".format(
            MASTER_SHEET.split("/")[-1]), "-"*60, sep='')
        
        # Read existing 'success' sheet
        try:
            df_success = pd.read_excel(
                MASTER_SHEET, sheet_name='success', engine='openpyxl')
        except FileNotFoundError:
            df_success = pd.DataFrame()
    
        # Concatenate new data with existing 'success' data
        merged_df_pass = pd.concat([df_success, watcher_df_pass], 
                                   ignore_index=True)
    
        # Read existing 'failed' sheet
        try:
            df_failed = pd.read_excel(MASTER_SHEET, sheet_name='failed',
                                     engine='openpyxl')
        except FileNotFoundError:
            df_failed = pd.DataFrame()
        #
        # Concatenate new data with existing 'failed' data
        merged_df_fail = pd.concat([df_failed, watcher_df_fail],
                                    ignore_index=True)
    
        # Write updated DataFrames back to Excel sheets
        with pd.ExcelWriter(MASTER_SHEET, engine='openpyxl') as writer:
            merged_df_pass.to_excel(writer, index=False, sheet_name='success')
            merged_df_fail.to_excel(writer, index=False, sheet_name='failed')

    def replace_input_file():
        # replace input file with master
        source_file = INPUT_FILE_MASTER_COPY
        destination_file = INPUT_FILE
        # Check if the source file exists
        if not os.path.exists(source_file):
            print(f"Source file '{source_file}' does not exist.")
            return
    
        # Check if the destination file exists
        if os.path.exists(destination_file):
            # If the destination file exists, delete it
            os.remove(destination_file)
    
        # Copy the source file to the destination
        shutil.copy2(source_file, destination_file)

if __name__ == "__main__":
    watch_gen = WatcherGenerator()
    watch_gen.watcher_creation()
