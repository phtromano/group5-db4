class PID:
    def __init__(self, measuredValue, wantedTemperature):
        self.measuredValue = measuredValue
        self.temp = wantedTemperature
        self.error = [self.temp-self.measuredValue]
        self.lengthError = 1
    
    def setP(self,value):
        self.P = value

    def setI(self,value):
        self.I = value
    
    def setD(self,value):
        self.D = value

    def PID_values(self, newMeasure):

        
        if self.lengthError > 10:
            self.error.pop(0)

        self.error.append(newMeasure - self.temp)
        self.lengthError +=1
        self.measuredValue = newMeasure


        P = self.P * self.error[-1]
        I = self.I * sum(self.error)
        D = self.D * (self.error[-1] - self.error[-2])

        u =  P + I + D
        return u