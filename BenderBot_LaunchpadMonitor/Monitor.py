from launchpadlib.launchpad import Launchpad
from datetime import datetime, timedelta
from ConfigParser import NoOptionError, NoSectionError
import lazr.restfulclient.errors as errors
from BenderBot.BenderProcess import BenderProcess
from time import sleep

class Monitor(BenderProcess):
    
    def run(self):
        
        # pull in our plugin configuration
        try:
            project = self.config.get('LaunchpadMonitor', 'project')
            age = self.config.get('LaunchpadMonitor', 'age')
            system = self.config.get('LaunchpadMonitor', 'system')
            intreval = self.config.get('LaunchpadMonitor', 'intreval')
        except NoOptionError as e:
            self.logger.error('Missing age, system, intreval, or project options')
            raise Exception(e)
        except NoSectionError as e:
            self.logger.error('missing LaunchpadMonitor section')
            raise Exception(e)
        
        # authenticate to Launchpad
        self.logger.debug('attempting login to launchpad %s' % system)
        try:
            lp = Launchpad.login_with('BenderBot.LaunchpadMonitor', system)
        except ValueError as e:
            self.logger.error('%s' % e)
            raise Exception(e)
            
        # Lookup Launchpad project
        self.logger.debug('looking up project %s' % project)
        try:
            ius = lp.projects(project)
        except errors.NotFound as e:
            self.logger.error('%s' % e)
            raise Exception(e)
        
        while True:
            drift = datetime.utcnow() - timedelta(minutes=int(age))
            self.logger.info('searching launchpad bugs')
            
            # Get bugs that are X minutes old
            try:
                tasks = ius.searchTasks(modified_since=drift)
            except:
                self.logger.warning('failed to get bugs from launchpad')
                return

            self.logger.info('found %s bugs' % len(tasks))            
            for task in tasks:
                title = task.title.split(': ')[1]
                msg = '[Bug Updated] %s: %s' % (title, task.web_link)
                self.irc.sendchannel(msg)
                
            sleep(int(intreval))