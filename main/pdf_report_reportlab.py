# this is to read the csv file
import pandas as pd

# libraries necessary for generating pdf report
from io import BytesIO  # for storing svg image in memory
from datetime import datetime
from datetime import timedelta
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.platypus import Table
from reportlab.lib.colors import red, black, darkolivegreen
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfbase.pdfmetrics import registerFont  # necessary for Arial font import
from reportlab.pdfbase.ttfonts import TTFont  # necessary for registering arial font
import matplotlib.dates as mdates
# Instead of creating a dummy data, I think it's more realistic to read from a datafile and generate the report
# dat3 = pd.read_csv("sample_data.csv")
import pandas


# pandas.to_datetime(dat3["DateTime"])

# dat2 = dat3.drop(['Barometric Pressure'], axis=1)
# dat1 = dat2.drop(['Relative Humidity'], axis=1)

# print(type(dat3))
# print(dat3)
# print(dat2)
# print(dat1)




# let's create a dummy dataset containing date-time, temp, rh, bmp

# date_time = pd.date_range(datetime.now(), datetime.now() + timedelta(1), freq='H')
# temp = np.random.randint(-10, 30, 25)
# rh = np.random.randint(5, 95, 25)
# bmp = np.random.randint(900, 1050, 25)
# alr = np.random.randint(0,1,25)
#
# # combining variables into a dataframe
# dat1 = pd.DataFrame({"DateTime": date_time,
#                     'Temperature': temp})
#
# dat2 = pd.DataFrame({"DateTime": date_time,
#                     'Temperature': temp,
#                     'Relative Humidity': rh
#                     })
#
# datx = pd.DataFrame({"DateTime": date_time,
#                     'Temperature': temp,
#                     'Relative Humidity': rh,
#                     'Barometric Pressure': bmp,
#                      'Alarm': alr
#                     })

'''
Before feeding data into the following function, it's variables should have the following format:
-----------------------------
Date-Time              object
Temperature             int64
Relative Humidity       int64
Barometric Pressure     int64
Alarm                   int64
dtype: object
'''




