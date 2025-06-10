class PID_OD:
    def __init__(self, measuredValue, wantedOD):
        self.measuredValue = measuredValue
        self.od = wantedOD
        self.error = [self.measuredValue - self.od]
        self.lengthError = 1
    
    def setP(self,value):
        self.P = value

    def setI(self,value):
        self.I = value
    
    def setD(self,value):
        self.D = value

    def PID_values(self, newMeasure):

        self.error.append(newMeasure - self.od)
        self.lengthErrorArray += 1
        self.measuredValue = newMeasure


        P = self.P * self.error[-1]
        I = self.I * sum(self.error)
        D = self.D * (self.error[-1] - self.error[-2])

        u =  P + I + D
        return u  