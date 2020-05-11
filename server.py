from bottle import route, run, request, response
import GmailImap
import logging
import re
import threading


logging.basicConfig(format='%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s', level=logging.DEBUG)

SECRET = 'YOUR API SECRET TO PREVENT OTHERS FROM MAKING REQUESTS'
GMAIL_ADDRESS = 'your@gmail.com'
G_APP_PASS = 'YOUR GOOGLE APP PASSWORD'

imap_obj = GmailImap.GmailIMAP4_SSL()
imap_obj.login(GMAIL_ADDRESS, G_APP_PASS)

# Provide app info to Google, and get some back in return (RFC2971)
imap_obj.id('name', 'Sam Battat', 'contact', 'sam@battat.us')

# RFC3501
# get the message count from e.g. ('OK', ['3'])
folders = imap_obj.special_folders()


def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        return fn(*args, **kwargs)
    return _enable_cors


@route('/read/<thread_id_dec>')
@enable_cors
def read(thread_id_dec):
    logging.debug('Received a request with thread_id_dec ' + thread_id_dec)
    if request.query.secret == SECRET:
        logging.debug('Secret is correct')
        thread = threading.Thread(target=mark_as_read, args=(thread_id_dec,))
        thread.daemon = True
        thread.start()
        logging.debug('Return success')
        return 'Success'
    else:
        logging.debug('Secret is incorrect')
    return 'Fail'


def mark_as_read(thread_id_dec):
    logging.debug('Getting inbox counts')
    try:
        inbox_count = int(imap_obj.select(folders['Inbox'])[1][0])
        for index in range(inbox_count, inbox_count - 15, -1):
            logging.debug('Index is ' + str(index))
            # get the uid from e.g. ('OK', ['1 (UID 15310)'])
            response = imap_obj.fetch(index, '(UID)')[1][0]
            uid = re.search(r'([0-9]+)\)', response).group(1)
            thrid = imap_obj.uid2thrid(uid)
            logging.debug('THRID is ' + thrid)
            logging.debug('===================')
            if thrid == thread_id_dec:
                logging.debug('THRID matches thread_id_dec')
                logging.debug('Marked as read ' + str(index) + '(' + thread_id_dec + ')')
                imap_obj.mark_as_read(index)
                break
    except Exception as e:
        logging.error('There was an exception')
        logging.error(str(e))


# run server
run(host='0.0.0.0', port=80, debug=True)
