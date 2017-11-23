import requests
import json
import time

SLEEP_INTERVAL=5

class EssentialsAPI:
    def __init__(self):
        self.__load_base_url()
        self.__load_auth_token()

    def __load_base_url(self):
        """ Load confluence api url from config file
        """
        try:
            self.base_url = file('base_url', 'rb').read().strip()
        except Exception as e:
            print 'Cannot find base url'
            print e
            exit(1)

    def __load_auth_token(self):
        """ Load confluence auth token from config file
        """
        try:
            print '\nLoading auth token...'
            self.auth_token = file('auth_token', 'rb').read().strip()
            print 'Auth token successfully loaded'
        except Exception as e:
            print 'Cannot load auth token from file "auth_token"'
            print e
            exit(1)

    def get_business_details(self, businessId):
        """ Create a page given page_content
            Space and page title are given by user at run time
        """
        headers = {"Authorization": "%s" % self.auth_token,
                  "Accept": "application/json, text/javascript",
                  "Content-Type": "application/json"}

        params_payload = {'businessId': businessId}

        print 'Sending get_business_details request for business %s...' % businessId
        try:
            response = requests.get(self.base_url, headers=headers, params=params_payload)
        except UnicodeEncodeError as e:
            print "Encountered error %s" % e
            print "sleeping %s seconds before retrying" % SLEEP_INTERVAL
            time.sleep(SLEEP_INTERVAL)
            response = requests.get(self.base_url, headers=headers, params=params_payload)

        if response.status_code == 200:
            print 'Request successful'
            return response.content
        else:
            print 'Oops error encountered!'
            print 'Status code: %s' % response.status_code
            print 'Response text: %s' % response.text
        print ""


def extract_details_businesses(fd, request_payload):
    payload = json.loads(request_payload)
    for business in payload:
        details = dict()
        details["businessId"] = business["businessId"]
        details["companyName"] = business["companyName"].encode('utf8')
        details["serialNumber"] = business["serialNumber"].encode('utf8')
        details["status"] = business["status"].encode('utf8')
        details["emails"] = map(lambda u: u['email'].encode('utf8'), business["users"])

        try:
            write_to_file(fd, details)
            # print_to_screen(details)
        except UnicodeEncodeError as e:
            print "Encountered error: %s" % e
            print details
            exit(-1)

def write_to_file(fd, business_details):
    fd.write('%s,%s,%s,%s,%s\n'% (business_details['businessId'],
                               business_details["companyName"],
                               business_details["serialNumber"],
                               business_details['status'],
                               ",".join(business_details['emails'])))

def print_to_screen(business_details):
    print '%s,%s,%s,%s,%s\n'% (business_details['businessId'],
                               business_details["companyName"],
                               business_details["serialNumber"],
                               business_details['status'],
                               ",".join(business_details['emails']))

def load_business_ids():
    input_file = 'au_businesses.txt'
    f = open(input_file, 'r')
    lines = f.readlines()
    if len(lines) <= 1:
        return []
    else:
        formatted_lines = map(lambda line: line.strip().split('_')[1], lines)
        f.close()
        return formatted_lines

"""
    This is test code only. Feel free to remove it!
"""
if __name__ == '__main__':
    api = EssentialsAPI()
    fd = open('emails.csv', 'w')
    fd.write('businessId, companyName, serialNumber, emails\n')
    map(lambda id: extract_details_businesses(fd, api.get_business_details(id)), load_business_ids())
    fd.close()