# function to generate pdf from data file
def generateReport(df,filepath = "report.pdf", dev_name="custom dev name", dev_model="CSL-H2 T0.2",
                    t_alarm_lo=-999, t_alarm_hi=-999,
                    rh_alarm_lo=-999, rh_alarm_hi=-999,
                    bmp_alarm_lo=-999, bmp_alarm_hi=-999, ):
    #  calculating summary statistics and format the output after excluding the alarm
    df1 = df.iloc[:, :-1]  # Alarm is the last column
    sumStat = df1.describe().round().T.reset_index()  # cal summary stats, round, transpose df, and resets row index
    sumStat.columns.values[0] = 'variable(s)'  # adding variable names

    # setting fonts for the plot
    font = {'family': 'Arial', 'size': 9}
    plt.rc('font', **font)
    plt.style.use('default')
    # changing line thickness in plots (globally)
    plt.rcParams['lines.linewidth'] = 0.75

    # creating the PDF report
    registerFont(TTFont('Arial', 'ARIAL.ttf'))  # arial is usually not a registered font, thus needs to be registered

    # file_name = dev_name + "_summary_report" + ".pdf"  # generating file name
    my_report = canvas.Canvas(filepath, pagesize=letter)  # creating a letter size canvas

    # headline
    my_report.setFont('Arial', 18)
    my_report.drawString(x=215, y=720, text="SUMMARY REPORT")

    # device model in the main headline
    my_report.setFont('Arial', 10)
    dev_id_txt = "Device: " + dev_model
    my_report.drawString(x=250, y=703, text=dev_id_txt)

    # report generation date in the main headline
    my_report.drawString(x=225, y=690, text="Generated on: " + datetime.now().strftime("%Y-%b-%d %H:%M"))

    # custom device name
    dev_name_txt = "Device Name: " + dev_name
    my_report.drawString(x=75, y=668, text=dev_name_txt)

    # total number of alarms
    alarm_txt = "ALARM COUNTS: " + str(df["Alarm"].sum(axis=0))
    my_report.drawString(x=440, y=668, text=alarm_txt)

    # header ending horizontal lines
    my_report.line(x1=75, y1=663, x2=540, y2=665)
    my_report.line(x1=75, y1=660, x2=540, y2=662)

    # logging started in the sub-header
    my_report.setFont('Arial', 11)
    start_time = df['DateTime'][0]
    my_report.setFillColor(darkolivegreen)
    my_report.circle(x_cen=80, y_cen=651, r=5, stroke=False, fill=1)
    my_report.setFillColor(black)
    my_report.drawString(x=100, y=647, text="Logging Started: " + start_time.strftime("%d %b %Y, %H:%M"))

    # logging ended in the sub-header
    end_time = df['DateTime'][len(df.index) - 1]
    my_report.setFillColor(red)
    my_report.circle(x_cen=344, y_cen=651, r=5, stroke=False, fill=1)
    my_report.setFillColor(black)
    my_report.drawString(x=360, y=647, text="Logging Ended: " + end_time.strftime("%d %b %Y, %H:%M"))

    # ending line of sub-header
    my_report.line(x1=75, y1=641, x2=540, y2=643)

    # crate body headline for summary statistics
    my_report.setFont('Arial', 12)
    my_report.rect(x=75, y=618, width=8, height=8, stroke=1, fill=1)
    my_report.drawString(x=93, y=618, text="Summary Statistics:")

    # table headers for the summary statistics
    my_report.setFont('Arial', 11)
    my_report.drawString(x=75, y=590, text="Variable(s)")
    my_report.drawString(x=175, y=590, text="Count")
    my_report.drawString(x=225, y=590, text="Mean")
    my_report.drawString(x=270, y=590, text="Std.")
    my_report.drawString(x=320, y=590, text="Min")
    my_report.drawString(x=360, y=590, text="25%")
    my_report.drawString(x=405, y=590, text="50% ")
    my_report.drawString(x=450, y=590, text="75%")
    my_report.drawString(x=495, y=590, text="Max")
    my_report.line(x1=75, y1=580, x2=537, y2=580)

    # number of ticks in common x-axis
    xticker = mticker.MaxNLocator(3)

    # create summary statistics table and add overview graph
    if len(sumStat.index) == 1:  # for one-variable data-logger
        tbl = Table(np.array(sumStat).tolist(), rowHeights=[25], colWidths=[100, 50, 45, 45, 45, 45, 45, 45, 45])
        tbl.setStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "LEFT")])  # table formatting

        # table size and positioning
        tbl.wrapOn(my_report, 300 * mm, 300 * mm)
        tbl.drawOn(my_report, x=25 * mm, y=193 * mm)  # low y lowers position in y-axis

        # plotting the two-variable data
        fig, ax1 = plt.subplots(1, 1, sharex=True)  # shared x-axis

        # plotting the single variable data
        ax1.plot(df["DateTime"], df[df.columns[1]], color="#f37738")
        ax1.set_ylabel(df.columns[1], fontsize=9)
        # plotting horizontal lines for alarm upper and lower limits for one-variable loggers
        # Although it's just temp now, I wanted to have this part a bit future proof
        if sum(df.columns == "Temperature") == 1 and t_alarm_lo != -999 and t_alarm_hi != -999:

            ax1.set_yticks([t_alarm_lo, t_alarm_hi])
            ax1.axhline(y=t_alarm_lo, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax1.axhline(y=t_alarm_hi, c="grey", linewidth=0.5, linestyle="--", zorder=0)

        elif sum(df.columns == "Relative Humidity") == 1 and rh_alarm_lo != -999 and rh_alarm_hi != -999:
            ax1.axhline(y=rh_alarm_lo, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax1.axhline(y=rh_alarm_hi, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax1.set_yticks([min(df["Relative Humidity"]), max(df["Relative Humidity"]), rh_alarm_lo, rh_alarm_hi])

        elif sum(df.columns == "Barometric Pressure") == 1 and bmp_alarm_lo != -999 and bmp_alarm_hi != -999:
            ax1.axhline(y=bmp_alarm_lo, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax1.axhline(y=bmp_alarm_lo, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax1.set_yticks([min(df["Barometric Pressure"]), max(df["Barometric Pressure"]), bmp_alarm_lo, bmp_alarm_hi])

        # setting ticks in common x-axis
        ax1.xaxis.set_major_locator(xticker)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %y, %H:%M'))
        plt.xlabel("Date-Time", fontsize=9)
        ax1.tick_params(axis='both', which='major', labelsize=9)

    elif len(sumStat.index) == 2:  # for two-variable data-logger
        tbl = Table(np.array(sumStat).tolist(), rowHeights=[25, 25], colWidths=[100, 50, 45, 45, 45, 45, 45, 45, 45])
        tbl.setStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "LEFT")])  # table formatting
        # table size and positioning
        tbl.wrapOn(my_report, 300 * mm, 300 * mm)
        tbl.drawOn(my_report, x=25 * mm, y=184 * mm)

        # plotting the two-variable data
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)  # shares x-axis

        # plotting first variable data
        ax1.plot(df["DateTime"], df[df.columns[1]], color="#f37738")
        ax1.set_ylabel(df.columns[1])

        # plotting second variable data
        ax2.plot(df["DateTime"], df[df.columns[2]], color="#7b85d4")
        ax2.set_ylabel(df.columns[2])

        # plotting horizontal lines for alarm upper and lower limits for two-variable loggers
        # for now  it's just temperature and relative humidity
        # TODO: add new variables as new data loggers are desinged
        if (sum(np.isin(["Temperature", "Relative Humidity"], df.columns)) == 2) and \
                t_alarm_lo != -999 and t_alarm_hi != -999 and rh_alarm_lo != -999 and rh_alarm_hi != -999:
            ax1.axhline(y=t_alarm_lo, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax1.axhline(y=t_alarm_hi, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax1.set_yticks([t_alarm_lo, t_alarm_hi])

            ax2.axhline(y=rh_alarm_lo, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax2.axhline(y=rh_alarm_hi, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax2.set_yticks([rh_alarm_lo, rh_alarm_hi])

        # setting ticks in common x-axis
        ax2.xaxis.set_major_locator(xticker)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %y, %H:%M'))
        plt.xlabel("Date-Time")
        ax1.tick_params(axis='both', which='major', labelsize=9)
        ax2.tick_params(axis='both', which='major', labelsize=9)

    elif len(sumStat.index) == 3:  # for three-variables data-logger
        tbl = Table(np.array(sumStat).tolist(), rowHeights=[25, 25, 25],
                    colWidths=[100, 50, 45, 45, 45, 45, 45, 45, 45])
        tbl.setStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "LEFT")])  # table formatting

        # table size and positioning
        tbl.wrapOn(my_report, 300 * mm, 300 * mm)
        tbl.drawOn(my_report, x=25 * mm, y=176 * mm)

        # plotting the three-variable data
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)  # shares x-axis

        # plotting first variable data
        ax1.plot(df["DateTime"], df[df.columns[1]], color="#f37738")
        ax1.set_ylabel(df.columns[1])

        # plotting second variable data
        ax2.plot(df["DateTime"], df[df.columns[2]], color="#7b85d4")
        ax2.set_ylabel(df.columns[2])

        # plotting third variable data
        ax3.plot(df["DateTime"], df[df.columns[3]], color="#83c995")
        ax3.set_ylabel(df.columns[3])

        # plotting horizontal lines for alarm upper and lower limits for two-variable loggers
        # for now  it's just temperature relative humidity, and barometric pressure
        # TODO: add new variables as new data loggers are desinged
        if (sum(np.isin(["Temperature", "Relative Humidity", "Barometric Pressure"], df.columns)) == 3) and \
                t_alarm_lo != -999 and t_alarm_hi != -999 and rh_alarm_lo != -999 and rh_alarm_hi != -999 and \
                bmp_alarm_lo != -999 and bmp_alarm_hi != -999:
            ax1.axhline(y=t_alarm_lo, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax1.axhline(y=t_alarm_hi, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax1.set_yticks([t_alarm_lo, t_alarm_hi])

            ax2.axhline(y=rh_alarm_lo, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax2.axhline(y=rh_alarm_hi, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax2.set_yticks([rh_alarm_lo, rh_alarm_hi])

            ax3.axhline(y=bmp_alarm_lo, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax3.axhline(y=bmp_alarm_hi, c="grey", linewidth=0.5, linestyle="--", zorder=0)
            ax3.set_yticks([bmp_alarm_lo, bmp_alarm_hi])

        # setting ticks in common x-axis
        ax3.xaxis.set_major_locator(xticker)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %y, %H:%M'))
        plt.xlabel("Date-Time")
        ax1.tick_params(axis='both', which='major', labelsize=9)
        ax2.tick_params(axis='both', which='major', labelsize=9)
        ax3.tick_params(axis='both', which='major', labelsize=9)

    else:
        print("Generation of summary stats failed due to sumStat row number mismatch")

    # set-up tight figure layout
    fig.tight_layout()
    fig.set_size_inches(5.5, 4.5)  # width, height

    # save the figure to SVG format in memory
    temp_svg_file = BytesIO()
    plt.savefig(temp_svg_file, format='SVG', dpi=90)

    #  plotting the graphical data overview
    #  graphical data overview headline
    my_report.setFont('Arial', 12)
    my_report.rect(x=75, y=460, width=8, height=8, stroke=1, fill=1)
    my_report.drawString(x=93, y=460, text="Graphical Data Overview:")

    # rewind the file for reading, and convert to a Drawing.
    temp_svg_file.seek(0)

    # reading the temporarily saved image and adding it to the pdf report
    renderPDF.draw(svg2rlg(temp_svg_file), my_report, x=65, y=50)

    # generate report and save it
    my_report.showPage()
    my_report.save()
    plt.style.use('ggplot')

# testing
# generate_report(df=datx, t_alarm_lo=-5, t_alarm_hi=20, rh_alarm_lo=30, rh_alarm_hi=90, bmp_alarm_lo=980,
#                 bmp_alarm_hi=1010)
# generate_report(df=dat2, t_alarm_lo=-5, t_alarm_hi=20, rh_alarm_lo=30, rh_alarm_hi=70)
# generate_report(df=dat1, t_alarm_lo=-5, t_alarm_hi=20)