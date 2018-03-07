import numpy as np
import math

class ActivationFunctions:
    def SIGMOID( x ):
        return 1 / ( 1 + math.exp( -4.9*x ) )

    def RELU( x ):
        return max( 0, x )

    def SOFTPLUS( x ):
        return math.log( 1 + math.exp( x ) )
