import numpy

def downsample(x,n=2):
    """downsample array x by factor n"""
    if n > 1:
        try:
            i = numpy.mod(len(x),n)
            x = x[:len(x)-i].reshape(-1, n).mean(axis=1)
        except:
            print "Warning: Could not downsample points"
            raise
    return x
    
def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size"""

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."

    if window_len<3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s = numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    
    if window == 'flat': #moving average
        w = numpy.ones(window_len,'d')
    else:
        w = eval('numpy.'+window+'(window_len)')

    y = numpy.convolve(w/w.sum(),s,mode='valid')
    return y

def GetSurface(x_orig, y_orig):
    """find surface of file[index]"""

    x = x_orig[250:] #cut off ca 1mm
    y = y_orig[250:]
    
    y = downsample(y, 20)
    x = downsample(x, 20)
    
    y=smooth(y,242)
    #x,y = butterworth(x,y,c=1))
    
    y_grad = numpy.gradient(y)
    y_grad = downsample(y_grad, 3)
    x_grad = downsample(x, 3)

    try:
        for i in numpy.arange(100,x_grad.size):

            std = numpy.std(y_grad[:i-1])
            mean = numpy.mean(y_grad[:i-1])
            if y_grad[i] >= 5*std + mean:
                surface = x_grad[i]
                break
            
        if i == x_grad.size-1:
            surface = numpy.amax(x_orig)   
    except:
        print "couldn't get surface"
        surface = numpy.amax(x_orig)
        pass
    
    print "surface: %0.2f mm"%surface
    return surface
 
def GetGround(pnt):
    """find ground of pnt object"""
    x = pnt.data[:,0]
    y = pnt.data[:,1]
    ol = pnt.header["Overload [N]"]
    ground = x[-1]
    
    if numpy.max(y) >= ol:
        i_ol = numpy.argmax(y)
        i_threshhold = numpy.where(x >= x[i_ol] - 20)[0][0]
        f_mean = numpy.mean(y[0:i_threshhold])
        f_std = numpy.std(y[0:i_threshhold])
        threshhold = f_mean + 5 * f_std
        
        while y[i_ol] > threshhold:
            i_ol -= 10 
        
        ground = x[i_ol]
    
    print "gound :%0.2f mm" %ground
    return ground
     
def linFit(x, y, surface=None):
    x = x[10:]
    y = y[10:]
    
    i = numpy.where(x >= surface)[0][0]
    x = x[:i]
    y = y[:i]
    
    m,c = numpy.polyfit(x, y, 1)
    y_fit = x * m + c
    std = numpy.std(y - y_fit)

    return x,y_fit,m,c,std


from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import scipy.fftpack
def butterworth(x,y,freq=242, c=5, o=2, show=False):
    """Filter signal y(x) with sampling frequency f using a o-order butterworth filter
       and cutoff frequency c""" 
    
    # Butterworth filter
    b, a = butter(o, (c/(freq/2)), btype = 'low')
    y2 = filtfilt(b, a, y) # filter with phase shift correction
    # plot
    """    fig, ax1 = plt.subplots(1,1)
    ax1.plot(x,  y, 'r.-', linewidth=1, label = 'raw data')
    ax1.plot(x, y2, 'g.-', linewidth=1, label = 'filtfilt')
    ax1.legend(frameon=False, fontsize=14)
    ax1.set_xlabel("Dist [mm]"); ax1.set_ylabel("Force [N]");

    plt.show()"""
    
    if show:
    # 2nd derivative of the data
        ydd = numpy.diff(y,2)*freq*freq   # raw data
        y2dd = numpy.diff(y2,2)*freq*freq # filtered data
        # frequency content 
        yfft = numpy.abs(scipy.fftpack.fft(y))/(y.size/2);   # raw data
        y2fft = numpy.abs(scipy.fftpack.fft(y2))/(y.size/2); # filtered data
        freqs = scipy.fftpack.fftfreq(y.size, 1./freq)
        yddfft = numpy.abs(scipy.fftpack.fft(ydd))/(ydd.size/2);
        y2ddfft = numpy.abs(scipy.fftpack.fft(y2dd))/(ydd.size/2);
        freqs2 = scipy.fftpack.fftfreq(ydd.size, 1./freq)
    
        fig, ((ax1,ax2),(ax3,ax4)) = plt.subplots(2, 2)
        
        ax1.set_title('Temporal domain', fontsize=14)
        ax1.plot(x, y, 'r', linewidth=1, label = 'raw data')
        ax1.plot(x, y2, 'b', linewidth=1, label = 'filtered @ %.2f per mm'%c)
        ax1.set_ylabel('f')
        ax1.legend(frameon=False, fontsize=12)
        
        ax2.set_title('Frequency domain', fontsize=14)
        ax2.plot(freqs[:yfft.size/2], yfft[:yfft.size/2],'r',  linewidth=1,label='raw data')
        ax2.plot(freqs[:yfft.size/2],y2fft[:yfft.size/2],'b--',linewidth=1,label='filtered @ %.2f per mm' %c)
        ax2.set_ylabel('FFT(f)')
        ax2.legend(frameon=False, fontsize=12)
        
        ax3.plot(x[:-2], ydd, 'r', linewidth=1, label = 'raw')
        ax3.plot(x[:-2], y2dd, 'b', linewidth=1, label = 'filtered @ %.2f Hz'%c)
        ax3.set_xlabel('Depth [mm]'); ax3.set_ylabel("f ''")
        
        ax4.plot(freqs[:yddfft.size/2], yddfft[:yddfft.size/2], 'r', linewidth=1, label = 'raw')
        ax4.plot(freqs[:yddfft.size/2],y2ddfft[:yddfft.size/2],'b--',linewidth=1,label='filtered @ %.2f per mm'%c)
        ax4.set_xlabel('Frequency [$mm^{-1}$]'); ax4.set_ylabel("FFT(f '')");
        
        plt.show()
    
    return x,y

def rsme(x_ref,x_sub, norm = False):
    rsme = ((x_ref - x_sub) ** 2).mean()
    if norm:
        rsme = rsme / numpy.max(x_ref) * 100
    return rsme
"""
.. topic:: Correlation module


    Provides two correlation functions. :func:`CORRELATION` is slower than 
    :func:`xcorr`. However, the output is as expected by some other functions. 
    Ultimately, it should be replaced by :func:`xcorr`.
    
    For real data, the behaviour of the 2 functions is identical. However, for
    complex data, xcorr returns a 2-sides correlation.
 

    .. autosummary:: 

        ~spectrum.correlation.CORRELATION
        ~spectrum.correlation.xcorr
        
    .. codeauthor: Thomas Cokelaer, 2011



