import requests
import time
import json
import win32serviceutil
import win32service
import win32event
import servicemanager

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = 'DDNS-Yourself'
    _svc_display_name_ = 'DDNS-Yourself'
    

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        try:
            with open('private.config.json') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            with open('config.json') as config_file:
                self.config = json.load(config_file)
        

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,'start to run'))
        self.setup_gateway()
        self.sync_hosts(force=True)  # 首次启动时强制同步
        while True:
            self.sync_hosts()
            time.sleep(self.config['syncTime'])

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def sync_hosts(self, force=False):
        try:
            payload = {'clientDomain': self.config['domain']}
            if force:
                payload['force'] = 1

            response = requests.post(f"http://{self.config['serverAddr']}:{self.config['serverPort']}/route/sync", json=payload)
            if response.json():
                with open(self.config["hostPath"], 'r+') as hosts_file:
                    lines = hosts_file.readlines()
                    new_content = ""
                    for line in lines:
                        if not line.strip().endswith(self.config["domainSuffix"]):
                            new_content += line
                    for domain, ipv6 in response.json().items():
                        new_content += f"{ipv6} {domain}\n"

                    hosts_file.seek(0)
                    hosts_file.write(new_content)
                    hosts_file.truncate()
                    # print("Hosts updated")

        except Exception as e:
            servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,e.with_traceback()))

    def setup_gateway(self):
        pass
        # if self.config['gateway']:
        #     for interface in self.config['networkInterface']:
        #         if platform.system() == "Windows":
        #             os.system(f"netsh interface ipv6 add route ::/0 interface={interface} store=persistent {self.config['gateway']}")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
