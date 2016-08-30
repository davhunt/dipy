"""
==========================================================================
Using the free water elimination model to remove free water contamination
==========================================================================

As shown previously (see :ref:`example_reconst_dti`), the diffusion tensor
model is a simple way to characterize the diffusion anisotropy. However, this
model is not specific to particular type of tissue. For example, diffusion
anisotropy in regions near the cerebral ventricle and parenchyma can be
underestimated by partial volume effects of the cerebral spinal fluid (CSF).
This free water contamination can particularly corrupt diffusion tensor imaging
analysis of microstructural changes when different groups of subject show
different brain morphology (e.g. brain ventricle enlargement associated with
brain tissue atrophy that occurs in several brain pathologies and ageing).

A way to remove this free water influences is to expand the DTI model to take
into account an extra compartment representing the contributions of free water
diffusion. The expression of the expanded DTI model is shown below:

.. math::

    S(\mathbf{g}, b) = S_0(1-f)e^{-b\mathbf{g}^T \mathbf{D}
    \mathbf{g}}+S_0fe^{-b D_{iso}}

where $\mathbf{g}$ and $b$ are diffusion grandient direction and weighted
(more information see :ref:`example_reconst_dti`), $S(\mathbf{g}, b)$ is the
diffusion-weighted signal measured, $S_0$ is the signal conducted in a
measurement with no diffusion weighting, $\mathbf{D}$ is the diffusion tensor,
$f$ the volume fraction of the free water component, and $D_iso$ is the
isotropic value of the free water diffusion (normally set to $3.0 \times
10^{-3} mm^{2}s^{-1}$).

In this example, we show how to process a diffusion weighted dataset using the
free water elimantion.

Let's start by importing the relevant modules:
"""

import numpy as np
import dipy.reconst.fwdti as fwdti
import dipy.reconst.dti as dti
import matplotlib.pyplot as plt
from dipy.data import fetch_cenir_multib
from dipy.data import read_cenir_multib
from dipy.segment.mask import median_otsu

"""
Without spatial constrains the free water elimination model cannot be solved
in data acquired from one non-zero b-value _[Hoy2014]. Therefore, here we
download a dataset that was required from multi b-values.
"""

fetch_cenir_multib(with_raw=False)

"""
From the downloaded data, we read only the data acquired with b-values up to
2000 $s.mm^{-2} to decrease the influence of non-Gaussain _[Hoy2014].
"""

bvals = [200, 400, 1000, 2000]

img, gtab = read_cenir_multib(bvals)

data = img.get_data()

affine = img.get_affine()

"""
The free water DTI model can take some minutes to process the full data set.
Thus, we remove the background of the image to avoid unnecessary calculations.
"""

maskdata, mask = median_otsu(data, 4, 2, False, vol_idx=[0, 1], dilate=1)

"""
Moreover, for illustration purposes we process only an axial slice of the
data.
"""

axial_slice = 40

mask_roi = np.zeros(data.shape[:-1], dtype=bool)
mask_roi[:, :, axial_slice] = mask[:, :, axial_slice]

"""
The free water elimantion model fit can then be initialized by instantiating
a FreeWaterTensorModel class object:
"""

fwdtimodel = fwdti.FreeWaterTensorModel(gtab, 'NLS', cholesky=False)

"""
The data can then be fitted using the ``fit`` function of the defined model
object:
"""

fwdtifit = fwdtimodel.fit(data, mask=mask_roi)


"""
This 2-steps procedure will create a FreeWaterTensorFit object which contains
all the diffusion tensor statistics free for free water contaminations. Below
we extract the fractional anisotropy (FA) and the mean diffusivity (MD) of the
free water diffusion tensor."""

FA = fwdtifit.fa
MD = fwdtifit.md
AD = fwdtifit.ad
RD = fwdtifit.rd

"""
For comparison we also compute the same standard measures processed by the
standard DTI model
"""

dtimodel = dti.TensorModel(gtab)

dtifit = dtimodel.fit(data, mask=mask_roi)

dti_FA = dtifit.fa
dti_MD = dtifit.md

"""
Below the FA values for both free water elimnantion DTI model and standard DTI
model are ploted in panels A and B, while the repective MD values are ploted in
panels D and E. For a better visualization of the effect of the free water
correction, the differences between these two metrics are shown in panels C and
E. In addition to the standard diffusion statistics, the estimated volume
fraction of the free water contamination is shown on panel G.
"""

fig1, ax = plt.subplots(2, 4, figsize=(12, 6),
                        subplot_kw={'xticks': [], 'yticks': []})

fig1.subplots_adjust(hspace=0.3, wspace=0.05)
ax.flat[0].imshow(FA[:, :, axial_slice].T, origin='lower',
                  cmap='gray', vmin=0, vmax=1)
ax.flat[0].set_title('A) fwDTI FA')
ax.flat[1].imshow(dti_FA[:, :, axial_slice].T, origin='lower',
                  cmap='gray', vmin=0, vmax=1)
ax.flat[1].set_title('B) standard DTI FA')

FAdiff = abs(FA[:, :, axial_slice] - dti_FA[:, :, axial_slice])
ax.flat[2].imshow(FAdiff.T, cmap='gray', origin='lower', vmin=0, vmax=1)
ax.flat[2].set_title('C) FA difference')

ax.flat[3].axis('off')

ax.flat[4].imshow(MD[:, :, axial_slice].T, origin='lower',
                  cmap='gray', vmin=0, vmax=2.5e-3)
ax.flat[4].set_title('D) fwDTI MD')
ax.flat[5].imshow(dti_MD[:, :, axial_slice].T, origin='lower',
                  cmap='gray', vmin=0, vmax=2.5e-3)
ax.flat[5].set_title('E) standard DTI MD')

MDdiff = abs(MD[:, :, axial_slice] - dti_MD[:, :, axial_slice])
ax.flat[6].imshow(MDdiff.T, origin='lower', cmap='gray', vmin=0, vmax=2.5e-3)
ax.flat[6].set_title('F) MD difference')

F = fwdtifit.f

ax.flat[7].imshow(F[:, :, axial_slice].T, origin='lower',
                  cmap='gray', vmin=0, vmax=1)
ax.flat[7].set_title('G) free water volume')

plt.show()
fig1.savefig('In_vivo_free_water_DTI_and_standard_DTI_measures.png')

"""
.. figure:: In_vivo_free_water_DTI_and_standard_DTI_measures.png
   :align: center
   ** In vivo diffusion measures obtain from the free water DTI and standard
   DTI. The values of Fractional Anisotropy for the free water DTI model and
   standard DTI model and their difference are shown in the upper panels (A-C),
   while respective MD values are shown in the lower panels (D-F). In addition
   the free water volume fraction estimated from the fwDTI model is shown in
   panel G**.

References:

.. [Hoy2014] Hoy, A.R., Koay, C.G., Kecskemeti, S.R., Alexander, A.L., 2014.
             Optimization of a free water elimination two-compartmental model
             for diffusion tensor imaging. NeuroImage 103, 323-333.
             doi: 10.1016/j.neuroimage.2014.09.053
"""
