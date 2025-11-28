import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import r, URL_VEHICLE, URL_FOR_REQUEST, URL_OPENAPI, MAIL_USER, MAIL_PASSWORD, MAIL_PORT, MAIL_SENDER, MAIL_SERVER, \
    access_logger, error_logger
from jinja2 import Environment, FileSystemLoader


def validate_env() -> None:
    '''Validate environment variables'''

    if not URL_VEHICLE:
        raise Exception('URL_VEHICLE environment variable not defined.')
    if not URL_FOR_REQUEST:
        raise Exception('URL_FOR_REQUEST environment variable not defined.')
    if not URL_OPENAPI:
        raise Exception('URL_OPENAPI environment variable not defined.')
    if not MAIL_USER:
        raise Exception('MAIL_USER environment variable not defined')
    if not MAIL_PASSWORD:
        raise Exception('MAIL_PASSWORD environment variable not defined')
    if not MAIL_PORT:
        raise Exception('MAIL_PORT environment variable not defined')
    if not MAIL_SENDER:
        raise Exception('MAIL_SENDER environment variable not defined')
    if not MAIL_SERVER:
        raise Exception('MAIL_SERVER environment variable not defined')


def get_mailer():
    '''Send mail config'''

    mailer = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
    mailer.login(MAIL_USER, MAIL_PASSWORD)
    return mailer


def send_mail(alignments: list[dict], recipients: list):
    '''Send mail using mailer'''

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('alignment_email.html')

    mailer = get_mailer()
    for alignment in alignments:
        try:
            html_content = template.render(data=alignment)
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Aligment Serial: {alignment.get('serial')}'
            msg['From'] = MAIL_SENDER
            msg['To'] = ', '.join(recipients)
            msg.attach(MIMEText(html_content, 'html'))
            access_logger.info(f'Sending email to {', '.join(recipients)}')
            mailer.sendmail(MAIL_SENDER, recipients, msg.as_string())
            r.set(alignment.get('serial'), 1)
        except Exception as ex:
            error_logger.exception(
                f'There was an error while trying to send the email {str(ex)}')
    mailer.quit()
    access_logger.info('Mails sent successfully')
