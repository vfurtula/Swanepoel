<u><b>Raw data:</b></u> Plot raw data and pay attention to the random electronic noise, fringes frequency and fringes amplitude vs. electronic noise. Especially the relative amplitude of the electronic noise can impact Gaussian filter performance. <br><br>

<u><b>Tmin and Tmax:</b></u> Find all the minima and maxima positions using Gaussian filter settings. Flattening is applied to the to raw data in order to catch the small vertical oscillations. Transmission corrections for slit width are applied here. Transmission corrections grow fast with the photon energy and the measured transmission. <br><br>

Gaussian filters are required in the search for local minima Tmin and local maxima Tmax in transmission curves with noisy backgrounds. Different spectral parts have different noise levels and therefore different gaussian factor should be applied. For instance, 5 gaussian borders requires 4 gaussian factors resulting in division of the spectrum into 4 parts. It seems easiest to determine gauissian borders and gaussian factors using eV as a unit for the X axis during visual inspection of the raw data. <br>
HIGH gaussian factor = broadband noise filtering. <br>
LOW gaussian factor = narrowband noise filtering. <br>
High gauissian factors (more than 2) will result in relatively large deviation from the raw data. Gaussian factor of zero or near zero (less than 0.5) will follow or almost follow the path of the raw data, respectively. Gaussian borders should be typed in the ascending order and their number of enteries is always one more compared with the number of enteries for the gaussian factors. Interpolation method for the local minima Tmin and the local maxima Tmax can either be linear or spline. <br><br>

<u><b>Std.Dev. in <i>d</i>:</b></u> Minimize dispersion in the film thickness <i>d</i> by ignoring a number of data points using visual graph inspection. By ingonring data points you will change the order number m_start and the mean film thickness <i>d</i>. It seems best practice to ignore number of data points such that the mean film thickness <i>d</i> falls into the region where it is expected to be. <br><br>

<u><b>Index <i>n</i>:</b></u> Plot the refractive index <i>n</i> assuming transparent region <i>n<sub>trans</sub></i> and assuming weak and medium absorption region <i>n<sub>1</sub></i> and correcting <i>n<sub>1</sub></i> for the dispersion in the film thickness <i>d</i> (<i>n<sub>2</sub></i>). <br><br>

<u><b>Absorption <i>alpha</i>:</b></u> Extrapolate the refractive index <i>n<sub>2</sub></i> into the strong absorption region using a polynomial function. The polynomial function is determined by the polyfit order (up to 5th order). Some of the calculated <i>n<sub>2</sub></i> points might not be suitable for the extrapolation. You can exclude these bad points by specifying a range of points you want to include such as [R1<sub>start</sub>,R1<sub>end</sub>,R2<sub>start</sub>,R2<sub>end</sub>,etc.] where R1 refers to the range 1 and R2 refers to the range 2, all values specified in eV. You can also specify more than two ranges, but in most of the cases 1 to 2 ranges is sufficient for a good polyfit. <br><br>

<u><b>Wavenumber <i>k</i>:</b></u> Plot the wavenumber <i>k</i> using the previously calculated value of the absorption <i>alpha</i>.