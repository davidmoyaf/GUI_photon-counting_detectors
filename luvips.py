# /*
# * Name:
# /* luvips.py
# *
# * Description:
# /* Graphical User Interface developed for assessing the performance of photon-counting detectors,
#   specifically designed for the Far-UV detector associated to the WSO-UV space mission.
#   (for further information, check the "readme" document).
# *
# /*
# * Lead Developer:
# /* David Moya
# 
# * Contributors:
# /* Juan C. Vallejo, María Frutos, Ana I. Gómez de Castro.

####################################################################################
####################################################################################

from astropy.io import fits
from astropy.stats import sigma_clipped_stats
import cv2
import glob
from matplotlib import pyplot as plt, colors, cm
from matplotlib.ticker import FixedLocator, FormatStrFormatter
from natsort import natsorted  # External library: to install it, run "pip install natsort" in the command prompt.
import numpy as np
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import os
from pandas import concat, read_excel, ExcelWriter, DataFrame as DF
from photutils.aperture import CircularAperture
from photutils.detection import DAOStarFinder
import seaborn as sns
import subprocess
from threading import Thread
import tkinter as tk
from tkinter import ttk, filedialog as fd, simpledialog as sd, messagebox as mb
import warnings

############################################################################################
############################# DISPLAY OF THE MAIN MENU ####################################
############################################################################################


