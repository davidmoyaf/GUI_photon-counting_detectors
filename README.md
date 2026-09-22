# A GRAPHICAL USER INTERFACE TO EVALUATE THE PERFORMANCE OF PHOTON-COUNTING DETECTORS

## Introduction

The World Space Observatory–Ultraviolet mission (Spektr-UF / WSO-UV) is an efficient multipurpose
orbital observatory for high- and low-resolution spectroscopy, high sensitivity imaging and slitless
spectroscopy in the ultraviolet wavelength range. It will open new opportunities in (exo)planetary
science, extragalactic astronomy, stellar astrophysics and cosmology. The observatory is based on a
complex of scientific instruments including a 170-cm-aperture telescope, spectrographs and imagers.
The latter make up the so-called Field Camera Unit (FCU), consisting of two channels for imaging in
Near-UV (174-305 nm) and Far-UV (115-176 nm) ranges, respectively. <sup>[1]</sup>

The instrument for the Far-UV (FUV) channel of the FCU - manufactured by Photek Ltd. under contract
from SENER Aerospace- is a Microchannel Plate (MCP) photodetector. The mechanism of photon-detection
in this detector is composed of three steps:

- First, a FUV photon strikes a photosensitive CsI substrate and generates an electron that is later
  multiplied by a factor of 10<sup>5</sup> at the MCP level.
- The shower of electrons is converted in a phosphorus interface into photons.
- These photons are which are captured by the optical fibers transporting the signal to a CMOS
  sensor.

  The analog output captured by the CMOS is digitized and sent to external software, which can
  record the digital image for a duration and at a frame rate tunable by the user, thereby
  generating a video in AVI format. <sup>[2]</sup>

## Motivation

Generally, the software that comes with photon-counting detectors is provided with a limited number
of functionalities that are often reduced to managing tools for basic read-out electronics such as
read-out speed, read-time, subframing, etc. For that reason, we came up with the idea and
implemented the design of our Graphical User Interface (GUI), which performs a complete processing
of the videos recorded during the conducted measurements; from the splitting of the aforementioned
videos into frames to the generation of a list of detected light events to further study the spatial
uniformity and temporal stability of the MCP devices in terms of the spatiotemporal distribution of
such events.

Hence, the GUI here presented has been conceived and designed to evaluate the performance of
photon-counting detectors, specifically for the two following models:

- The one above described, intended for being part of the WSO-UV observatory as its FCU-FUV channel.
- A replica -also manufactured by Photek- for testing and characterizing the optical elements
  (lenses and prisms) onboard WSO-UV. This model, mounted in an optical emulator, is located within
  the Laboratory for Vacuum Ultraviolet (LUV), at the Complutense University of Madrid (UCM).
  <sup>[3]</sup>

## Features

The interface presents a Main Menu window with seven possible actions:

- Split video in frames: the recorded video can be selected and then divided into the different
  frames it is composed of. These frames will be stored in an automatically generated folder named
  after the code of the measurement and located under the user choice.
- Get composite image: the frames are co-added to generate a composite image (in FITS format) that
  will be stored where the user desires. In case there is a "dark" background recording (and it has
  been previously split into frames), it is also possible to subtract an average background frame in
  the process of getting the composite image of the original measurement.
- Split videos + get composite images: split at once multiple videos into frames and generate the
  corresponding composite images. In this case, the videos are read but not written (individual
  frames are not saved).
- Test parameters for event extraction: to generate a list of the detected events, the DAOFIND(\*)
  algorithm is used. In this data processing, the value of the three following parameters must first
  be set by the user:
  - Clipping value: number of times the standard deviation is added/subtracted to the mean in order
    to set both clipping limits. The median value of the clipped data is subtracted to the original
    data before applying DAOFIND.
  - FWHM (Full-Width at Half-Maximum): it is directly related to the size (in pixels) of the event
    candidate: size = (FWHM + 1)<sup>2</sup> pix.
  - Threshold: minimal local value of a signal to be considered as an event. The GUI applies the
    algorithm with the selected values in a sample frame -selected by the user of the measurement,
    depicting a graph with the events that are (or not) extracted depending on the values of the
    parameters chosen. Thus, this feature —which can be run as many times as necessary— serves to
    fine-tune the relevant parameters until the most appropriate values are found to extract
    everything that can be considered a light event from each frame of a measurement. Once these
    most suitable parameters are determined, the process can be extended to all the frames in a
    movie via the "Extract events" functionality.