"""#from numpy.fft import fft, ifft
import numpy
from numpy import  arange, isrealobj
from pylab import rms_flat

__all__ = ['CORRELATION', 'xcorr']


def CORRELATION(x, y=None, maxlags=None, norm='unbiased'):
    r"""Correlation function

    This function should give the same results as :func:`xcorr` but it 
    returns the positive lags only. Moreover the algorithm does not use
    FFT as compared to other algorithms. 
     
    :param array x: first data array of length N
    :param array y: second data array of length N. If not specified, computes the 
        autocorrelation. 
    :param int maxlags: compute cross correlation between [0:maxlags]
        when maxlags is not specified, the range of lags is [0:maxlags].
    :param str norm: normalisation in ['biased', 'unbiased', None, 'coeff']
     
        * *biased*   correlation=raw/N, 
        * *unbiased* correlation=raw/(N-`|lag|`)
        * *coeff*    correlation=raw/(rms(x).rms(y))/N
        * None       correlation=raw

    :return: 
        * a numpy.array correlation sequence,  r[1,N]
        * a float for the zero-lag correlation,  r[0]
    
    The *unbiased* correlation has the form:
    
    .. math::

        \hat{r}_{xx} = \frac{1}{N-m}T \sum_{n=0}^{N-m-1} x[n+m]x^*[n] T 

    The *biased* correlation differs by the front factor only:

    .. math::

        \check{r}_{xx} = \frac{1}{N}T \sum_{n=0}^{N-m-1} x[n+m]x^*[n] T 

    with :math:`0\leq m\leq N-1`.
    
    .. doctest::
    
        >>> from spectrum import *
        >>> x = [1,2,3,4,5]
        >>> res = CORRELATION(x,x, maxlags=0, norm='biased')
        >>> res[0]
        11.0
        
    .. note:: this function should be replaced by :func:`xcorr`.
    
    .. seealso:: :func:`xcorr`
    """
    assert norm in ['unbiased','biased', 'coeff', None]
    #transform lag into list if it is an integer
    if y == None:
        y = x
    
    # N is the max of x and y
    N = max(len(x), len(y))
    if len(x)<N:
        y = y.copy()
        y.resize(N)
    if len(y)<N:
        y = y.copy()
        y.resize(N)
            
    #default lag is N-1
    if maxlags == None:
        maxlags = N - 1
    assert maxlags < N, 'lag must be less than len(x)'
    
    realdata = isrealobj(x) and isrealobj(y)
    #create an autocorrelation array with same length as lag
    if realdata == True:
        r = numpy.zeros(maxlags, dtype=float)
    else:
        r = numpy.zeros(maxlags, dtype=complex)

    if norm == 'coeff':
        rmsx = rms_flat(x)
        rmsy = rms_flat(y)
        
    for k in range(0, maxlags+1):
        nk = N - k - 1
        
        if realdata == True:
            sum = 0
            for j in range(0, nk+1):
                sum = sum + x[j+k] * y[j]
        else:
            sum = 0. + 0j
            for j in range(0, nk+1):
                sum = sum + x[j+k] * y[j].conjugate()
        if k == 0:
            if norm in ['biased', 'unbiased']:
                r0 = sum/float(N)
            elif norm == None:
                r0 = sum
            else:
                r0 =  1.
        else:
            if norm == 'unbiased':
                r[k-1] = sum / float(N-k)
            elif norm == 'biased':
                r[k-1] = sum / float(N)
            elif norm == None:
                r[k-1] = sum
            elif norm == 'coeff':
                r[k-1] =  sum/(rmsx*rmsy)/float(N)

    r = numpy.insert(r, 0, r0)
    return r
 

def xcorr(x, y=None, maxlags=None, norm='biased'):
    """Cross-correlation using numpy.correlate
    
    Estimates the cross-correlation (and autocorrelation) sequence of a random
    process of length N. By default, there is no normalisation and the output
    sequence of the cross-correlation has a length 2*N+1. 
    
    :param array x: first data array of length N
    :param array y: second data array of length N. If not specified, computes the 
        autocorrelation. 
    :param int maxlags: compute cross correlation between [-maxlags:maxlags]
        when maxlags is not specified, the range of lags is [-N+1:N-1].
    :param str option: normalisation in ['biased', 'unbiased', None, 'coeff']
     
    The true cross-correlation sequence is
    
    .. math:: r_{xy}[m] = E(x[n+m].y^*[n]) = E(x[n].y^*[n-m])

    However, in practice, only a finite segment of one realization of the 
    infinite-length random process is available.
    
    The correlation is estimated using numpy.correlate(x,y,'full'). 
    Normalisation is handled by this function using the following cases:

        * 'biased': Biased estimate of the cross-correlation function
        * 'unbiased': Unbiased estimate of the cross-correlation function
        * 'coeff': Normalizes the sequence so the autocorrelations at zero 
           lag is 1.0.

    :return:
        * a numpy.array containing the cross-correlation sequence (length 2*N-1)
        * lags vector
        
    .. note:: If x and y are not the same length, the shorter vector is 
        zero-padded to the length of the longer vector.
               
    .. rubric:: Examples
    
    .. doctest::
    
        >>> from spectrum import *
        >>> x = [1,2,3,4,5]
        >>> c, l = xcorr(x,x, maxlags=0, norm='biased')
        >>> c
        array([ 11.])
    
    .. seealso:: :func:`CORRELATION`.  
    """
    N = len(x)
    if y == None:
        y = x
    assert len(x) == len(y), 'x and y must have the same length. Add zeros if needed'
    assert maxlags <= N, 'maxlags must be less than data length'
    
    if maxlags == None:
        maxlags = N-1
        lags = arange(0, 2*N-1)
    else:
        assert maxlags < N
        lags = arange(N-maxlags-1, N+maxlags)
              
    res = numpy.correlate(x, y, mode='full')
    
    if norm == 'biased':
        Nf = float(N)
        res = res[lags] / float(N)    # do not use /= !! 
    elif norm == 'unbiased':
        res = res[lags] / (float(N)-abs(arange(-N+1, N)))[lags]
    elif norm == 'coeff':        
        Nf = float(N)
        rms = rms_flat(x) * rms_flat(y)
        res = res[lags] / rms / Nf
    else:
        res = res[lags]

    lags = arange(-maxlags, maxlags+1)        
    return res, lags

from scipy.signal import detrend
def shotnoise(dz,f_z,A_cone=19.6):
    """This functions calculates the shot noise parameters from the 
    SMP penetration force correlation function according to:
    Loewe and van Herwijnen, 2012: A Poisson shot noise model for 
    micro-penetration of snow, CRST.
    d_z:
    f_z: array with force values
    A-cone: projected cone area [mm^2]"""
    
    N = len(f_z)
    
    #estimate shot noise parameters:
    c1 = numpy.mean(f_z) #mean
    c2 = numpy.var(f_z,ddof=1) #variance
    
    C_f,d = xcorr(detrend(f_z-c1),detrend(f_z-c1),norm="unbiased") # eq. 8 in Loewe and van Herwijnen, 2012
    
    #shot noise parameters
    delta = -3./2 * C_f[N-1] / ((C_f[N]) - C_f[N-1]) * dz # eq. 11 in Loewe and van Herwijnen, 2012  
    Lambda = 4./3 * (c1**2) / c2 / delta # eq. 12 in Loewe and van Herwijnen, 2012
    f_0 = 3./2 * c2 / c1 # eq. 12 in Loewe and van Herwijnen, 2012
    L = (A_cone/Lambda)**1/3
    
    return Lambda, f_0, delta, L 

def getSNParams(file, window=2.5,overlap=50):
    """get shot noise theory parameters, see function shotnoise()
    for details.
    x: distance array in mm 
    y: force array in N
    windows: analysis windows in mm
    overlap: overlap of windows in %
    """
    x = file.data[:,0]
    y = file.data[:,1]
    overlap = window * overlap / 100.
    dz = (x[-1]-x[0]) / len(x)
    start = numpy.where(x >= file.surface)[0][0]
    end = numpy.where(x >= file.ground)[0][0]
    x = x[start:end]
    y = y[start:end]
    
    x0 = x[0]
    dx = window - overlap
    data = []
    while x0 + window <= x[-1]:
        start = numpy.where(x >= x0)[0][0]
        end = numpy.where(x >= x0 + window)[0][0]
        data.append(shotnoise(dz,y[start:end]))
        x0 += dx
    
    return data 

def subtractMedian(x,y,window=200):
    """subtract median of frame from original signal y """
    start = 0
    end = len(y)-1
    y_out = []
    
    while start <= end:
        median = numpy.median(y[start:start+window])
        y_out[start:start+window] = y[start:start+window] - median
        start += window

    x_out = x[:len(y_out)]
    return x_out, y_out   

def transsectGetValues(x,y,window=2.5,overlap=50):
    """this function prepares 2d transect data.
    x = distance array
    y = force array f(x)
    window [mm] = alaysation window for log(median(f))
    overlap [%] = overlap of analyzation windows"""
    
    x_out = []
    y_out = []
    while x[0] + window <= x[-1]:
        i_end = numpy.where(x >=  x[0] + window)[0][0]
        median = numpy.median(y[:i_end])   
        i_start = numpy.where(x >= x[0] + window * overlap/100.)[0][0]
        x_out.append(x[0])
        y_out.append(numpy.log(median))
        x = x[i_start:]
        y = y[i_start:]        
        
    return x_out, y_out

from scipy import interpolate
def transsectFromFile(Files):
    """Create 2d transsect from pnt Files"""
    X = []
    F = []
    y = []
    #appen x,y, and force data to 3 arrays
    for file in Files:
        x, f = transsectGetValues(file.data[:,0],file.data[:,1])
        surface = numpy.where(x >= file.surface)[0][0]
        ground = numpy.where(x >= file.ground)[0][0]
        
        X.append(x[surface:ground])
        F.append(f[surface:ground])
        y.append(len(y))
            
    # Set up a regular grid of interpolation points
    xi, yi = numpy.linspace(X.min(), X.max(), len(X)/len(Files)), numpy.linspace(y.min(), y.max(), len(X)/len(Files))
    xi, yi = numpy.meshgrid(xi, yi)
    
    # Interpolate
    rbf = interpolate.Rbf(X, y, F, function='linear')
    zi = rbf(xi, yi)
    
    plt.imshow(zi, vmin=F.min(), vmax=F.max(), origin='lower',
               extent=[X.min(), X.max(), y.min(), y.max()])
    plt.scatter(X, y, c=F)
    plt.colorbar()
    plt.show() 

def forceDrops(x,y, max_dx = 0.020, min_dy = 0.050, dx_bins = 0.02):

    dy = -min_dy
    start = 0
    end = 1
    down = []
    i_max = len(y)
    
    while end < i_max:
                
        delta = y[start] - y[end]
        
        if x[end] - x[start] > max_dx:
            start += 1
            end = start + 1        
            continue

        elif  delta > dy:
            end += 1
            continue
        
        down.append(delta)

        start = end
        end = start + 1

    down = numpy.abs(down)
    bin_down = (max(down)-min(down))/dx_bins

    plt.hist(down, normed = True,  stacked = False, bins = bin_down)
    plt.show()    

    return down