##### GENERATION OF THE MAIN MENU WINDOW:
########################################
class MainWindow:
    def __init__(self, master):
        self.fr = tk.Frame(master)
        self.fr.pack()
        self.fr.config(bg="gray", bd=30, relief="groove")
        self.master = master

        # Buttons for the different features of the GUI (open functionality + information tab)
        #####################################################################################
        ### 1.- Split video in frames
        ##############################
        readVideo_Button = tk.Button(self.fr, text="Split video in frames", command=self.readVideo)
        readVideo_Button.grid(row=0, column=0, padx=10, pady=10)
        readVideo_Info_Button = tk.Button(self.fr, text="?", fg="gray", bg="black", command=self.readVid_info)
        readVideo_Info_Button.grid(row=0, column=1, padx=10, pady=10)
        ##############################

        ### 2.- Get composite image
        ##########################
        compImage_Button = tk.Button(self.fr, text="Get composite image", command=self.sumIm)
        compImage_Button.grid(row=1, column=0, padx=10, pady=10)
        compImage_Info_Button = tk.Button(self.fr, text="?", fg="gray", bg="black", command=self.sumIm_info)
        compImage_Info_Button.grid(row=1, column=1, padx=10, pady=10)
        ############################

        ### 3.- Split videos in frames + get composite images
        #####################################################
        readVideos_compImages_Button = tk.Button(
            self.fr,
            text="Split videos + get composite images",
            command=self.readVidsCreateSumImages,
        )
        readVideos_compImages_Button.grid(row=2, column=0, padx=10, pady=10)

        readVideoscompImages_Info_Button = tk.Button(
            self.fr, text="?", fg="gray", bg="black", command=self.readVidsCreateSumImages_info
        )
        readVideoscompImages_Info_Button.grid(row=2, column=1, padx=10, pady=10)
        #####################################################

        ### 4.- Test parameters for event extraction
        #############################################
        setDAOparameters_Button = tk.Button(
            self.fr, text="Test parameters for event extraction", command=self.test_parameters
        )
        setDAOparameters_Button.grid(row=3, column=0, padx=10, pady=10)

        setDAOparameters_Info_Button = tk.Button(
            self.fr, text="?", fg="gray", bg="black", command=self.test_parameters_info
        )
        setDAOparameters_Info_Button.grid(row=3, column=1, padx=10, pady=10)
        #############################################

        ### 5.- Extract events
        ######################
        extractEvents_Button = tk.Button(self.fr, text="Extract events", command=self.extr_events)
        extractEvents_Button.grid(row=4, column=0, padx=10, pady=10)
        extractEvents_Info_Button = tk.Button(self.fr, text="?", fg="gray", bg="black", command=self.extr_events_info)
        extractEvents_Info_Button.grid(row=4, column=1, padx=10, pady=10)
        ######################

        ### 6.- Show event spatial distribution
        #######################################
        eventsSpatDistr_Button = tk.Button(self.fr, text="Show event spatial distribution", command=self.ev_sp_distr)
        eventsSpatDistr_Button.grid(row=5, column=0, padx=10, pady=10)
        eventsSpatDistr_Button_Info_Button = tk.Button(
            self.fr, text="?", fg="gray", bg="black", command=self.ev_sp_distr_info
        )
        eventsSpatDistr_Button_Info_Button.grid(row=5, column=1, padx=10, pady=10)
        ########################################

        ### 7.- Show event temporary evolution
        ######################################
        eventsTempEvol_Button = tk.Button(self.fr, text="Show event temporary evolution", command=self.ev_temp_evol)
        eventsTempEvol_Button.grid(row=6, column=0, padx=10, pady=10)
        eventsTempEvol_Button_Info_Button = tk.Button(
            self.fr, text="?", fg="gray", bg="black", command=self.ev_temp_evol_info
        )
        eventsTempEvol_Button_Info_Button.grid(row=6, column=1, padx=10, pady=10)
        ######################################

        ### 8.- Close interface
        #######################
        close_Button = tk.Button(master, text="Close interface", command=self.exit_interface)
        close_Button.pack(pady=10)
        close_Button.configure(cursor="hand2", font=("Verdana", 9, "bold"))
        #####################################################################################

        for widget in self.fr.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(cursor="hand2", font=("Verdana", 9, "bold"))

    def exit_interface(self):
        os._exit(0)

    ########################################

    ##### Generation of the progress bar to appear while any task is being carried out:
    ###################################################################################
    global run_progbar

    def run_progbar():
        global topl
        topl = tk.Toplevel()
        topl.geometry("400x50")
        topl.title("Task in progress")
        progbar = ttk.Progressbar(topl, mode="indeterminate")
        progbar.place(x=50, y=20, width=300)
        progbar.start(20)

    ###################################################################################

    ####################################################################################
    ####################### DISPLAY AND EXECUTION OF THE SUBMENUS ######################
    ####################################################################################

    ## The design architecture of each submenu is primarily based on three functions:
    ## showing an information message, displaying the submenu window and completing the associated tasks.

    ########## 1.- "Split video in frames":
    #######################################
    def readVid_info(self):
        self.master.withdraw()
        _readVid_Info = mb.showinfo(
            title="Split video in frames",
            message=(
                "Processing of a video file (AVI), generating a folder which contains"
                " JPG files corresponding to each of the frames in the video."
            ),
        )
        self.master.deiconify()

    def readVideo(self):
        self.settingsWindow = ReadVideo_SettingsWindow(self.splitVideoInFrames)

    def splitVideoInFrames(self, inDir, outDir):
        def split_Video_Frames():
            self.master.withdraw()
            outputFolder = os.path.join(outDir, os.path.basename(inDir).replace(".avi", ""))
            if not os.path.exists(outputFolder):
                os.makedirs(outputFolder)
            vidcap = cv2.VideoCapture(inDir)
            success, image = vidcap.read()
            count = 1
            while success:
                cv2.imwrite(outputFolder + "/frame-%d.jpg" % count, image)
                success, image = vidcap.read()
                count += 1
            topl.destroy()
            _readVid_Done = mb.showinfo(
                title="Video reading finished",
                message="The splitting of the video into frames has been successfully performed.",
            )
            self.master.deiconify()

        Thread(target=run_progbar).start()
        Thread(target=split_Video_Frames).start()

    ########################################

    ########## 2.- "Get composite image":
    #####################################
    def sumIm_info(self):
        self.master.withdraw()
        _sumIm_Info = mb.showinfo(
            title="Get composite image",
            message="It creates an image resulting of co-adding the signal of a selected set of frames",
        )
        self.master.deiconify()

    def sumIm(self):
        self.settingsWindow = SumImage_SettingsWindow(self.getSumImage)

    def getSumImage(self, option, inDir, outDir, backgDir, name):
        def get_sum_image():
            self.master.withdraw()
            if backgDir:
                file_lastname = "_subtractedBackground_"
                os.chdir(backgDir)
                frames = natsorted(glob.glob("*.jpg"))
                q = len(frames)
                image = plt.imread(frames[0])
                backg = image[:, :, 0].astype(np.int32) / q
                for i in range(1, q):
                    image = plt.imread(frames[i])
                    backg += image[:, :, 0].astype(np.int32) / q
            else:
                file_lastname = ""
                backg = 0

            if option:
                midName = ""
                os.chdir(inDir)
                frames = natsorted(glob.glob("*.jpg"))
                q = len(frames)
                image = plt.imread(frames[0])
                data = image[:, :, 0].astype(np.int32)
                for i in range(1, q):
                    image = plt.imread(frames[i])
                    data += image[:, :, 0].astype(np.int32)
            else:
                first_frame_num = inDir[0].split("frame-")[1].replace(".jpg", "")
                last_frame_num = inDir[-1].split("frame-")[1].replace(".jpg", "")
                midName = "_frames_" + first_frame_num + "-" + last_frame_num
                frames = [f for f in inDir]
                q = len(frames)
                image = plt.imread(frames[0])
                data = image[:, :, 0].astype(np.int32)
                for i in range(1, q):
                    image = plt.imread(frames[i])
                    data += image[:, :, 0].astype(np.int32)

            Data = data - backg
            hdu = fits.PrimaryHDU(Data)
            hdu.writeto(os.path.join(outDir, name) + midName + file_lastname + ".fits", overwrite=True)
            topl.destroy()
            _sumImage_Done = mb.showinfo(
                title="Image integration finished",
                message="The processing of the time-integrated image has been successfully completed.",
            )
            self.master.deiconify()

        Thread(target=run_progbar).start()
        Thread(target=get_sum_image).start()

    #####################################

    ########## 3.- "Split videos + get composite images" :
    ######################################################
    def readVidsCreateSumImages_info(self):
        self.master.withdraw()
        _readVidsSumImages_Info = mb.showinfo(
            title="Split videos + get composite images",
            message=(
                "This option combines the splitting of the video and the generation of its composite image. "
                "Several videos can be treated at once."
            ),
        )
        self.master.deiconify()

    def readVidsCreateSumImages(self):
        self.settingsWindow = ReadVideoandSumImage_SettingsWindow(self.readVideoandCreateSumImage)

    def readVideoandCreateSumImage(self, inDir, outDir):
        def readandgetsumimage():
            def form_composite_image(video_path):
                video = cv2.VideoCapture(video_path)
                accumSignal = None
                while True:
                    success, frame = video.read()
                    if not success:
                        break
                    oneFrameSignal = frame[:, :, 0]
                    if accumSignal is None:
                        accumSignal = np.zeros_like(oneFrameSignal, dtype=np.float32)
                    accumSignal += oneFrameSignal
                video.release()
                return accumSignal

            self.master.withdraw()
            for i in inDir:
                test_name = os.path.basename(i).replace(".avi", "")
                data = form_composite_image(i)
                hdu = fits.PrimaryHDU(data)
                hdu.writeto(os.path.join(outDir, test_name) + ".fits", overwrite=True)
            topl.destroy()
            _readVidsSumImages_Done = mb.showinfo(title="Tasks completed", message="Video(s) sucessfully processed.")
            self.master.deiconify()

        Thread(target=run_progbar).start()
        Thread(target=readandgetsumimage).start()

    ######################################################

    ########## 4.- "Test parameters for event extraction":
    ######################################################
    def test_parameters_info(self):
        self.master.withdraw()
        _testParameters_Info = mb.showinfo(
            title="Test parameters for event extraction",
            message=(
                "It allows the testing in a single frame of the DAOStarFinder algorithm for luminous event detection. "
                "Differents sets of parameters can be tried to refine the process."
            ),
        )
        self.master.deiconify()

    def test_parameters(self):
        self.settingsWindow = TestParameters_SettingsWindow(self.daof)

    def daof(self, inDir, clip, FWHM, thresh):
        def daoFind():
            self.master.withdraw()
            plt.close("all")
            frame_number = os.path.basename(inDir).replace(".jpg", "")
            test_name = os.path.basename(inDir.replace("/" + os.path.basename(inDir), ""))
            image = plt.imread(inDir)
            data = image[:, :, 0]
            numel = np.shape(data)[0] * np.shape(data)[1]
            mean = np.mean(data)
            std = np.std(data)
            lower_clippLim = mean - clip * std
            upper_clippLim = mean + clip * std
            points_in = sum(sum(np.logical_and(data >= lower_clippLim, data <= upper_clippLim)))
            percent = np.round(points_in * 100 / numel, 2)
            mean, median, std = sigma_clipped_stats(data, sigma=clip)
            daofind = DAOStarFinder(fwhm=FWHM, threshold=thresh * std)
            sources = daofind(data - median)
            L = len(sources)
            fig = plt.figure(figsize=(12, 9))
            ax = fig.add_subplot(111)
            positions = np.transpose((sources["xcentroid"], sources["ycentroid"]))
            apertures = CircularAperture(positions, r=4.0)
            apertures.plot(color="blue", lw=1.5, alpha=0.5)
            ax.invert_yaxis()
            ax.imshow(data, norm=colors.LogNorm(), cmap="Blues", origin="upper")
            ax.set_xlabel("X-axis (pix)")
            ax.set_ylabel("Y-axis (pix)")
            ax.set_title(
                (
                    f"Test {test_name}, {frame_number} \n After the sigma-clipping, {percent}% of the total "
                    f"of pixels used for calculating the median (subtracted to the data). \n Number of events detected: {L} \n"
                )
            )
            topl.destroy()
            plt.show()
            self.master.deiconify()

        Thread(target=run_progbar).start()
        Thread(target=daoFind).start()

    ######################################################

    ########## 5.- "Extract events":
    ################################

    def extr_events_info(self):
        self.master.withdraw()
        _extrEvents_Info = mb.showinfo(
            title="Extract events",
            message=(
                "Generation of a XLS table containing the most relevant information about the events "
                "detected in a given set of frames, applying the DAOStarFinder for the entered input parameters."
            ),
        )
        self.master.deiconify()

    def extr_events(self):
        self.settingsWindow = EventExtraction_SettingsWindow(self.extractEvents)

    def extractEvents(self, clip, FWHM, thresh, option, frameFiles, table_path):
        def extract_events():
            self.master.withdraw()
            if option:
                os.chdir(frameFiles)
                frames = natsorted(glob.glob("*.jpg"))
            else:
                frames = [f for f in frameFiles]
                first_frame_num = frameFiles[0].split("frame-")[1].replace(".jpg", "")
            q = len(frames)
            df1 = DF()
            image = plt.imread(frames[0])
            data = image[:, :, 0]
            print("Image clipped basic stats: \n")
            for i in range(q):
                image = plt.imread(frames[i])
                data = image[:, :, 0]
                mean, median, std = sigma_clipped_stats(data, sigma=clip)
                print(
                    f"---------------------------------------- \nFrame {i + 1}): \n \t Mean = ",
                    np.round(mean, 3),
                    "\n \t Median = ",
                    np.round(median, 3),
                    "\n \t Standard deviation = ",
                    np.round(std, 3),
                )
                daofind = DAOStarFinder(fwhm=FWHM, threshold=thresh * std)
                sources = daofind(data - median)
                L = len(sources)
                print("Number of events detected:", L, "\n")
                sources = DF(dict(sources))
                numFrame = (
                    (i + 1) * np.ones((L,), dtype=int)
                    if option
                    else (i + int(first_frame_num)) * np.ones((L,), dtype=int)
                )
                sources.insert(0, "Frame", numFrame)
                df1 = concat([df1, sources])
            df1 = round(df1, 2)
            df1.drop(["sharpness", "roundness1", "roundness2", "mag", "daofind_mag"], axis=1, inplace=True)
            writer = ExcelWriter(table_path)
            paramLine = DF({"Clipping value": clip, "FWHM": FWHM, "Threshold": thresh}, index=[0])
            paramLine.to_excel(writer, index=False)
            headerLine = DF(
                {
                    0: "# Frame",
                    1: "# Event",
                    2: "xCentroid",
                    3: "yCentroid",
                    4: "No. pix",
                    5: "Peak",
                    6: "Flux",
                },
                index=[0],
            )
            headerLine.to_excel(writer, startcol=0, startrow=3, header=None, index=False)
            df1.to_excel(writer, startcol=0, startrow=4, header=None, index=False)
            writer._save()
            wb = load_workbook(table_path)
            ws = wb.active
            for row in ws.iter_rows():
                for cell in row:
                    cell.alignment = Alignment(horizontal="center")
            ws.column_dimensions["A"].width = 15
            ws.column_dimensions["C"].width = 10
            wb.save(table_path)
            topl.destroy()
            _extrEvents_Done = mb.showinfo(
                title="Events table created",
                message="The XLS table containing the list of all events has been completed.",
            )
            self.master.deiconify()

        Thread(target=run_progbar).start()
        Thread(target=extract_events).start()

    ################################

    ########## 6.- "Show event spatial distribution":
    #################################################

    def ev_sp_distr_info(self):
        self.master.withdraw()
        _evSpDistr_Info = mb.showinfo(
            title="Show event spatial distribution",
            message="The spatial distribution of the extracted events is 3-D depicted. "
            "These representation considers the number of events within a cell whose size is given by a predefined grid.",
        )
        self.master.deiconify()

    def ev_sp_distr(self):
        ask = mb.askyesno(
            title="Event info. table already created?",
            message="Have you already generated the XLS event table(s)?",
        )
        if ask:
            self.settingsWindow = EventsSpatialDistrib_SettingsWindow(self.eventsSpatDistr)

    def eventsSpatDistr(self, inDir, imageSize, xi, yi, p):
        def events_Spat_Distr():
            self.master.withdraw()
            XLSfilename = os.path.basename(inDir).replace(".xlsx", "")
            df2 = read_excel(inDir, header=None)
            x = df2.iloc[4 : len(df2), 2]
            y = df2.iloc[4 : len(df2), 3]
            delta = int(imageSize / p)
            n = np.zeros((p, p))
            for i in range(p):
                for j in range(p):
                    maskx = np.logical_and(x > xi + j * delta, x <= xi + (j + 1) * delta)
                    masky = np.logical_and(y > yi + i * delta, y <= yi + (i + 1) * delta)
                    n[i, j] = sum(np.logical_and(maskx, masky))

                ################################# PLOTS ###############################

            xMajorLocator = FixedLocator(np.arange(0, p + 1, 10))
            yMajorLocator = FixedLocator(np.arange(0, p + 1, 10))
            majorFormatter = FormatStrFormatter("%d")
            xMinorLocator = FixedLocator(np.arange(0, p + 1))
            yMinorLocator = FixedLocator(np.arange(0, p + 1))
            X = np.arange(0, p)
            Y = np.arange(0, p)
            X, Y = np.meshgrid(X, Y)
            defaultFigSize = [6.4, 4.8]
            plt.rcParams["figure.figsize"] = [1.75 * x for x in defaultFigSize]

            ######### XY-PLANE

            fig = plt.figure()
            ax = sns.heatmap(n, cmap=cm.Spectral)
            ax.set_xlabel(f"X-Axis (x {delta} pix)")
            ax.set_ylabel(f"Y-Axis (x {delta} pix)")
            ax.set(title="Test " + XLSfilename + ": Spatial distribution of events")
            ax.xaxis.set_major_locator(xMajorLocator)
            ax.yaxis.set_major_locator(yMajorLocator)
            ax.xaxis.set_major_formatter(majorFormatter)
            ax.yaxis.set_major_formatter(majorFormatter)
            ax.xaxis.set_minor_locator(xMinorLocator)
            ax.yaxis.set_minor_locator(yMinorLocator)
            ax.tick_params(which="minor", left=False, bottom=False)
            ax.grid(visible=True, which="both")
            ax.set_aspect("equal")
            plt.xticks(rotation=0)
            plt.yticks(rotation=0)

            fig1, ax1 = plt.subplots(subplot_kw={"projection": "3d"})
            ax1.plot_surface(X, Y, n, cmap=cm.Spectral, linewidth=0, antialiased=False)
            ax1.view_init(elev=90, azim=0, roll=90)
            ax1.set_xlabel(f"X-Axis (x {delta} pix)", labelpad=15)
            ax1.set_ylabel(f"Y-Axis (x {delta} pix)", labelpad=10)
            ax1.tick_params(axis="x", pad=10)
            ax1.set_title("Test " + XLSfilename + ": Spatial distribution of events")
            ax1.xaxis.set_major_locator(xMajorLocator)
            ax1.yaxis.set_major_locator(yMajorLocator)
            ax1.xaxis.set_major_formatter(majorFormatter)
            ax1.yaxis.set_major_formatter(majorFormatter)
            ax1.set_zticklabels([])
            ax1.set_xlim(0, p)
            ax1.set_ylim(0, p)
            ax1.invert_yaxis()
            frame1 = plt.gca()
            frame1.axes.zaxis.set_ticklabels([])

            ########### XZ-PLANE

            fig2, ax2 = plt.subplots(subplot_kw={"projection": "3d"})
            ax2.plot_surface(X, Y, n, cmap=cm.Spectral, linewidth=0, antialiased=False)
            ax2.view_init(elev=0, azim=-90)
            ax2.set_xlabel(f"X-Axis (x {delta} pix)", labelpad=10)
            ax2.set_zlabel("Number of events", labelpad=15)
            ax2.set_title("Test " + XLSfilename + ": Spatial distribution of events along X-axis")
            ax2.xaxis.set_major_formatter(majorFormatter)
            ax2.zaxis.set_major_formatter(majorFormatter)
            ax2.set_yticklabels([])
            ax2.set_xlim(0, p)
            frame2 = plt.gca()
            frame2.axes.yaxis.set_ticklabels([])

            ################ YZ-PLANE

            fig3, ax3 = plt.subplots(subplot_kw={"projection": "3d"})
            ax3.plot_surface(X, Y, n, cmap=cm.Spectral, linewidth=0, antialiased=False)
            ax3.view_init(elev=0, azim=0)
            ax3.set_ylabel(f"Y-Axis (x {delta} pix)", labelpad=10)
            ax3.set_zlabel("Number of events", labelpad=15)
            ax3.set_title("Test " + XLSfilename + ": Spatial distribution of events along Y-axis")
            ax3.yaxis.set_major_formatter(majorFormatter)
            ax3.zaxis.set_major_formatter(majorFormatter)
            ax3.set_xticklabels([])
            ax3.set_ylim(0, p)
            ax3.tick_params(axis="z", pad=10)
            frame3 = plt.gca()
            frame3.axes.xaxis.set_ticklabels([])
            topl.destroy()
            plt.show(block=False)
            plt.pause(1)
            save_option = mb.askyesno(title="Save figures", message="Save generated figures?")
            if save_option:
                outDir = fd.askdirectory(title="Select the folder in which the figures are to be saved")
                heatmap_name = (
                    os.path.join(outDir, XLSfilename)
                    + "_heatmap"
                    + "("
                    + str(delta)
                    + "x"
                    + str(delta)
                    + " pix\u00b2-sized cells).png"
                )
                fig1name = (
                    os.path.join(outDir, XLSfilename)
                    + "_XY_projection"
                    + "_("
                    + str(delta)
                    + "x"
                    + str(delta)
                    + " pix\u00b2-sized cells).png"
                )
                fig2name = (
                    os.path.join(outDir, XLSfilename)
                    + "_XZ_projection"
                    + "_("
                    + str(delta)
                    + "x"
                    + str(delta)
                    + " pix\u00b2-sized cells).png"
                )
                fig3name = (
                    os.path.join(outDir, XLSfilename)
                    + "_YZ_projection"
                    + "_("
                    + str(delta)
                    + "x"
                    + str(delta)
                    + " pix\u00b2-sized cells).png"
                )
                fig.savefig(heatmap_name, bbox_inches="tight", dpi=fig.dpi)
                fig1.savefig(fig1name, bbox_inches="tight", dpi=fig1.dpi)
                fig2.savefig(fig2name, bbox_inches="tight", dpi=fig2.dpi)
                fig3.savefig(fig3name, bbox_inches="tight", dpi=fig3.dpi)
                _evSpDistr_Done = mb.showinfo(title="Figures saved", message="The displayed figures have been saved.")
            plt.show()
            self.master.deiconify()

        Thread(target=run_progbar).start()
        Thread(target=events_Spat_Distr).start()

    #################################################

    ########## 7.- "Show event temporary distribution"
    ##################################################

    def ev_temp_evol_info(self):
        self.master.withdraw()
        _tempEvol_Info = mb.showinfo(
            title="Show event temporal evolution",
            message=(
                "The temporal evolution of the number of detected events "
                "(in terms of the total of events each time period corresponding "
                "to a user-defined number of frames) is plotted."
            ),
        )
        self.master.deiconify()

    def ev_temp_evol(self):
        ask = mb.askyesno(
            title="Event info. table already created?",
            message="Have you already generated the XLS event table(s)?",
        )
        if ask:
            self.settingsWindow = EventsTempEvol_SettingsWindow(self.eventsTempEvol)

    def eventsTempEvol(self, inDirs, imageSize, p, startRow, startCol, endRow, endCol, frameRate, framesPerSubset):
        def events_temp_evol():
            def find_closest_divisor(n, m):
                divisors = np.array([i for i in range(1, int(np.sqrt(n) + 1)) if n % i == 0])
                divisions = n / divisors
                return int(divisions[np.argmin(np.abs(m - divisions))])

            self.master.withdraw()
            totalNumFigs = (endRow - startRow + 1) * (endCol - startCol + 1)
            plt.rcParams["figure.figsize"] = [32, 28]
            for _ in range(totalNumFigs):
                plt.figure(figsize=(8, 6))
            figs = [plt.figure(n) for n in plt.get_fignums()]
            numfig = -1
            for i in range(startRow, endRow + 1):
                for j in range(startCol, endCol + 1):
                    numfig += 1
                    minN = []
                    maxN = []
                    for d in inDirs:
                        XLSfilename = os.path.basename(d).replace(".xlsx", "")
                        df2 = read_excel(d, header=None)
                        f = df2.iloc[4 : len(df2), 0]
                        x = df2.iloc[4 : len(df2), 2]
                        y = df2.iloc[4 : len(df2), 3]
                        numFrames = df2.iloc[len(df2) - 1, 0]
                        Q = find_closest_divisor(numFrames, framesPerSubset)
                        delta = int(imageSize / p)
                        N = np.zeros((int(numFrames / Q),), dtype=int)
                        maskx = np.logical_and(x > j * delta, x <= (j + 1) * delta)
                        masky = np.logical_and(y > i * delta, y <= (i + 1) * delta)
                        pos = [i for i, x in enumerate(np.logical_and(maskx, masky)) if x]
                        for k in range(0, numFrames + 1 - Q, Q):
                            accumEvents = sum(np.logical_and(f[pos] > k, f[pos] <= k + Q))
                            N[int(k / Q)] = accumEvents
                        minN.append(np.min(np.min(N)))
                        maxN.append(np.max(np.max(N)))
                        plt.figure(figs[numfig])
                        plt.plot(
                            np.arange(Q / frameRate, (numFrames + 1) / frameRate, Q / frameRate),
                            N,
                            "-o",
                            label=XLSfilename,
                        )
                        plt.xlabel("Time (s)")
                        plt.ylabel("Number of events")
                        plt.xlim(left=0)
                        plt.ylim(np.min(np.min(minN)) - 20, np.max(np.max(maxN)) + 20)
                        if len(inDirs) > 1:
                            plt.legend()
                            plt.title(
                                "Temporary evolution of events in cell ("
                                + str(i)
                                + ","
                                + str(j)
                                + ") - "
                                + str(p)
                                + "x"
                                + str(p)
                                + "-cell grid"
                            )
                        else:
                            plt.title(
                                'Test "'
                                + XLSfilename
                                + '": \n Temporary evolution of events in cell ('
                                + str(i)
                                + ","
                                + str(j)
                                + ") - "
                                + str(p)
                                + "x"
                                + str(p)
                                + "-cell grid"
                            )

            topl.destroy()
            plt.show(block=False)
            plt.pause(2)
            save_option = mb.askyesno(title="Save figures", message="Save generated figures?")
            if save_option:
                outDir = fd.askdirectory(title="Select the folder in which the figures are to be saved")
                for fig in figs:
                    cell = fig.axes[0].get_title().partition("cell ")[2]
                    fig.savefig(os.path.join(outDir, XLSfilename) + "_" + cell + ".png", bbox_inches="tight")
                    plt.close(fig)
                _tempEvol_Done = mb.showinfo(title="Figures saved", message="The displayed figures have been saved.")
            plt.show()
            self.master.deiconify()

        Thread(target=run_progbar).start()
        Thread(target=events_temp_evol).start()