- Extract events: the DAOFIND algorithm is applied to each and every frame of a measurement;
  collecting the data of the extracted events through all frames of the measurement. An XLS table
  listing and classifying the events by the number of frame where they have been detected, the
  spatial coordinates (x,y) of their centroids, as well as their sizes and intensities, will be
  generated and saved.
- Show event spatial distribution: those listed events are again classified depending on its
  location. For that purpose, the CMOS total surface (\*\*) is divided into a matrix (grid-like) is
  defined by the user. The interface will generate a colormap along with cross-sections graphs of
  the relative to the x- and y-axes representing the total amount of events contained in every
  matrix cell.
- Show event temporary evolution: besides, for a specific cell (or subset of cells), the
  time-depending stability of the detector -in terms of the amount of events accumulated each "n"
  frames- can be studied.

(\*) Algorithm widely used in astronomy and designed to search for local density maxima in digital
images in order to detect stars or other point-like objects.

(\*\*) Active CMOS area: 2048 x 2048 pix<sup>2</sup> for the WSO-UV "Flying Model" detector; 1216 x
1216 pix<sup>2</sup> for the replica detector at UCM (the actual area of the sensor is 1836 x 1216
pix<sup>2</sup>; however, only a centered square subarea is selected as the region of interest).

## Technologies

The interface has been fully developed in Python (latest version used: 3.12.6). The libraries
employed include:

- Astropy.
- Cv2.
- Matplotlib.
- NumPy.
- Pandas.
- Photutils.
- Threading.
- Tkinter.

## Utilization

The different functionalities of the GUI have been employed through the optical qualification
campaign of both the "Flying Model" detector<sup>[4]</sup>, as well as in its counterpart for
laboratory testing.

## Acknowledgements

This work has been developed within the framework of the project "Spanish Participation in WSO-UV:
2021-2024", carried out in the Joint Center for Ultraviolet Astronomy by UCM's "AEGORA" Space
Astronomy Research Group and funded by the Spanish Ministry Science and Innovation through grant
PID2020-116726RB-I00.

## References

- [1] M. Sachkov, Ana Inés Gómez de Castro, B. Shustov, et al. "World Space Observatory: ultraviolet
  mission: status 2022", Proc. SPIE 12181, Space Telescopes and Instrumentation 2022: Ultraviolet to
  Gamma Ray, 121812S (31 Aug 2022); https://doi.org/10.1117/12.2629580

- [2] Maria Frutos, David Moya, Juan Carlos Vallejo, Ana I. Goméz de Castro: "An interface to
  evaluate the performance of photon-counting detectors", Proc. SPIE 13093, Space Telescopes and
  Instrumentation 2024: Ultraviolet to Gamma Ray, 130935K (21 Aug 2024);
  https://doi.org/10.1117/12.3019889

- [3] Ana Inés Gómez de Castro, Ernesto Sanchez-Blanco "Small laboratory emulator of the far UV
  imager on board WSO-UV to test the optical performance of the field camera unit FUV channel",
  Proc. SPIE 12181, Space Telescopes and Instrumentation 2022: Ultraviolet to Gamma Ray, 1218132 (31
  Aug 2022); https://doi.org/10.1117/12.2630190

- [4] Ana I. Gómez de Castro, Maria Frutos, David Moya, et al. "Performance qualification of the
  far-ultraviolet detector for the field camera unit on board the Spektr-UF World Space
  Observatory-Ultraviolet space telescope," Journal of Astronomical Telescopes, Instruments, and
  Systems 11(3), 036003 (12 Aug 2025) https://doi.org/10.1117/1.JATIS.11.3.036003

## License

...
