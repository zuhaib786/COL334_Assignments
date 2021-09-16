import subprocess
import re
import time
import matplotlib
import matplotlib.pyplot as plt
class Traceroute:
    def __init__(self, destination, count):
        self.destination = destination
        self.version = "-4"
        self.data =[]
        self.RTT = []
        self.count = count
    def run(self):
        for ttl in range(1, 31):
            bashCmd = ["ping", self.version, "-i", str(ttl), self.destination]
            process = subprocess.Popen(bashCmd, stdout = subprocess.PIPE)
            output, error =  process.communicate()
            process.kill()
            output = output.split(b"\n")
            output = [i.decode('utf-8') for i in output]
            print("TTL = ", ttl,flush = True)
            s = None
            for i in range(2, 5):
                if (output[i].find('expired') == -1 and output[i].find('timed out') == -1):
                    print(output[i],flush = True)
                    print(output[i].split()[4].split("=")[1][:-2],flush = True)
                    self.RTT.append(int(output[i].split()[4].split("=")[1][:-2]))
                    self.data.append(ttl)
                    plt.plot(self.data, self.RTT)
                    plt.xlabel("Number of Hops")
                    plt.ylabel("Round Trip Time")
                    plt.savefig("TTL vs RTT.png")
                    plt.show()
                    return
                elif (output[i].find('timed out') == -1):
                    s = output[i]
            if(s==None):
                self.RTT.append(0.0)
                self.data.append(ttl)
                print("*   *    *  RTTT = 0 due to timeout",flush = True)
                
            else:
                s = s.split()
                bashCmd = ["ping", self.version, s[2][:-1]]
                print(s[2][:-1])
                process = subprocess.Popen(bashCmd, stdout = subprocess.PIPE)
                output, error =  process.communicate()
                process.kill()
                output = output.split(b"\n")
                output = [i.decode('utf-8') for i in output]
                cnt = 0
                time = 0
                for i in range(2, 5):
                    if(output[i].find('expired')==-1 and output[i].find('timed out') == -1):
                        st = output[i].split()[4].split("=")[1][:-2]
                        print(st, "ms",end = ' ',flush = True)
                        time+=int(st)
                        cnt+=1
                    else:
                        print("*",end = ' ',flush = True)
                if(cnt == 0):
                    self.data.append(ttl)
                    self.RTT.append(0)
                    print("RTT = 0 due to ping failure",flush = True)
                else:
                    self.data.append(ttl)
                    self.RTT.append(time/cnt)
                    print("RTT = ", time/cnt,flush = True)
print("Enter the destination to Traceroute: ",flush =True)
url = input().split()[0]
print("Tracing route to ", url,flush = True)
tracker = Traceroute(url, 0)
tracker.run()