##################################################

###########################################################################
################### GENERATION OF THE SUBMENUS' WINDOWS ###################
###########################################################################


##### 1.- "Split Video in Frames"
#################################
class ReadVideo_SettingsWindow:
    def __init__(self, splitVideoInFrames):
        self.top = tk.Toplevel()
        self.top.title("Split video in frames")
        self.top.resizable(False, False)
        self.top.geometry("500x150")
        self.splitVideoInFrames = splitVideoInFrames
        self.inDir = None
        self.outDir = None

        _ReadVideo_selectInDir_Label = tk.Label(self.top, text="Select video file to be split into frames:").place(
            x=10, y=10
        )
        _ReadVideo_selectInDir_Button = tk.Button(self.top, text="Select", command=self.selectVideo).place(x=400, y=10)
        _ReadVideo_selectOutDir_Label = tk.Label(
            self.top, text="Select location of the frames folder to be auto-generated:"
        ).place(x=10, y=65)
        _ReadVideo_selectOutDir_Button = tk.Button(self.top, text="Select", command=self.selectOutDir).place(
            x=400, y=60
        )
        self.submitted = False
        _ReadVideoStart_Button = tk.Button(self.top, text="START", command=self.submit).place(x=200, y=115)

        for widget in self.top.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(cursor="hand2")

    def selectVideo(self):
        self.top.withdraw()
        self.inDir = fd.askopenfilename(title="Select video file to be processed", filetypes=[("Video files", ".avi")])
        self.top.deiconify()

    def selectOutDir(self):
        self.top.withdraw()
        self.outDir = fd.askdirectory(title="Select location of the to-be-generated frame folder")
        self.top.deiconify()

    def submit(self):
        if not self.inDir:
            self.top.withdraw()
            _ReadVideo_noVideo_ErrorMsg = mb.showerror(
                title="No video file selected", message="A video file (.avi) must be selected"
            )
            self.top.deiconify()
        elif not self.outDir:
            self.top.withdraw()
            _ReadVideo_noOutDir_ErrorMsg = mb.showerror(
                title="No output directory selected",
                message="An output directory for the to-be-created frame folder must be selected",
            )
            self.top.deiconify()
        else:
            self.top.destroy()
            self.splitVideoInFrames(self.inDir, self.outDir)


