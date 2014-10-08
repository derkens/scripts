def SendEmail(user, title):

  # Import smtplib for the actual sending function
  import smtplib
  import getpass, socket

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
  msg['Subject'] = title % textfile
  msg['From'] = getpass.getuser() + '@' + socket.gethostname()
  msg['To'] = user

  # Send the message via our own SMTP server, but don't include the
  # envelope header.
  s = smtplib.SMTP('localhost')
  s.sendmail(me, [you], msg.as_string())
  s.quit()
  return
