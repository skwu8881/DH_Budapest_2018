import numpy as np

class CNN2label():
    def __init__(self,price):
        self.price = price
    
    def PriceSimulation():
        pass
    
    def CreatPriceImage():
        pass 
    
    def get_label(self):
        CNN_sim = self.price
        CNN_sim['CNN_label'] = np.random.randint(low = -1,high = 1,size = CNN_sim.shape[0])
        return CNN_sim