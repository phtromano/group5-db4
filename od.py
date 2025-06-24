import math

def blue_to_concentration(blue_channel):
    od = math.log10(92.67/blue_channel) 
    concentration = 486850.8 * od - 2589.31
    return concentration


def blue_to_concentration(blue_channel):
    od = math.log10(92.67/blue_channel) 
    concentration = 486850.8 * od - 2589.31
    return concentration

def c_to_concentration(c_channel):
    od = math.log10(146.138/c_channel) 
    concentration = 518613.298 * od - 461.345
    return concentration

def bc_to_concentration(b,c):
    od_b = math.log10(92.67/b) 
    od_c = math.log10(146.138/c)
    return 499054.5 * od_b - 490.5* od_c

u_per_hour = 0.058           # h⁻¹
u_per_ms   = u_per_hour / (3600 * 1000)  # ms⁻¹

def algae_growth_model(N0, dt):
    return N0 * math.exp(u_per_ms * dt)

def algae_growth_jacobian(N0, dt):
    return math.exp(u_per_ms * dt)

class ScalarKalman:
    def __init__(self, x0, P0, Q, R, growth_func, jacobian_F):
        # x0: initial conc.
        # P0: initial uncertainty
        # Q: process noise variance
        # R: measurement noise variance
        # growth_func(x): your model f(x)
        # jacobian_F(x): df/dx at x
        self.x = x0
        self.P = P0
        self.Q = Q
        self.R = R
        self.f = growth_func
        self.F = jacobian_F

    def predict(self, dt):
        # propagate state
        self.x = self.f(self.x, dt)
        Fk = self.F(self.x, dt)
        self.P = Fk*self.P*Fk + self.Q

    # def update(self, z):
    #     # z: measured concentration from OD regression
    #     K = self.P / (self.P + self.R)
    #     self.x = self.x + K*(z - self.x)
    #     self.P = (1 - K)*self.P
    #     return self.x

    def update(self, z, R=None):
        R = self.R if R is None else R
        K = self.P/(self.P + R)
        self.x = self.x + K*(z - self.x)
        self.P = (1 - K)*self.P
        return self.x
