"""
A convenient webfaction interactive api wrapper.

The perfect tool to play with webfaction api.
"""

__author__ = 'Rolando Espinoza La fuente <darkrho@gmail.com>'
    
import sys
import xmlrpclib

APIREF = {
    'login': 'login(username, password [, machine=None])',
    'change_mailbox_password': 'change_mailbox_password(mailbox, password)',
    'create_email': "create_email(email_address, targets[,"
    "autoresponder_on=False, autoresponder_subject='',"
    "autoresponder_message='', autoresponder_from=''])",
    'create_mailbox': "create_mailbox(mailbox,"
    "enable_spam_protection=True, discard_spam=False,"
    "spam_redirect_folder='', use_manual_procmailrc=False,"
    "manual_procmailrc='')",
    'delete_email': 'delete_email(email_address)',
    'list_emails': 'list_emails()',
    'list_mailboxes': 'list_mailboxes()',
    'update_email': "update_email(email_address, targets,"
    "autoresponder_on=False, autoresponder_subject='',"
    "autoresponder_message='', autoresponder_from='')",
    'update_mailbox': "update_mailbox(mailbox,"
    "enable_spam_protection=True, discard_spam=False,"
    "spam_redirect_folder='', use_manual_procmailrc=False,"
    "manual_procmailrc='')",
    'create_domain': "create_domain(domain, *subdomains)",
    'create_website': 'create_website(website_name, ip, https,'
    'subdomains, *site_apps)',
    'update_website': 'update_website(website_name, ip, https,'
    'subdomains, *site_apps)',
    'delete_domain': 'delete_domain(domain, *subdomains)',
    'delete_website': 'delete_website(website_name, ip=None,'
    'https=None)',
    'list_domains': 'list_domains()',
    'list_websites': 'list_websites()',
    'create_app': "create_app(name, type, autostart,"
    "extra_info, script_code='')",
    'delete_app': 'delete_app(name)',
    'list_apps': 'list_apps()',
    'create_cronjob': 'create_cronjob(line)',
    'delete_cronjob': 'delete_cronjob(line)',
    'create_dns_override': "create_dns_override(domain,"
    "a_ip='', cname='', mx_name='', mx_priority='', spf_record='')",
    'delete_dns_override': "delete_dns_override(domain,"
    "a_ip='', cname='', mx_name='', mx_priority='', spf_record='')",
    'list_dns_overrides': 'list_dns_overrides()',
    'create_db': 'create_db(name, db_type, password)',
    'delete_db': 'delete_db(name, db_type)',
    'list_dbs': 'list_dbs()',
    'replace_in_file': 'replace_in_file(filename, *changes)',
    'write_file': "write_file(filename, str, mode = 'wb')",
    'run_php_script': "run_php_script(script[, code_before=''])",
    'set_apache_acl': "set_apache_acl(paths, permission='rwx',"
    "recursive=False)",
    'system': 'system(cmd)',
}

API_SESSION_METHODS = ('login',)

class Webfaction(object):
    """This class represents webfaction api wrapper"""

    def __init__(self, username, password, machine=None):
        """setup session id"""
        self.server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
        # store credentials
        self.username = username
        self.machine = machine
        # make login call
        args = [username, password]
        if machine:
            args.append(machine)
        self.session_id, self.account = self.server.login(*args)
        # setup __dict__ from APIREF for easy reference
        for method,doc in APIREF.items():
            self.__dict__[method] = self.__getattr__(method)

    def __getattr__(self, attr):
        """wraps server.func with session_id"""
        #TODO: prevent or wrap second login call
        class wrap(object):
            def __init__(inner, attr):
                inner.method = getattr(self.server, attr)
                inner.add_sessid = attr in API_SESSION_METHODS
                inner.__doc__ = APIREF.get(attr, 'unknown')

            def __call__(inner, *args, **kwargs):
                if inner.add_sessid:
                    return inner.method(self.session_id, *args, **kwargs)
                else:
                    return inner.method(*args, **kwargs)

            def __repr__(inner):
                return '<Ref: %s>' % inner.__doc__

        return wrap(attr)

    def __repr__(self):
        return '<%s - %s>' % (self.username, self.session_id)

    def help(self):
        for item in APIREF.items():
            print "%s\t%s" % item

if __name__ == '__main__':
    nargs = len(sys.argv[1:])
    if nargs < 2 or nargs > 3:
        print "usage: %s username password [machine]" % sys.argv[0]
        sys.exit()

    banner = """
    A convenient Webfaction api wrapper
    See docs: http://docs.webfaction.com/xmlrpc-api/apiref.html
    Available objects: api
    example:
        api.create_createdb
        api.list_dbs()
        api.system('ls')
        api.help()
    Just do not use session_id parameter that it is already
    added to each api call."""

    try:
        api = Webfaction(*sys.argv[1:])
    except xmlrpclib.Fault, e:
        print >> sys.stderr, "RPC Error: %s" % e
    else:
        from IPython import Shell
        Shell.IPShellEmbed([], banner)()
    