#################################


##### 2.- "Get composite image"
###############################
class SumImage_SettingsWindow:
    def __init__(self, getSumImage):
        self.top = tk.Toplevel()
        self.top.title("Get composite image")
        self.top.resizable(False, False)
        self.top.geometry("600x275")
        self.getSumImage = getSumImage
        self.backgDir = None
        self.inDir = None
        self.inDir2 = None
        self.outDir = None
        self.option = True
        self.name = None

        _SumImage_selectInDir_Label = tk.Label(
            self.top, text="Select all the frames in video or subset of frames:"
        ).place(x=10, y=30)
        _SumImage_selectInDir_Button = tk.Button(self.top, text="Select frame folder", command=self.selectFrames).place(
            x=350, y=10
        )
        _SumImage_selectInDir2_Button = tk.Button(
            self.top, text="Select subset of frames", command=self.selectFrameSubset
        ).place(x=350, y=50)
        _SumImage_selectBackgDir_Label = tk.Label(
            self.top, text="Select folder containing dark frames (optional):"
        ).place(x=10, y=120)
        _SumImage_selectBackgDir_Button = tk.Button(
            self.top, text="Select dark frame folder", command=self.selectDarkFrames
        ).place(x=350, y=115)
        _SumImage_BackgInfo_Button = tk.Button(
            self.top, text="?", fg="gray", bg="black", font="bold", command=self.DarkFrames_info
        ).place(x=550, y=115)
        _SumImage_select_InDir_Label = tk.Label(self.top, text="Select location of the composite image:").place(
            x=10, y=170
        )
        _SumImage_selectOutDir_Button = tk.Button(
            self.top, text="Select output directory", command=self.selectOutDir
        ).place(x=350, y=170)
        _SumImage_start_Button = tk.Button(self.top, text="START", command=self.submit).place(x=250, y=240)

        for widget in self.top.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(cursor="hand2")

    def DarkFrames_info(self):
        self.top.withdraw()
        _SumImage_darkFrames_Info = mb.showinfo(
            title="Dark background",
            message=(
                "Select a folder containing frames from a non-lightened measurement. "
                'An average "dark" frame will be calculated and subtracted to each '
                "of the above selected frames to form the composite image."
            ),
        )
        self.top.deiconify()

    def selectDarkFrames(self):
        self.top.withdraw()
        self.backgDir = fd.askdirectory(title="Select dark-frame folder")
        self.top.deiconify()

    def selectFrames(self):
        self.top.withdraw()
        self.inDir = fd.askdirectory(title="Select frame folder")
        self.name = os.path.basename(self.inDir)
        self.top.deiconify()

    def selectFrameSubset(self):
        self.top.withdraw()
        self.option = False
        self.inDir2 = fd.askopenfilenames(title="Select subset of frames", filetypes=[("Frame files", ".jpg")])
        self.name = os.path.basename(self.inDir2[0].replace(os.path.basename(self.inDir2[0]), "")[:-1])
        self.top.deiconify()

    def selectOutDir(self):
        self.top.withdraw()
        self.outDir = fd.askdirectory(title="Select location of the sum image to be generated")
        self.top.deiconify()

    def submit(self):
        if not self.inDir and not self.inDir2:
            self.top.withdraw()
            _SumImage_NoFrames_ErrorMsg = mb.showerror(
                title="No frames selected",
                message="A whole frame folder or a subset of frames must be selected.",
            )
            self.top.deiconify()
        elif not self.outDir:
            self.top.withdraw()
            _SumImage_NoOutDir_ErrorMsg = mb.showerror(
                title="No output directory selected",
                message="A location for the composite image must be selected.",
            )
            self.top.deiconify()
        else:
            self.top.destroy()
            if self.inDir:
                self.getSumImage(self.option, self.inDir, self.outDir, self.backgDir, self.name)
            elif self.inDir2:
                self.getSumImage(self.option, self.inDir2, self.outDir, self.backgDir, self.name)


