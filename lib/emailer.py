def SendEmail(title):

  # Import smtplib for the actual sending function
  import smtplib
  import getpass, socket
  import traceback
  import lib.logger.logger as logger
  import lib.config as config

  # Import the email modules we'll need
  from email.mime.text import MIMEText

  # Open a plain text file for reading.  For this example, assume that
  # the text file contains only ASCII characters.
  textfile = "Output.txt"
  fp = open(textfile, 'rb')
  # Create a text/plain message
  msg = MIMEText(fp.read())
  fp.close()

  # me == the sender's email address
  # you == the recipient's email address
  msg['Subject'] = title .format(textfile)
  msg['From'] = config.from_address
  msg['To'] = config.to_address

  try:
    # Open the SMTP connection, via SSL if requested
    logger.logging.debug("Connecting to host %s on port %s" % (config.smtp_server, config.smtp_port))
    logger.logging.debug("SMTP over SSL %s", ("enabled" if config.smtp_ssl == 1 else "disabled"))
    mailserver = smtplib.SMTP_SSL(config.smtp_server, config.smtp_port) if config.smtp_ssl == 1 else smtplib.SMTP(config.smtp_server, config.smtp_port)

    if config.starttls:
      logger.logging.debug("Using StartTLS to initiate the connection with the SMTP server")
      mailserver.starttls()

    # Say hello to the server
    mailserver.ehlo()

    # Check too see if an login attempt should be attempted
    if len(smtp_user) > 0:
      logger.logging.debug("Logging on to SMTP server using username \'%s\'%s", (config.smtp_user, " and a password" if len(config.smtp_pass) > 0 else ""))
      mailserver.login(config.smtp_user, config.smtp_pass)

      # Send the e-mail
      logger.logging.debug("Sending the email")
      mailserver.sendmail(config.from_address, splitString(config.to_address), message.as_string())

      # Close the SMTP connection
      mailserver.quit()
      
      logger.logging.info('Email notification sent')

    return True
  except:
    logger.logging.error('E-mail failed: %s', traceback.format_exc())
