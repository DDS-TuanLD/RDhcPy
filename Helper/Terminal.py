import subprocess

class Terminal():
    def Execute(self, cmd: str):
        s = subprocess.getstatusoutput(cmd)
    
    def ExecuteWithResult(self, cmd: str)->tuple:
        s = subprocess.getstatusoutput(cmd)
        return s
    