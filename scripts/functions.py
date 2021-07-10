from libraries import *

vims_wave = np.loadtxt('/home/alanyu/Dropbox (MIT)/VIMS_UROP/vims_wave.txt')
#belet = glob.glob("pixels/belet/*.pkl")
#senkyo = glob.glob("pixels/senkyo/*.pkl")
#shangrai = glob.glob("pixels/shangrai/*.pkl")

def gaussian(x,mean,sigma,A):    
    return A*np.exp(-((x-mean)**2.)/(2.*sigma**2))

def powerlaw(x,a, k, c):
    return a*x**k + c

def powerlaw_no_constant(x, a, k):
    return a*x**k

def V(x, A, mean, alpha, gamma):
    """
    Return the Voigt line shape at x with Lorentzian component HWHM gamma
    and Gaussian component HWHM alpha.

    """
    sigma = alpha / np.sqrt(2 * np.log(2))

    return np.real(A*wofz(((x-mean) + 1j*gamma)/sigma/np.sqrt(2))) / sigma\
                                                           /np.sqrt(2*np.pi)

def P(phase):
    return 4*np.pi/5 * ((np.sin(phase)+(np.pi-phase)*np.cos(phase))/np.pi + (1-np.cos(phase))**2/10)

def F(incidence,emission,phase,A=.285):
    return A * (np.cos(incidence)/(np.cos(incidence)+np.cos(emission))) * P(phase) + (1-A)*np.cos(incidence)

def pdf(x):
    return 1/sqrt(2*pi) * exp(-x**2/2)

def cdf(x):
    return (1 + erf(x/sqrt(2))) / 2

def skew(x,A=.15,e=0,w=1,a=0):
    t = (x-e) / w
    return A * 2 / w * pdf(t) * cdf(a*t)
