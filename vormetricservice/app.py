from __future__ import absolute_import
import logging, time, os

from dxlbootstrap.app import Application
from dxlclient.message import Event

# Configure local logger
logger = logging.getLogger(__name__)

class VormetricService(Application):
    """
    The "Vormetric Service" application class.
    """	
    
    # The topic to publish events to
    VOR_TOPIC = "/vormetric/event/denied_alert"
    
    #: The name of the "General" section within the application configuration file
    GENERAL_CONFIG_SECTION = "General"
    #: The property used to specify the the location of the Vormetric log file
    GENERAL_LOG_LOCATION_CONFIG_PROP = "logLocation"
    #: The property used to specify the interval to check the log in seconds
    GENERAL_LOG_CHECK_INTERVAL_CONFIG_PROP = "logCheckInterval"	

    def __init__(self, config_dir):
        """
        Constructor parameters:

        :param config_dir: The location of the configuration files for the
            application
        """
        super(VormetricService, self).__init__(config_dir, "vormetricservice.config")
        self._log_location = None
        self._log_check_interval = 10

    @property
    def client(self):
        """
        The DXL client used by the application to communicate with the DXL
        fabric
        """
        return self._dxl_client

    @property
    def config(self):
        """
        The application configuration (as read from the "vormetricservice.config" file)
        """
        return self._config

    def on_run(self):
        """
        Invoked when the application has started running.
        """
        logger.info("On 'run' callback.")

    def on_load_configuration(self, config):
        """
        Invoked after the application-specific configuration has been loaded

        This callback provides the opportunity for the application to parse
        additional configuration properties.

        :param config: The application configuration
        """
        logger.info("On 'load configuration' callback.")
        
        # Log location
        try:
            self._log_location = config.get(self.GENERAL_CONFIG_SECTION,
                                       self.GENERAL_LOG_LOCATION_CONFIG_PROP)
        except Exception:
            pass
        if not self._log_location:
            raise Exception(
                "Log location not found in configuration file: {0}"
                .format(self._app_config_path))
                
        logger.info("Vormetric log file location=" + self._log_location)

        # Log check interval
        try:
            self._log_check_interval = int(config.get(self.GENERAL_CONFIG_SECTION,
                                       self.GENERAL_LOG_CHECK_INTERVAL_CONFIG_PROP))
        except Exception:
            pass
        if not self._log_check_interval:
            raise Exception(
                "Log check interval not found in configuration file: {0}"
                .format(self._app_config_path))
                
        logger.info("Vormetric log check interval=" + str(self._log_check_interval))

    def on_dxl_connect(self):
        """
        Invoked after the client associated with the application has connected
        to the DXL fabric.
        """
        logger.info("On 'DXL connect' callback.")
        fileRead = open(self._log_location, 'r')

        stResults = os.stat(self._log_location)
        stSize = stResults[6]
        fileRead.seek(stSize)

        event = Event(self.VOR_TOPIC)

        while 1:
            where = fileRead.tell()
            line = fileRead.readline()
            if not line:
                time.sleep(self._log_check_interval)
                fileRead.seek(where)
            else:
                if line.find("vee-fs:") != -1 and line.find("[ALARM]") != -1:
                    #print("Line: |{}|".format(line.strip()))
                    parsedLog = self._parse_vor_log(line)

                    #line_parsed = {"Policy": parsedLog[0], "User": parsedLog[1], "Process": parsedLog[2], "Action": parsedLog[3], "Res": parsedLog[4]}
                    line_parsed = '{ "Policy":"' + parsedLog[0] + '", "User":"' + parsedLog[1] + '", "Process":"' + parsedLog[2] + '", "Action":"' + parsedLog[3] + '", "Resource":"' + parsedLog[4] + '"}'
                    #line_parsed = '{Policy: ' + parsedLog[0] + ',' + 'User: ' + parsedLog[1] + ','
                    print ("Line Parsed: {}".format(line_parsed))
                    
                    event.payload = (line_parsed)
                    self.client.send_event(event)

    def _parse_vor_log(self,lineToRead):
        parsedLog = []
        lineSplit = lineToRead.split(" Policy[")
        lineSplit = lineSplit[1].split("] User[")
        parsedLog.append(lineSplit[0])
        lineSplit = lineSplit[1].split("] Process[")
        parsedLog.append(lineSplit[0])
        lineSplit = lineSplit[1].split("] Action[")
        parsedLog.append(lineSplit[0])
        lineSplit = lineSplit[1].split("] Res[")
        parsedLog.append(lineSplit[0])
        if lineToRead.find("] Effect[") != -1:
            lineSplit = lineSplit[1].split("] Effect[")
            parsedLog.append(lineSplit[0].strip())
        else:
            lineSplit = lineSplit[1].split("]  Effect[")
            parsedLog.append(lineSplit[0].strip())
        return parsedLog
                    

