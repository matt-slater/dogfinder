from requests_html import HTMLSession
import time
import smtplib
from email.message import EmailMessage
import ssl
import logging
import signal

class TimeoutException(Exception):   # Custom exception class
    pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException

# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)


def get_dogs_list(s, log):
    try:
        log.info("\x1B[3mfetching\x1B[23m new dogs...")
        r = s.get('https://www.muddypawsrescue.org/adoptable-dogs', stream=True)
    except:
        log.error("error in http request")
    log.info("request complete, rendering dog list....")
    r.html.render()
    log.info("render complete")
    dogs = r.html.xpath("//*[@id='result']//h5/text()")
    return set(dogs)


def get_local_time():
    t = time.localtime()
    curr_time = time.strftime("%H:%M:%S", t)
    return curr_time


def get_doggie_diff(new, old, log):
    log.info("new: {names}".format(names=new))
    log.info("old: {names}".format(names=old))
    if new.difference(old):
        return new.difference(old)
    else:
        return set()


def makeMessage(send, rec, message, subject):
    msg = EmailMessage()
    msg['From'] = send
    msg['To'] = rec
    msg['Subject'] = subject
    msg.set_content(message)
    return msg


def sendEmail(message):
    # constants
    port = 465  # For SSL

    # set up email server
    password = "00nothing"
    context = ssl.create_default_context()

    server = smtplib.SMTP_SSL("smtp.gmail.com", port, context=context)
    server.login("dogfinder.dev@gmail.com", password)
    server.send_message(message)
    server.quit()


def setup_logger():
    log = logging.getLogger('dogfinder-dev')
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s || %(name)s || %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    ch.setFormatter(formatter)
    log.addHandler(ch)
    return log


def main():
    log = setup_logger()
    log.info("STARTING DOGFINDER")

    # constants
    port = 465  # For SSL
    send_addresses = 'matt.a.slater@gmail.com,emmakimlin@gmail.com'
    from_address = 'dogfinder.dev@gmail.com'

    # get initial list
    s = HTMLSession()
    dogs = get_dogs_list(s, log)
    log.info("initial dog list: {names}".format(names=dogs))

    while True:
        signal.alarm(500)
        try:
            newDogs = get_dogs_list(s, log)
        except TimeoutException:
            log.info("get new dogs timed out. trying again.")
            continue
        else:
            signal.alarm(0)

        log.info("got dogs from remote: {names}".format(names=newDogs))
        doggieDiff = get_doggie_diff(newDogs, dogs, log)
        if doggieDiff:
            log.info("there are new dogs: {names}".format(names=doggieDiff))
            body = "there are new dogs:\n{names}\n go to https://www.muddypawsrescue.org/adoptable-dogs .....".format(names=doggieDiff)
            message = makeMessage(from_address, send_addresses, body, "NEW DOG ALERT!!!!")
            sendEmail(message)
            
        else:
            log.info("no new dogs")
        dogs = newDogs
        log.info("sleeping for 300 seconds")
        time.sleep(300)


if __name__== "__main__":
  main()

