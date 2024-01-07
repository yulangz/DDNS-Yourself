import time
import os
import win32serviceutil
import win32service
import win32event
import servicemanager
import core

defaultConfigDir = os.path.dirname(os.path.abspath(__file__))

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = 'DDNS-Yourself'
    _svc_display_name_ = 'DDNS-Yourself'
    

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        self.ddns_client = core.DDNSClient()
        self.is_run = True

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,'start to run'))
        while self.is_run:
            try:
                self.ddns_client.readConfig()
                self.ddns_client.sync_hosts()
            except Exception as e:
                servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,"error" + e.__str__()))
            time.sleep(self.ddns_client.config['syncTime'])

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_run = False

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