###############################


##### 3.- "Split Videos + Get Composite Image"
##############################################
class ReadVideoandSumImage_SettingsWindow:
    def __init__(self, readVidsCreateSumImages):
        self.top = tk.Toplevel()
        self.top.title("Split videos + get composite images")
        self.top.resizable(False, False)
        self.top.geometry("350x150")
        self.readVidsCreateSumImages = readVidsCreateSumImages
        self.inDir = None
        self.outDir = None

        _ReadVideoandSumImage_selectInDir_Label = tk.Label(self.top, text="Select video file(s):").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        _ReadVideoandSumImage_selectInDir_Button = tk.Button(self.top, text="Select", command=self.selectVideos).grid(
            row=0, column=1, padx=10, pady=10
        )

        _ReadVideoandSumImage_selectOutDir_Label = tk.Label(self.top, text="Select location of the sum images:").grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        _ReadVideoandSumImage_selectOutDir_Button = tk.Button(self.top, text="Select", command=self.selectOutDir).grid(
            row=1, column=1, padx=10, pady=10
        )

        _ReadVideoandSumImage_Start_Button = tk.Button(self.top, text="START", command=self.submit).place(x=130, y=115)

        for widget in self.top.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(cursor="hand2")

    def selectVideos(self):
        self.top.withdraw()
        self.inDir = fd.askopenfilenames(
            title="Select video file(s) to be processed", filetypes=[("Video files", ".avi")]
        )
        self.top.deiconify()

    def selectOutDir(self):
        self.top.withdraw()
        self.outDir = fd.askdirectory(title="Select location of the composite images to be generated")
        self.top.deiconify()

    def submit(self):
        if not self.inDir:
            self.top.withdraw()
            _ReadVideoandSumImage_noVideo_ErrorMsg = mb.showerror(
                title="No video file selected",
                message="At least one video file (.avi) must be selected.",
            )
            self.top.deiconify()
        elif not self.outDir:
            self.top.withdraw()
            _ReadVideoandSumImage_noOutDir_ErrorMsg = mb.showerror(
                title="No output directory selected",
                message="A location for the composite image(s) must be selected.",
            )
            self.top.deiconify()
        else:
            self.top.destroy()
            self.readVidsCreateSumImages(self.inDir, self.outDir)


