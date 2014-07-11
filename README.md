<h1>IPMon<h1>
=====

a simple Python IP monitor and notifier

<p>IPMon has four main modes:
  <ul><li>Waiting</li>
      <li>Pinging</li>
      <li>DNS Lookup</li>
      <li>Notifying</li></ul></p>
  <br>
  <h2>Waiting</h2>
  <p>When waiting, the program is sitting idle. By default, the app has a 5 minute timeout. This is to keep the DNS servers and the checked servers from suspecting that IPMon is some sort of malware.</p>
  <h2>Pinging</h2>
  <p>IPMon uses a spread of 3 simple ICMP pings to determine if it is on and responding or not.</p>
  <h2>DNS Lookup</h2>
  <p>IPMon will perform a DNS lookup of your servers and determine if the IP has changed since the last check. If so, it will invoke the notify state. For DNS lookups, IPMon uses your local DNS config.</p>
  <h2>Notifying</h2>
  <p>IPMon uses a simple SMTP subprocess to send a notification email to the recipiants listed in the recipiants file. Additioanlly, any errors will be reported on the console, and all activity will be logged in the logfile.</p>

  <h1>Install Instructions</h1>
  <ol><li>clone the git repo into root (/)</li>
  <br># git clone https://github.com/peterfraedrich/IPMon.git
  <li>install sendmail<br># yum install -y sendmail</li>
  <li>configure sendmail<br>in /etc/mail/sendmail.mc
  <ul>  
  <li>change 'dnl MASQUERADE_AS('yourdomain.com')dnl to the domain of your mail server</li>
  <li>delete 'localhost' in 'DAEMON_OPTIONS('Port=smtp, Name=MTA')dnl</li></li>
  <li>open SMTP / port 25 in iptables<br># iptables -A INPUT -p tcp --dport 25 -j ACCEPT</li>
  <li>run<br># ./ipmon.py</li></ol> 
  