##############################################


##### 4.- "Test parameters for event extraction"
################################################
def check_numeric_parameters(window, data):
    values = {}
    type_errors = []
    value_errors = []
    for name, value in data.items():
        try:
            value = float(value.get())
        except (ValueError, TypeError):
            type_errors.append(f'"{name}"')
            continue
        if name == "FWHM" and value <= 0:
            value_errors.append(f'"{name}" must be a positive value.')
        elif (name == "Clipping value" or name == "Threshold") and value < 0:
            value_errors.append(f'"{name}" cannot be a negative value.')
        else:
            values[name] = value
    errors = []
    if type_errors:
        names = ", ".join(type_errors)
        errors.append(f"{names} must be numeric.")
    errors.extend(value_errors)
    if errors:
        window.withdraw()
        _WrongValues_ErrorMsg = mb.showerror(title="Wrong parameter value(s)", message="\n".join(errors))
        window.deiconify()
        return None
    return values


class TestParameters_SettingsWindow:
    def __init__(self, daof):
        self.top = tk.Toplevel()
        self.top.title("Test parameters for event extraction")
        self.top.resizable(False, False)
        self.top.geometry("350x300")
        self.daof = daof
        self.inDir = None

        _TestParameters_selectInDir_Label = tk.Label(self.top, text="Select test frame: ").grid(
            row=0, column=0, padx=20, pady=10, sticky="w"
        )

        _TestParameters_selectInDir_Button = tk.Button(self.top, text="Select", command=self.selectInDir).grid(
            row=0, column=2, padx=20, pady=10
        )

        self.clipValue = tk.StringVar()
        _TestParameters_ClipValue_Setter = tk.Entry(
            self.top, textvariable=self.clipValue, justify="center", width=5
        ).grid(row=1, column=2, padx=20, pady=10)
        _TestParameters_ClipValue_Label = tk.Label(self.top, text="Clipping value: ").grid(
            row=1, column=0, padx=20, pady=10, sticky="w"
        )
        _TestParameters_ClipValue_Info_Button = tk.Button(
            self.top, text="?", bg="black", fg="gray", font="bold", command=self.clip_info
        ).grid(row=1, column=1, padx=20, pady=10)

        self.FWHM = tk.StringVar()
        _TestParameters_FWHM_Setter = tk.Entry(self.top, textvariable=self.FWHM, justify="center", width=5).grid(
            row=2, column=2, padx=20, pady=10
        )
        _TestParameters_FWHM_Label = tk.Label(self.top, text="FWHM: ").grid(
            row=2, column=0, padx=20, pady=10, sticky="w"
        )
        _TestParameters_FWHM_Info_Button = tk.Button(
            self.top, text="?", bg="black", fg="gray", font="bold", command=self.FWHM_info
        ).grid(row=2, column=1, padx=20, pady=10)

        self.thresh = tk.StringVar()
        _TestParameters_Threshold_Setter = tk.Entry(self.top, textvariable=self.thresh, justify="center", width=5).grid(
            row=3, column=2, padx=20, pady=10
        )
        _TestParameters_Threshold_Label = tk.Label(self.top, text="Threshold: ").grid(
            row=3, column=0, padx=20, pady=10, sticky="w"
        )
        _TestParameters_Threshold_Info_Button = tk.Button(
            self.top, text="?", bg="black", fg="gray", font="bold", command=self.thresh_info
        ).grid(row=3, column=1, padx=20, pady=10)

        _TestParameters_Try_Button = tk.Button(self.top, text="TRY", command=self.submit).place(x=150, y=250)

        for widget in self.top.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(cursor="hand2")

    def selectInDir(self):
        self.top.withdraw()
        self.inDir = fd.askopenfilename(title="Select frame for testing", filetypes=[("Frames", ".jpg")])
        self.top.deiconify()

    def clip_info(self):
        self.top.withdraw()
        _TestParameters_ClipValue_Info = mb.showinfo(
            title="Clipping value",
            message=(
                "In sigma-clipping statistics, number of times the standard deviation is "
                "added/subtracted to the mean in order to set both clipping limits. "
                "The median value of the clipped data is subtracted to the original data "
                "before applying the event-finder algorithm."
            ),
        )
        self.top.deiconify()

    def FWHM_info(self):
        self.top.withdraw()
        _TestParameters_FWHM_Info = mb.showinfo(
            title="Full-width at half-maximum (FWHM)",
            message="The size of the events considered will be \n(FWHM + 1)\u00b2 pix",
        )
        self.top.deiconify()

    def thresh_info(self):
        self.top.withdraw()
        _TestParameters_Threshold_Info = mb.showinfo(
            title="Threshold",
            message="Mininimum local signal value (times the data standard deviation) to consider an event.",
        )
        self.top.deiconify()

    def check_input_data(self):
        if not self.inDir:
            self.top.withdraw()
            mb.showerror(title="No frame selected", message="A JPG file containing a frame must be selected.")
            self.top.deiconify()
            return None

        else:
            num_inputs = {"Clipping value": self.clipValue, "FWHM": self.FWHM, "Threshold": self.thresh}
            num_inputs = check_numeric_parameters(self.top, num_inputs)
            if num_inputs is None:
                return

            fwhm = num_inputs["FWHM"]
            clip = num_inputs["Clipping value"]
            thresh = num_inputs["Threshold"]

            return fwhm, clip, thresh, self.inDir

    def submit(self):
        data = self.check_input_data()
        if data is None:
            return
        else:
            fwhm, clip, thresh, inDir = data
            self.daof(inDir, clip, fwhm, thresh)


################################################


##### 5.- "Extract events"
##########################
class EventExtraction_SettingsWindow:
    def __init__(self, extractEvents):
        self.top = tk.Toplevel()
        self.top.title("Extract events")
        self.top.resizable(False, False)
        self.top.geometry("400x300")
        self.extractEvents = extractEvents
        self.imaFolder = None
        self.frameSubset = None
        self.option = True
        self.name = None
        self.outDir = None
        self.tablePath = None

        _EventExtraction_Sigma_Label = tk.Label(self.top, text="Clipping value: ").place(x=40, y=10)
        self.clip = tk.StringVar()
        _EventExtraction_Sigma_Entry = tk.Entry(self.top, textvariable=self.clip, justify="center", width=5).place(
            x=210, y=10
        )

        _EventExtraction_FWHM_Label = tk.Label(self.top, text="FWHM: ").place(x=40, y=55)
        self.FWHM = tk.StringVar()
        _EventExtraction_FWHM_Entry = tk.Entry(self.top, textvariable=self.FWHM, justify="center", width=5).place(
            x=210, y=55
        )

        _EventExtraction_threshold_Label = tk.Label(self.top, text="Threshold: ").place(x=40, y=100)
        self.thresh = tk.StringVar()
        _EventExtraction_threshold_Entry = tk.Entry(
            self.top, textvariable=self.thresh, justify="center", width=5
        ).place(x=210, y=100)

        _EventExtraction_selectFrames_Label = tk.Label(
            self.top, text="Select a frame folder\nor a subset of frames: ", justify="left"
        ).place(x=40, y=140)

        _EventExtraction_selectFrameFolder_Button = tk.Button(
            self.top, text="Select frame folder", command=self.selectFrameFolder
        ).place(x=210, y=130)

        _EventExtraction_selectFrameSubset_Button = tk.Button(
            self.top, text="Select frame subset", command=self.selectFrameSubset
        ).place(x=210, y=160)

        _EventExtraction_selectOutDir_Label = tk.Label(self.top, text="Select output directory: ").place(x=40, y=200)
        _EventExtraction_selectOutDir_Button = tk.Button(self.top, text="Select", command=self.selectOutDir).place(
            x=210, y=200
        )

        _EventExtraction_Start_Button = tk.Button(self.top, text="START EVENT EXTRACTION", command=self.submit).place(
            x=100, y=260
        )

        for widget in self.top.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(cursor="hand2")

    def selectFrameFolder(self):
        self.top.withdraw()
        self.imaFolder = fd.askdirectory(title="Select folder containing the frames whose events will be extracted")
        if self.imaFolder:
            self.name = os.path.basename(self.imaFolder)
        self.top.deiconify()

    def selectFrameSubset(self):
        self.top.withdraw()
        self.frameSubset = fd.askopenfilenames(
            title="Select subset of frames whose events will be extracted",
            filetypes=[("Frames", ".jpg")],
        )
        if self.frameSubset:
            self.option = False
            self.name = os.path.basename(self.frameSubset[0].replace(os.path.basename(self.frameSubset[0]), "")[:-1])
        self.top.deiconify()

    def selectOutDir(self):
        self.top.withdraw()
        self.outDir = fd.askdirectory(title="Select location of the events info. table to be created")
        self.tablePath = os.path.join(self.outDir, self.name) + ".xlsx"
        if os.path.exists(self.tablePath):
            ask = mb.askyesno(
                title="Already existing table in selected path",
                message=(
                    "There is already a table with that name in the selected directory. Would you like to overwrite it?"
                    " (if not, a new directory for the to-be-created table can be chosen)."
                ),
            )
            if not ask:
                while True:
                    newOutDir = fd.askdirectory(title="Select new directory for the event XLS table.")
                    if not newOutDir:
                        return
                    elif newOutDir == self.outDir:
                        _SameDirectory_Warning = mb.showwarning(
                            title="Same directory selected", message="The same directory is being again selected."
                        )
                        continue
                    self.tablePath = os.path.join(newOutDir, self.name) + ".xlsx"
                    break
        self.top.deiconify()

    def check_input_data(self):
        if not self.name:
            self.top.withdraw()
            _NoFramesSelected_ErrorMsg = mb.showerror(
                title="No frames selected",
                message="Select a whole frame folder or a subset of frame files.",
            )
            self.top.deiconify()
            return None

        elif not self.tablePath:
            self.top.withdraw()
            _EventExtraction_NoOutDir_ErrorMsg = mb.showerror(
                title="No output directory selected",
                message="Select directory for the XLS table to be created.",
            )
            self.top.deiconify()
            return None
        else:
            num_inputs = {"Clipping value": self.clip, "FWHM": self.FWHM, "Threshold": self.thresh}
            num_inputs = check_numeric_parameters(self.top, num_inputs)
            if num_inputs is None:
                return

            fwhm = num_inputs["FWHM"]
            clip = num_inputs["Clipping value"]
            thresh = num_inputs["Threshold"]

            return fwhm, clip, thresh, self.tablePath

    def submit(self):
        data = self.check_input_data()
        if data is None:
            return
        else:
            fwhm, clip, thresh, tablePath = data
            if self.imaFolder:
                self.top.destroy()
                self.extractEvents(clip, fwhm, thresh, self.option, self.imaFolder, tablePath)
            elif self.frameSubset:
                self.top.destroy()
                self.extractEvents(clip, fwhm, thresh, self.option, self.frameSubset, tablePath)


##########################


##### 6.- "Show event spatial distribution"
############################################
class EventsSpatialDistrib_SettingsWindow:
    def __init__(self, eventsSpatDistr):
        self.top = tk.Toplevel()
        self.top.title("Show event spatial distribution")
        self.top.resizable(False, False)
        self.top.geometry("400x200")
        self.eventsSpatDistr = eventsSpatDistr
        self.inDir = None

        _EventsSpatialDistrib_selectDetector_Label = tk.Label(self.top, text="Select detector: ").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        self.option = tk.StringVar()
        _EventsSpatialDistrib_option1 = tk.Radiobutton(self.top, value="LUV", text="LUV", variable=self.option).place(
            x=300, y=5
        )
        _EventsSpatialDistrib_option2 = tk.Radiobutton(self.top, value="FM", text="FM", variable=self.option).place(
            x=300, y=25
        )

        _EventsSpatialDistrib_selectInDir_Label = tk.Label(self.top, text="Select XLS table:").grid(
            row=1, column=0, padx=10, pady=20, sticky="w"
        )
        _EventsSpatialDistrib_selectInDir_Button = tk.Button(self.top, text="Select", command=self.selectInDir).grid(
            row=1, column=1, padx=10, pady=10
        )
        _EventsSpatialDistrib_createGrid_Label = tk.Label(
            self.top, text="Select number of cells per grid dimension:", justify="center"
        ).grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.numCells = tk.IntVar()
        _EventsSpatialDistrib_selectInDir_Button = tk.Entry(self.top, textvariable=self.numCells, width=5).grid(
            row=2, column=1
        )

        _EventsSpatialDistrib_Start_Button = tk.Button(self.top, text="START", command=self.submit).place(x=155, y=160)

        for widget in self.top.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(cursor="hand2")

    def selectInDir(self):
        self.top.withdraw()
        self.inDir = fd.askopenfilename(
            title="Select XLS table containing the events",
            filetypes=[("Excel files", ".xlsx .xls")],
        )
        self.top.deiconify()

    def submit(self):
        if not self.inDir:
            self.top.withdraw()
            _EventsSpatialDistrib_NoXLSTable_ErrorMsg = mb.showerror(
                title="No XLS table selected", message="You must select a XLS file."
            )
            self.top.deiconify()
        elif not self.option.get():
            self.top.withdraw()
            _EventsSpatialDistrib_NoDetector_ErrorMsg = mb.showerror(
                title="No detector selected", message='You must select detector ("LUV" or "FM").'
            )
            self.top.deiconify()
        else:
            xi, _xf, yi, yf = [410, 1626, 0, 1216] if self.option == "LUV" else [0, 2048, 0, 2048]
            imageSize = yf - yi
            sizes = [1]
            for i in range(2, imageSize + 1):
                if (imageSize % i) == 0:
                    sizes.append(i)
            if self.numCells.get() not in sizes:
                self.top.withdraw()
                _EventsSpatialDistrib_WrongGridDimValue_ErrorMsg = mb.showerror(
                    title="Wrong grid dimension value",
                    message=f"The number of cells per grid dimension must be"
                    f" one of the following:\n{str(sizes)[1:-1]}.",
                )
                self.top.deiconify()
            else:
                self.top.destroy()
                self.eventsSpatDistr(self.inDir, imageSize, xi, yi, self.numCells.get())


############################################


###### 7.- "Show event temporary evolution"
###########################################
class EventsTempEvol_SettingsWindow:
    def __init__(self, eventsTempEvol):
        self.top = tk.Toplevel()
        self.top.title("Show event temporary evolution")
        self.top.resizable(False, False)
        self.top.geometry("450x450")
        self.eventsTempEvol = eventsTempEvol

        _EventsTempEvol_selectDetector_Label = tk.Label(self.top, text="Select detector: ").place(x=10, y=20)

        self.option = tk.StringVar()
        _EventsTempEvol_selectDetector_option1 = tk.Radiobutton(
            self.top, value="LUV", text="LUV", variable=self.option
        ).place(x=300, y=10)

        _EventsTempEvol_selectDetector_option2 = tk.Radiobutton(
            self.top, value="FM", text="FM", variable=self.option
        ).place(x=300, y=30)

        self.inDirs = []
        _EventsTempEvol_selectInDirs_Label = tk.Label(self.top, text="Select XLS table(s):").place(x=10, y=75)
        _EventsTempEvol_selectInDirs_Button = tk.Button(self.top, text="Select", command=self.selectInDirs).place(
            x=300, y=70
        )

        _EventsTempEvol_selGridSize_Label = tk.Label(self.top, text="Set number of grid cells/dimension: ").place(
            x=10, y=120
        )

        self.p = tk.IntVar()
        _EventsTempEvol_p_Entry = tk.Entry(self.top, textvariable=self.p, justify="center", width=5).place(x=300, y=120)

        _EventsTempEvol_selectROI_Label = tk.Label(self.top, text="Specify region of interest: ").place(x=10, y=150)

        _EventsTempEvol_startRow_Label = tk.Label(self.top, text="* Start Row: ").place(x=30, y=175)

        _EventsTempEvol_startCol_Label = tk.Label(self.top, text="* Start Column: ").place(x=30, y=200)

        _EventsTempEvol_endRow_Label = tk.Label(self.top, text="* End Row: ").place(x=30, y=225)

        _EventsTempEvol_endCol_Label = tk.Label(self.top, text="* End Column: ").place(x=30, y=250)

        self.startRow = tk.IntVar()
        _EventsTempEvol_startRow_Entry = tk.Entry(
            self.top, textvariable=self.startRow, justify="center", width=5
        ).place(x=300, y=175)

        self.startCol = tk.IntVar()
        _EventsTempEvol_startCol_Entry = tk.Entry(
            self.top, textvariable=self.startCol, justify="center", width=5
        ).place(x=300, y=200)

        self.endRow = tk.IntVar()
        _EventsTempEvol_endRow_Entry = tk.Entry(self.top, textvariable=self.endRow, justify="center", width=5).place(
            x=300, y=225
        )

        self.endCol = tk.IntVar()
        _EventsTempEvol_endCol_Entry = tk.Entry(self.top, textvariable=self.endCol, justify="center", width=5).place(
            x=300, y=250
        )

        _EventsTempEvol_frameRate_Label = tk.Label(self.top, text="Enter video frame rate (fps): ").place(x=10, y=370)

        self.frameRate = tk.IntVar()
        _EventsTempEvol_frameRate_Entry = tk.Entry(
            self.top, textvariable=self.frameRate, justify="center", width=5
        ).place(x=300, y=370)

        _EventsTempEvol_setFramesPerSubset_Label = tk.Label(self.top, text="Set number of frames per subset: ").place(
            x=10, y=310
        )

        self.framesPerSubset = tk.IntVar()
        _EventsTempEvol_FramesPerSubset = tk.Entry(
            self.top, textvariable=self.framesPerSubset, justify="center", width=5
        ).place(x=300, y=310)

        _EventsTempEvol_Start_Button = tk.Button(self.top, text="START", command=self.submit).place(x=180, y=415)

        for widget in self.top.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(cursor="hand2")

    def selectInDirs(self):
        self.top.withdraw()
        numTables = sd.askinteger(
            title="Enter number of tables",
            prompt="Enter the number of tests (XLS event tables) to be processed",
        )
        if numTables:
            i = 0
            for _ in range(numTables):
                i += 1
                table = fd.askopenfilename(
                    title="Select XLS table (" + str(i) + "/" + str(numTables) + ")",
                    filetypes=[("Excel files", ".xlsx .xls")],
                )
                self.inDirs.append(table)
        self.top.deiconify()

    def submit(self):
        if not self.inDirs:
            self.top.withdraw()
            _EventsTempEvol_NoXLSTable_ErrorMsg = mb.showerror(
                title="No XLS table(s) selected",
                message="You must select (at least) one XLS file.",
            )
            self.top.deiconify()
        elif not self.option.get():
            self.top.withdraw()
            mb.showerror(title="No detector selected", message='You must select detector ("LUV" or "FM").')
            self.top.deiconify()
        elif (
            self.startRow.get() > self.p.get()
            or self.startCol.get() > self.p.get()
            or self.endRow.get() > self.p.get()
            or self.endCol.get() > self.p.get()
            or self.endCol.get() < self.startCol.get()
            or self.endRow.get() < self.startRow.get()
            or self.startRow.get() == 0
            or self.startCol.get() == 0
            or self.endRow.get() == 0
            or self.endCol.get() == 0
        ):
            self.top.withdraw()
            mb.showerror(
                title="Wrong ROI value(s)",
                message='Wrong value(s) set on \n"region of interest" fields',
            )
            self.top.deiconify()
        elif self.framesPerSubset.get() == 0:
            self.top.withdraw()
            mb.showerror(
                title="No frame-subset length set",
                message="Enter desired number of frames per subset",
            )
            self.top.deiconify()
        elif self.frameRate.get() == 0:
            self.top.withdraw()
            mb.showerror(title="No frame rate value set", message="Enter frame rate value")
            self.top.deiconify()
        else:
            _xi, _xf, yi, yf = [410, 1626, 0, 1216] if self.option == "LUV" else [0, 2048, 0, 2048]
            imageSize = yf - yi
            sizes = [1]
            for i in range(2, imageSize + 1):
                if (imageSize % i) == 0:
                    sizes.append(i)
            if self.p.get() not in sizes:
                self.top.withdraw()
                mb.showerror(
                    title="Wrong grid dimension value",
                    message=f"The number of cells per grid dimension must be"
                    f" one of the following:\n{str(sizes)[1:-1]}.",
                )
                self.top.deiconify()
            else:
                self.top.destroy()
                self.eventsTempEvol(
                    self.inDirs,
                    imageSize,
                    self.p.get(),
                    self.startRow.get(),
                    self.startCol.get(),
                    self.endRow.get(),
                    self.endCol.get(),
                    self.frameRate.get(),
                    self.framesPerSubset.get(),
                )


###########################################


#################################################################
######################## MAIN PROGRAM ############################
##################################################################


def main():
    warnings.simplefilter("ignore", UserWarning)
    subprocess.run(["cls"], shell=True) if os.name == "nt" else subprocess.run(["clear"])  # Terminal cleaning
    root = tk.Tk()
    root.title("Photon-Counting Interface")
    root.config(bg="#743c74", bd=50)
    root.resizable(False, False)
    MainWindow(root)
    root.update_idletasks()
    root.mainloop()


if __name__ == "__main__":
    main()
