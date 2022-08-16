#!/usr/bin/env python2
from __future__ import division
import math
import numpy as np
import numpy.linalg
from mpl_toolkits import mplot3d
from matplotlib import pyplot as plt
import scipy
import pandas as pd
import os
import six
from pandas.plotting import table
from scipy.spatial import distance
from scipy.stats import weibull_max, lognorm, chi2, loggamma, skew
import seaborn as sns
from matplotlib.lines import Line2D
import os
HOME = os.getenv("HOME")

destination = ''


pd.set_option('display.max_columns',10)
pd.set_option('display.width',300)

#imports impingement analysis data that is created by the mass planner
def getdata(filename):
    info = pd.read_csv(filename, sep =',',header = None, nrows = 2)
    #print info
    s = str(info[1][0])
    result = ''.join([i for i in s if not i.isdigit()])
    partname = result.strip('.')
    slicewidth = info[3][0]
    adapttype = info[0][1]
    statmethod = info[1][1]

    #print partname, ' ',adapttype, ' ', statmethod, ' ', slicewidth

    adapttype, statmethod, partname =  rearrange_data(adapttype, statmethod, partname)
    treatment = [adapttype,statmethod,partname]

    #print filename
    data = pd.read_csv(filename, sep =',', skiprows = [0,1],index_col = 0)
    data['Part Name'] = partname
    data['Slice Width'] = slicewidth
    data['Adaptive Algorithm'] = adapttype
    data['Statistical Method'] = statmethod
    data['Index'] = data.index

    trim_uncovered = data['Time Value'] != 0.0
    data = data[trim_uncovered]

    dummydata = data.copy()

    dummydata.set_index(['Part Name','Slice Width','Adaptive Algorithm','Statistical Method','Index'],inplace=True)
    dummydata = dummydata[['Combined Value']]

    title = str(partname)+' sliced at '+str(slicewidth)+'\nAdapt Based On '+adapttype+'   Using '+statmethod

    figdummy = destination+partname+adapttype+statmethod+str(slicewidth)

    fit_data = fit_curves(dummydata,title,figdummy+'FittedCurves.png')
    #print 'Fit_data',fit_data
    #print dummydata
    threshold_result = thresholdcalc(dummydata)

    skew = scipy.stats.skew(list(dummydata[dummydata.columns[0]]))

    figname = destination+partname+adapttype+statmethod+str(slicewidth)+'SummaryStats.png'
    sumstats = ['Count','Mean','Std Dev','Min','25%','50%','75%','Max']
    tabledata = dummydata.describe()
    labels = ['Stat']
    dummylabels = list(tabledata.columns)
    for i in range(len(dummylabels)):
        labels.append(dummylabels[i])
    tabledata['Stat'] = sumstats
    tabledata = tabledata[labels]
    
    #prints chart of summary stats, only useful if needed for a presentation
    #render_mpl_table(tabledata,title, figname, col_width = 3.0, header_columns=0)

    figname = destination+partname+adapttype+statmethod+str(slicewidth)+'KDE.png'
    mx = float(np.percentile(dummydata.values,95)/19)

    #builds plot for individual treatments
    sns.distplot(dummydata, hist=True, kde=True, rug = False, bins=50, color = 'blue', hist_kws={'edgecolor':'black'}, kde_kws={'linewidth': 2})#.set(xlim=(-mx,22*mx))
    #sns.plt.xlim(-mx,21*mx)

    plt.title(title, fontsize=12)
    plt.xlabel('Impingement Value')
    plt.ylabel('Density')
    plt.savefig(figname)
    plt.close()
    #plt.show()

    return data, tabledata, fit_data, treatment, threshold_result, skew

#returns the number of facets meeting a certain threshhold;not used in analysis
def thresholdcalc(data):
    global threshold
    data = list(data[data.columns[0]])
    l = len(data)
    #print 'l',l
    above = 0
    below = 0
    for x in range(l):
        if data[x] > threshold:
            above += 1
        if data[x] <= threshold:
            below += 1

    percent = above/l

    return percent

#combines all of the relevant data by part and treatment into a single dataframe to compare across any variable
def build_compare_df(Treatments, Sumstats, Fitstats, thresholds, Skews, binmetric,PathStats):
    t = len(Treatments)
    s = len(Sumstats)
    f = len(Fitstats)
    th = len(thresholds)
    sk = len(Skews)
    b = len(binmetric)
    if t != s or t != f or t != th or t != sk or t != b:
        print "Error: No Comparison Possible, lengths do not match"
        return

    #print 'lengths ', t, s, f
    #print Treatments
    #print Sumstats
    #print Fitstats

    sumstat = Sumstats[0]
    s = sumstat['Combined Value'].tolist()
    #print sumstat
    #print s

    for x in range(len(PathStats)):
        if PathStats[x][0][0] == Treatments[0][0] and PathStats[x][0][1] == Treatments[0][1]:
            pathstat = PathStats[x]

    #print Treatments[0][2],Treatments[0][0],Treatments[0][1],s[0],s[1],s[2],s[3],s[4],s[5],s[6],s[7],Fitstats[0][0],Fitstats[0][1],Fitstats[0][2],Fitstats[0][3]

    compare_df = pd.DataFrame([[Treatments[0][2],Treatments[0][0],Treatments[0][1],s[0],s[1],s[2],s[3],s[4],s[5],s[6],s[7],Fitstats[0][0],Fitstats[0][1],Fitstats[0][2],Fitstats[0][3],thresholds[0],Skews[0], binmetric[0][1],pathstat[1],pathstat[2]]],columns = ['Part Name','Adaptive Algorithm','Statistical Method','Count','Mean','Std Dev','Min','25th Percentile','50th Percentile','75th Percentile','Max','Fitted Mean','Fitted Variance','Fitted Skew','Fitted Kurtosis','Threshold Percentage','Data Skew', 'Bin Metric', 'Total Path Time', 'Total Path Length'])


    for x in range(1,t):
        for y in range(len(PathStats)):
            if PathStats[y][0][0] == Treatments[x][0] and PathStats[y][0][1] == Treatments[x][1]:
                pathstat = PathStats[y]
        sumstat = Sumstats[x]
        s = sumstat['Combined Value'].tolist()
        middf = pd.DataFrame([[Treatments[x][2],Treatments[x][0],Treatments[x][1],s[0],s[1],s[2],s[3],s[4],s[5],s[6],s[7],Fitstats[x][0],Fitstats[x][1],Fitstats[x][2],Fitstats[x][3],thresholds[x],Skews[x], binmetric[x][1],pathstat[1],pathstat[2]]],columns = ['Part Name','Adaptive Algorithm','Statistical Method','Count','Mean','Std Dev','Min','25th Percentile','50th Percentile','75th Percentile','Max','Fitted Mean','Fitted Variance','Fitted Skew','Fitted Kurtosis','Threshold Percentage','Data Skew','Bin Metric', 'Total Path Time', 'Total Path Length'])

        compare_df = compare_df.append(middf)


    #print 'Compare DF\n',compare_df

    newfilename = destination + Treatments[0][2] + 'FullComparison.csv'

    #print compare_df

    return compare_df, newfilename

#pulls summary stats that were output from the mass planner
def getstats(filename):
    global destination
    info = pd.read_csv(filename, sep =',',header = None, nrows = 2)
    #print info
    s = str(info[1][0])
    result = ''.join([i for i in s if not i.isdigit()])
    partname = result.strip('.')
    slicewidth = info[3][0]
    adapttype = info[0][1]
    statmethod = info[1][1]

    adapttype, statmethod, partname =  rearrange_data(adapttype, statmethod, partname)

    title = str(partname)+' sliced at '+str(slicewidth)+'\nAdapt Based On '+adapttype+'   Using '+statmethod

    treatment = [adapttype,statmethod,partname]

    stats = pd.read_csv(filename, sep =',', skiprows = [0,1],header=None,nrows=5)
    stats['Stats'] = stats[0]
    stats.rename(columns = {1:'Value'},inplace = True)
    percentage = pd.read_csv(filename, sep =',', skiprows = [0,1,2,3,4,5,6],header=None)
    percentage.drop([2,3,4],axis=1,inplace=True)    
    percentage.rename(columns = {1:'Value'},inplace=True)
    percentage['Stats'] = percentage[0]
    stats = stats.append(percentage,ignore_index=True)

    stats['Part Name'] = partname
    stats['Slice Width'] = slicewidth
    stats['Adaptive Algorithm'] = adapttype
    stats['Statistical Method'] = statmethod

    stats.drop([0],axis=1,inplace=True)

    dummystats = stats.copy()

    dummystats.set_index(['Part Name','Slice Width','Adaptive Algorithm','Statistical Method'],inplace=True)

    dummystats = dummystats[['Stats','Value']]
    stats = stats[['Stats','Value','Part Name','Slice Width','Adaptive Algorithm','Statistical Method']]



    pathstat = [treatment,dummystats.loc[dummystats['Stats'] == 'Total Path Time' ,'Value'].iloc[0],dummystats.loc[dummystats['Stats'] == 'Total Path Length' ,'Value'].iloc[0]]

    figname = destination+partname+adapttype+statmethod+str(slicewidth)+'Stats.png'
    #render_mpl_table(dummystats,title, figname, header_columns=0)

    return stats, pathstat

#builds the dataframes by parts
def build_dfs(partdirectory):
    global destination
    Sumstats = []
    Fitstats = []
    Treatments = []
    thresholds = []
    Skews = []
    PathStats = []

    slicedirectories = [x[0] for x in os.walk(partdirectory)]

    for x in range(0,len(slicedirectories)): #change 0 back to 1 for multiple subdirectories; needed if there are multiple slicing widths
        partfiles = [] 
        dummypartfiles = os.listdir(slicedirectories[x])
        #print dummypartfiles
        for i in range(len(dummypartfiles)):
            if ".csv" in str(dummypartfiles[i]):
                if "FullComparison" not in str(dummypartfiles[i]):
                    partfiles.append(dummypartfiles[i])
        #print partfiles
        for y in range(len(partfiles)):
            if "Analysis" in partfiles[y]:
                #print partfiles[y]
                if "Stats" in partfiles[y]:
                    new_df,pathstat = getstats(slicedirectories[x]+'/'+partfiles[y])
                    PathStats.append(pathstat)
                    try:
                        part_stats_df = part_stats_df.append(new_df)
                    except NameError:
                        part_stats_df = new_df.copy()

                if "Stats" not in partfiles[y]:
                    #print y
                    new_df, sumstat, fitstat, treatment, threshold_data, skew = getdata(slicedirectories[x]+'/'+partfiles[y])
                    #print 'fitstats',fitstat
                    Sumstats.append(sumstat)
                    Fitstats.append(fitstat)
                    Treatments.append(treatment)
                    thresholds.append(threshold_data)
                    Skews.append(skew)
                    try:
                        part_df = part_df.append(new_df)
                        #print y
                    except NameError:
                        part_df = new_df.copy()
                        #print 'except ',y


    slicevals = list(part_df['Slice Width'].unique())
    newvals = ['1/15','1/10','1/5']
    #print len(slicevals)
    if len(slicevals) == 3:
        part_df['Slice Value'] = part_df['Slice Width']
        for z in range(len(slicevals)):
            #print slicevals[z]
            part_df.loc[part_df['Slice Value'] == slicevals[z],'Slice Value'] = newvals[z]
    else:
        part_df['Slice Value'] = 'n/a'

    try:
        master_data_df = master_data_df.append(part_df)
        #print y
    except NameError:
        master_data_df = part_df
        #print 'except ',y

    try:
        master_stats_df = master_stats_df.append(part_stats_df)
    except NameError:
        master_stats_df = part_stats_df

    part_df = part_df.iloc[0:0]
    #print part_df
    part_stats_df = part_stats_df.iloc[0:0]
    #print part_stats_df

    BinMetric = bin_metric(master_data_df, Treatments)

    master_compare_df, comparename = build_compare_df(Treatments, Sumstats, Fitstats, thresholds, Skews,BinMetric,PathStats)

    master_compare_df.to_csv(comparename,sep=',')

    value_plots(master_stats_df,master_compare_df,'')

    diff_plots(master_stats_df,master_compare_df,'')

    return master_data_df, master_stats_df,master_compare_df

#takes dataframes and convets to table for visual export
def render_mpl_table(data, title, figname,col_width=4.5, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
#https://stackoverflow.com/questions/26678467/export-a-pandas-dataframe-as-a-table-image/26681726

    global destination

    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])

    plt.title(title, fontsize=12)
    plt.savefig(figname)
    plt.close()

#builds a bin metric for each part
def bin_metric(data,treatments):
    bins = 10
    binrange = data['Combined Value'].max()*1.001
    binwidth = binrange/bins
    result = []


    #print algorithms
    #print methods
    #print binrange

    for x in range(len(treatments)):
        metriccount = 0
        a = treatments[x][0]
        m = treatments[x][1]
        if a == 'Naive':
            treatdata = data[data['Adaptive Algorithm'] == a]
            impdata = treatdata['Combined Value'].tolist()

        else:
            treatdata = data[(data['Statistical Method'] == m) & (data['Adaptive Algorithm'] == a)]
            impdata = treatdata['Combined Value'].tolist()

        binresult = []
        for y in range(bins):
            minbin = y*binwidth
            maxbin = minbin + binwidth
            #print 'range: ',minbin,maxbin,y
            bincount = 0
            for z in range(len(impdata)):
                if impdata[z] < maxbin and impdata[z] >= minbin:
                    bincount += 1
                    metriccount += (y+1)

            binresult.append([bincount,bincount/len(impdata)])
        #print metriccount/len(impdata)
        result.append([binresult,metriccount/len(impdata)])

    return result

#deprecated; multiple slice widths were not considered
def compare_across_slice_width(data,name):
    global destination

    if name == '':
        uniquecheck = list(data['Part Name'].unique())
        #print uniquecheck
        if len(uniquecheck) == 1:
            name+=str(uniquecheck[0])
        else:
            name+="Multiple Parts"
        uniquecheck = list(data['Statistical Method'].unique())
        #print uniquecheck
        if len(uniquecheck) == 1:
            name+=str(uniquecheck[0])

        uniquecheck = list(data['Adaptive Algorithm'].unique())
        #print uniquecheck
        if len(uniquecheck) == 1:
            name+=str(uniquecheck[0])

    data = data[['Slice Value','Slice Width','Combined Value']]

    is5 = data['Slice Value'] == '1/5'
    is10 = data['Slice Value'] == '1/10'
    is15 = data['Slice Value'] == '1/15'

    slicevals = list(data['Slice Width'].unique())

    newvals = ['1/15','1/10','1/5']

    if len(slicevals) < 2:
        print "Not enough slice widths for comparison"
        return

    data5 = data[is5]
    #print 'data5\n', data5
    data5 = data5.rename(index=str, columns={"Combined Value":"5 Slices"})
    data5 = data5.groupby('Index').agg('mean')
    #print 'data5\n', data5

    data10 = data[is10]
    data10 = data10.rename(index=str, columns={"Combined Value":"10 Slices"})
    data10 = data10.groupby('Index').agg('mean')

    data15 = data[is15]
    data15 = data15.rename(index=str, columns={"Combined Value":"15 Slices"})
    data15 = data15.groupby('Index').agg('mean')


    dummy = pd.concat([data5,data10], axis =1,join='inner')
    comb = pd.concat([dummy,data15], axis =1,join='inner')
  
    comb = comb[['5 Slices','10 Slices','15 Slices']]
    #print time

    if len(slicevals) == 3:
       
        comb.rename(index=str, columns={'5 Slices':str(slicevals[2]),'10 Slices':str(slicevals[1]),'15 Slices':str(slicevals[0])})
    else:
        
        comb.rename(index=str, columns={'5 Slices':str(newvals[2]),'10 Slices':str(newvals[1]),'15 Slices':str(newvals[0])})


    plot_hist_side(comb,destination+name+'SliceWidthHist.png',name+'\nSlice Width Histogram')

    figname = destination+name+'SliceWidthKDE.png'
    name += '\nSlice Width Kernel Density Estimate'

    mx = float(np.percentile(comb.values,95)/19*20)
    comb.plot.kde(xlim=[0,mx])
    #comb.plot.hist()
    plt.title(name, fontsize=12)
    plt.xlabel('Impingement Value')
    plt.ylabel('Density')
    plt.savefig(figname)
    plt.close()


#bins impingement values histograms for both stat method and adaptive algorithm
def plot_hist_side(data,figname,name):
    cols = len(data.columns)
    d = []
    l = []
    step = 0.001
    for y in range(cols):
        #print "multidata"
        d.append(list(data[data.columns[y]]))
        l.append(str(data.columns[y]))
    #print l

    bins = np.arange(0,0.012,step) #0.012 is two steps past the max value of uniform bins(in this case 0.01), there is stil one bin for extreme points
   
    dt = np.clip(d,bins[0],bins[-1])    #sets extreme values to safe value for binning

    fig,ax = plt.subplots(figsize = (7,5))

    if cols == 5:
        maintitle = 'Histogram Based on Statistical Method'
        _, bins, patches = plt.hist([dt[0], dt[1], dt[2], dt[3], dt[4]], label = [l[0], l[1], l[2], l[3], l[4]], align = 'mid',bins=bins) #,color = ['C4','C6','C8','C9','C3']
    elif cols == 3:
        maintitle = 'Histogram Based on Adaptive Algorithm'
        _, bins, patches = plt.hist([dt[0], dt[1], dt[2]], label = [l[0], l[1], l[2]], align = 'mid',bins=bins)#,color = ['C0','C3','C4']
    else:
        maintitle = ''

    xlabels = [str(round(float(x),3)) for x in bins]       #may need to change if step changes, it is currently giving a wierd rounding error when converting to string, hence the round function
    xlabels[-1] = ''

    N_labels = len(xlabels)
    plt.xticks(step * np.arange(N_labels-1))
    ax.set_xticklabels(xlabels)

    plt.title(name, fontsize=12)
    plt.legend()
    plt.xlabel('Impingement Value')
    plt.ylabel('Density')
    plt.savefig(figname)
    plt.close()

#comparison stats grouped by statistical aggregate method
def compare_across_stat_method(data,name):
    global destination, directory

    if name == 'AllData': destination = directory+'/'


    if name == '':
        uniquecheck = list(data['Part Name'].unique())
        #print uniquecheck
        if len(uniquecheck) == 1:
            name+=str(uniquecheck[0])
        else:
            name+="Multiple Parts"

        uniquecheck = list(data['Adaptive Algorithm'].unique())
        #print uniquecheck
        if len(uniquecheck) == 1:
            name+=str(uniquecheck[0])

    data = data[['Statistical Method','Adaptive Algorithm','Combined Value']]

    isNaive = data['Adaptive Algorithm'] == 'Naive'

    isMean = data['Statistical Method'] == 'Mean'
    isMode = data['Statistical Method'] == 'Mode'
    isMax = data['Statistical Method'] == 'Max'
    isMin = data['Statistical Method'] == 'Min'

    vals = list(data['Statistical Method'].unique())
    
    if len(vals) < 2:
        print "Not enough data for comparison"
        return

    dataMean = data[isMean]
    dataMean = dataMean.rename(index=str, columns={'Combined Value':'Mean'})
    dataMean = dataMean.groupby('Index').agg('mean')

    dataMode = data[isMode]
    dataMode = dataMode.rename(index=str, columns={'Combined Value':'Mode'})
    dataMode = dataMode.groupby('Index').agg('mean')

    dataMax = data[isMax]
    dataMax = dataMax.rename(index=str, columns={'Combined Value':'Max'})
    dataMax = dataMax.groupby('Index').agg('mean')    

    dataMin = data[isMin]
    dataMin = dataMin.rename(index=str, columns={'Combined Value':'Min'})
    dataMin = dataMin.groupby('Index').agg('mean')

    dataNaive = data[isNaive]
    dataNaive = dataNaive.rename(index=str,columns={'Combined Value':'Naive'})
    dataNaive = dataNaive.groupby('Index').agg('mean')

    dummy = pd.concat([dataMean,dataMode], axis=1,join='inner') 
    dummy2 = pd.concat([dummy,dataMax], axis =1,join='inner')
    dummy3 = pd.concat([dummy2,dataMin], axis =1,join='inner')
    statdf = pd.concat([dummy3,dataNaive], axis =1,join='inner')

    #fit_curves(statdf,name+'Stat','')

    #run_minkowski(statdf,name+'Stat')

    plot_hist_side(statdf,destination+name+'ByStatMethodHist.png',name+'\nStatistical Method Histogram')

    figname = destination+name+'ByStatMethodKDE.png'
    name += '\nStatistical Method Kernel Density Estimate'

    mx = float(np.percentile(statdf.values,95)/19*20)
    statdf.plot.kde(xlim=[0,mx])
    #statdf.plot.hist()
    plt.title(name, fontsize=12)
    plt.xlabel('Impingement Value')
    plt.ylabel('Density')
    plt.savefig(figname)
    plt.close()

#comparison stats grouped by adaptive method
def compare_across_adapt_method(data,name):
    global destination, directory

    if name == 'AllData': destination = directory+'/'

    if name == '':
        uniquecheck = list(data['Part Name'].unique())
        #print uniquecheck
        if len(uniquecheck) == 1:
            name+=str(uniquecheck[0])
        else:
            name+="Multiple Parts"

        uniquecheck = list(data['Statistical Method'].unique())
        #print uniquecheck
        if len(uniquecheck) == 1:
            name+=str(uniquecheck[0])

    data = data[['Adaptive Algorithm','Time Value','Distance Value','Combined Value']]

    isTime = data['Adaptive Algorithm'] == 'Time'
    isDist = data['Adaptive Algorithm'] == 'Distance'
    isBoth = data['Adaptive Algorithm'] == 'Both'
    isNeither = data['Adaptive Algorithm'] == 'Naive'

    vals = list(data['Adaptive Algorithm'].unique())
    
    if len(vals) < 2:
        print "Not enough data for comparison"
        return

    dataTime = data[isTime]
    dataTime = dataTime.rename(index=str, columns={"Combined Value":"Time"})
    dataTime = dataTime.groupby('Index').agg('mean')

    dataDist = data[isDist]
    dataDist = dataDist.rename(index=str, columns={"Combined Value":"Distance"})
    dataDist = dataDist.groupby('Index').agg('mean')

    dataBoth = data[isBoth]
    dataBoth = dataBoth.rename(index=str, columns={"Combined Value":"Both"})
    dataBoth = dataBoth.groupby('Index').agg('mean') 
   
    dataNeither = data[isNeither]
    dataNeither = dataNeither.rename(index=str, columns={"Combined Value":"Naive"})
    dataNeither = dataNeither.groupby('Index').agg('mean')

    ##############uncomment to include time and modify line below
    #dummy = pd.concat([dataTime,dataDist], axis=1,join='inner') 
    dummy2 = pd.concat([dataDist,dataBoth], axis =1,join='inner')
    adaptdf = pd.concat([dummy2,dataNeither], axis =1,join='inner')
    adaptdf = adaptdf[["Distance","Both","Naive"]]#"Time",
    #print adaptdf
    
    #fit_curves(adaptdf,name+'Adapt','')

    #run_minkowski(adaptdf,name+'Adapt')

    plot_hist_side(adaptdf,destination+name+'By AdaptMethodHist.png',name+'\nAdaptive Algorithm Histogram')

    figname = destination+name+'ByAdaptMethodKDE.png'
    name += '\nAdaptive Algorithm Kernel Density Estimate'

    mx = float(np.percentile(adaptdf.values,95)/19*20)
    adaptdf.plot.kde(xlim=[0,mx])
    #adaptdf.plot.hist()
    plt.title(name, fontsize=12)
    plt.xlabel('Impingement Value')
    plt.ylabel('Density')
    plt.savefig(figname)
    plt.close()

#modify names from the mass planner for clarity
def rearrange_data(adapt,stat,name):
    if stat == "Adapt Using Mean":
        stat = "Mean"
    if stat == "Adapt Using Mode":
        stat = "Mode"
    if stat == "Adapt Using Max":
        stat = "Max"
    if stat == "Adapt Using Min":
        stat = "Min"

    if adapt == "Adapt Based On Time":
            adapt= "Time"
    if adapt == "Adapt Based On Distance":
            adapt = "Distance"
    if adapt == "Adapt Based On Time and Distance":
            adapt = "Both"
    if adapt == "No Adaptive Algorithm":
            adapt = "Naive"
            stat = "None"

    name = name.replace('Mean','')
    name = name.replace('Mode','')
    name = name.replace('Max','')
    name = name.replace('Min','')
    name = name.replace('Time','')
    name = name.replace('Distance','')
    name = name.replace('Both','')
    name = name.replace('Naive','')
    name = name.replace('None','')

#remove these lines to use true part names in figures; used for presentation in papers
    name = name.replace('Blade_reduced','Part D')
    name = name.replace('Incidence_Test','Part B')
    name = name.replace('Solid_Wheel_Upright','Part C')
    name = name.replace('Test_Part','Part A')
    name = name.replace('Wing_Section__reduced','Part E')

    return adapt, stat, name

def run_all_comparisons(data,partname):

    #compare_across_slice_width(data,partname)

    compare_across_stat_method(data,partname)

    compare_across_adapt_method(data,partname)

#compares minkowski distance from naive;deprecated
def run_minkowski(data,partname):
    global destination
    cols = len(data.columns) - 1
    naive = list(data[data.columns[cols]])

    minkowski_result = []

    if cols > 2:
        for x in range(cols):
            title = data.columns[x]
            compare_data = list(data[data.columns[x]])
            result = distance.minkowski(naive,compare_data,2)   #change p value
            minkowski_result.append([title,result,0])

    if cols == 2:
        for x in range(3):
            y = x + 1
            if x == 2: y = 0
            #print x,y
            title = data.columns[x]+ ' ' + data.columns[y]
            compare1 = list(data[data.columns[x]])
            compare2 = list(data[data.columns[y]])
            result = distance.minkowski(compare1,compare2,2)   #change p value
            minkowski_result.append([title,result,0])

    if cols == 4:
        maintitle = 'Minkowski Distance from Naive Path Based on Statistical Method'
        midfig = 'Stat'
    elif cols == 3:
        maintitle = 'Minkowski Distance from Naive Path Based on Adaptive Algorithm'
        midfig = 'Adapt'
    else:
        maintitle = ''
        #maintitle = 'Minkowski Distance between Slices'
        #midfig = 'Slice'

    title = partname + '\n' + maintitle
   
    figname = destination+partname+'Minkowski.png'

    x = []
    y = []
    n = []

    for i in range(len(minkowski_result)):
        x.append(float(minkowski_result[i][1]))
        y.append(float(minkowski_result[i][2]))
        n.append(str(minkowski_result[i][0])+'\n'+str(round(minkowski_result[i][1],3)))
    #print x, y, n
    fig, ax = plt.subplots()
    ax.scatter(x,y)

    for i, txt in enumerate(n):
        ax.annotate(txt, (x[i], y[i]))

    plt.title(title, fontsize=12)
    plt.xlabel('Distance')
    #plt.show()
    plt.savefig(figname)
    plt.close()

    return minkowski_result


#attempts to fit distributions to a curve; deprecated
def fit_curves(data,title,figname):

    #print title,figname,data

    def single_curve(data,title,figname):
        #print 'Single Curve\n',data
        fig, ax = plt.subplots(1, 1)
        x = np.linspace(0, 1, 100) 

        curve_data = weibull_max.fit(data)
            #print 'Weibull Max Data\n',curve_data
        rv = weibull_max(curve_data[0],curve_data[1],curve_data[2])
        ax.plot(x,rv.pdf(x), label='Weibull Max')
        #ax.legend(loc='best', frameon=False)
        #plt.show()

        plt.title(title, fontsize=12)
        plt.xlabel('')
        #plt.show()
        #plt.savefig(figname)
        plt.close()

        stats = weibull_max.stats(curve_data[0],curve_data[1],curve_data[2],moments='mvsk')
        #print 'Stats\n',stats

        return list(stats)
        
    ##########################################################

    global destination
    cols = len(data.columns)

    if cols == 1:
        dummydata = list(data[data.columns[0]])
        #dummydata = filter(lambda a: a != 0, dummydatamid)
        #print "Dummy Data\n",dummydata
        dummy = single_curve(dummydata,title,figname)
        return dummy

    if cols == 5:
        maintitle = 'Fitted Weibull Curves Based on Statistical Method'
        #midfig = 'Stat'
    elif cols == 3:
        maintitle = 'Fitted Weibull Curves Based on Adaptive Algorithm'
        #midfig = 'Adapt'
    else:
        maintitle = ''

    x = np.linspace(0, 1, 100)
    fig, ax = plt.subplots(1, 1)
    curves_result = []

    for y in range(cols):
        #print "multidata"
        col_data = list(data[data.columns[y]])
        col_title = data.columns[y]
        #print col_title,'\n',col_data
        #z = dummyfit_curves(col_data,'','')
        curve_data = weibull_max.fit(col_data)
        rv = weibull_max(curve_data[0],curve_data[1],curve_data[2])
        ax.plot(x,rv.pdf(x), label=col_title)
        stats = weibull_max.stats(curve_data[0],curve_data[1],curve_data[2],moments='mvsk')
        #print 'Stats\n',stats
        curves_result.append([col_title,stats])


    figtitle = title + '\n' + maintitle
   
    figname = destination+title+'FittedCurves.png'

    #ax.legend(loc='best', frameon=False)
    plt.title(figtitle, fontsize=12)
    #plt.show()
    #plt.savefig(figname)
    plt.close()
    
    #print curves_result

    return curves_result

#builds dataframes for all parts both individually and as a whole by looping through all siubsequent directories and looking for csv files
def partloops(directory):
    global destination
    partdirectories = []
    dummypartdirectories = os.listdir(directory)
    #print dummypartdirectories
    for x in range(len(dummypartdirectories)):
        if "." not in str(dummypartdirectories[x]): 
            partdirectories.append(directory+'/'+dummypartdirectories[x])
    #print 'part directory',partdirectories

    for i in range(len(partdirectories)):
        destination = partdirectories[i]+'/'
        print destination
        part_df,part_stats_df,part_compare_df = build_dfs(partdirectories[i])
        #print partdirectories[i], '\n',part_df.head()
        #print part_stats_df
        run_all_comparisons(part_df,'')

        try:
            master_data_df = master_data_df.append(part_df)
            #print y
        except NameError:
            master_data_df = part_df
            #print 'except ',y

        try:
            master_stats_df = master_stats_df.append(part_stats_df)
        except NameError:
            master_stats_df = part_stats_df

        try:
            master_compare_df = master_compare_df.append(part_compare_df)
        except NameError:
            master_compare_df = part_compare_df

        part_compare_df = part_compare_df.iloc[0:0]

        part_df = part_df.iloc[0:0]

        part_stats_df = part_stats_df.iloc[0:0]

    return master_data_df, master_stats_df, master_compare_df

#takes the full comparison data and finds the difference from the appropriate naive path before exporting
def diff_compare_export(comparestats):
    global destination, directory

    parts = list(comparestats['Part Name'].unique())

    treatset = [['Distance','Mean'],['Distance','Mode'],['Distance','Max'],['Distance','Min'],['Both','Mean'],['Both','Mode'],['Both','Max'],['Both','Min']] #['Time','Mean'],['Time','Mode'],['Time','Max'],['Time','Min'],

    dataset = ['Part Name','Adaptive Algorithm','Statistical Method']
    responseset = ['Bin Metric', 'Mean', 'Total Path Time', 'Total Path Length']    #'Data Skew',
    for x in range(len(responseset)):
        dataset.append(responseset[x])

    diffstats = comparestats[dataset].copy()

    for x in range(len(parts)):
        for r in responseset:
        #Response
            NaiveResponse = float(diffstats.loc[(diffstats['Part Name'] == str(parts[x])) & (diffstats['Adaptive Algorithm'] == 'Naive') & (diffstats['Statistical Method'] == 'None'),r].iloc[0])
            #print NaiveResponse
            for y in treatset:
            #Response
                response = float(diffstats.loc[(diffstats['Part Name'] == str(parts[x])) & (diffstats['Adaptive Algorithm'] == str(y[0])) & (diffstats['Statistical Method'] == str(y[1])),r].iloc[0])-NaiveResponse
                #print 'r ', response
                diffstats.loc[(diffstats['Part Name'] == str(parts[x])) & (diffstats['Adaptive Algorithm'] == str(y[0])) & (diffstats['Statistical Method'] == str(y[1])),r] = response


    diffstats = diffstats[diffstats['Adaptive Algorithm'] != 'Naive']

    diffstats.to_csv(directory+'/DifferenceComparison.csv',sep=',')

#takes the full comparison data and finds the difference from the appropriate naive path and runs teh vs plots
def diff_plots(sumstats,comparestats,name):
    global destination, directory

    if name == 'AllData':
        destination = directory+'/'
        parts = list(sumstats['Part Name'].unique())

#uncomment after rearrangement 
    if name == '':
        parts = list(sumstats['Part Name'].unique())
        #print uniquecheck
        if len(parts) == 1:
            name+=str(parts[0])
        else:
            name+="Multiple Parts"

    treatset = [['Distance','Mean'],['Distance','Mode'],['Distance','Max'],['Distance','Min'],['Both','Mean'],['Both','Mode'],['Both','Max'],['Both','Min']] #['Time','Mean'],['Time','Mode'],['Time','Max'],['Time','Min'],

    responseset = ['Bin Metric', 'Mean']    # 'Data Skew',
    #print 'parts',parts    

    T = []
    D = []
    R = []
    c = []
    m = []

    #custom legend building
    custom_legend = [Line2D([], [], color='k', marker='*', label='Mean'),
                    Line2D([], [], color='k', marker='o', label='Mode'),
                    Line2D([], [], color='k', marker='^', label='Max'),
                    Line2D([], [], color='k', marker='v', label='Min'),
                    Line2D([], [], color='r', lw=4, label='Distance'),
                    Line2D([], [], color='b', lw=4, label='Both')]

#results for the data summed across a treatment
    if name == 'AllDataSummed':
        return
        for r in responseset:            
            T = []
            D = []
            R = []
            c = []
            m = []

            for row in comparestats.itertuples():
                if row[0] == 'Naive':
                    NaiveTime = row[12]
                    NaiveDistance = row[13] 
                    if r == 'Bin Metric':
                        NaiveResponse = row[11]
                    if r == 'Data Skew':
                        NaiveResponse = row[10]
                    if r == 'Mean':
                        NaiveResponse = row[2]

            for row in comparestats.itertuples():
                if row[0] != 'Naive':
                #Time
                    T.append((row[12]/NaiveTime-1)*100)

                #Distance
                    D.append((row[13]/NaiveDistance-1)*100)

                #Response
                    if r == 'Bin Metric':
                        R.append(row[11]-NaiveResponse)
                    if r == 'Data Skew':
                        R.append(row[10]-NaiveResponse)
                    if r == 'Mean':
                        R.append(row[2]-NaiveResponse)

                    if row[0] == 'Distance': c.append('r')
                    if row[0] == 'Both': c.append('b')

                    if row[1] == 'Mean': m.append('*')
                    if row[1] == 'Mode': m.append('o')
                    if row[1] == 'Max': m.append('^')
                    if row[1] == 'Min': m.append('v')


            #Begin Plotting
            figname = destination+name+r+'vsTotalTimeDiff.png'
            title = r + ' vs Total Path Time\n'+name
            for _m, _c, _x, _y in zip(m, c, T, R):
                plt.scatter(_x, _y, marker=_m, c=_c)
            plt.title(title, fontsize=12)
            plt.xlabel('Total Path Time in Seconds')
            plt.ylabel('Actual Difference in '+r)
            plt.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()

            figname = destination+name+r+'vsTotalLengthDiff.png'
            title = r + ' vs Total Path Length\n'+name 
            for _m, _c, _x, _y in zip(m, c, D, R):
                plt.scatter(_x, _y, marker=_m, c=_c)
            plt.title(title, fontsize=12)
            plt.xlabel('Total Path Length')
            plt.ylabel('Actual Difference in '+r)
            plt.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()

            #stacked test
            figname = destination+name+r+'ScatterDiff.png'
            f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
            for _m, _c, _x, _y in zip(m, c, T, R):
                ax1.scatter(_x, _y, marker=_m, c=_c)
            ax1.set_title('vs Total Path Time')
            for _m, _c, _x, _y in zip(m, c, D, R):
                ax2.scatter(_x, _y, marker=_m, c=_c)
            ax2.set_title('vs Total Path Length')
            f.suptitle(name + ' ' + r)
            plt.ylabel('Actual Difference in '+r)
            #f.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()  

        return

    for r in responseset:
        T = []
        D = []
        R = []
        c = []
        m = []
        for x in range(len(parts)):
        #Time
            NaiveTime = float(sumstats.loc[(sumstats['Part Name'] == str(parts[x])) & (sumstats['Stats'] == 'Total Path Time') & (sumstats['Adaptive Algorithm'] == 'Naive') & (sumstats['Statistical Method'] == 'None'),'Value'].iloc[0])

        #Distance
            NaiveDistance = float(sumstats.loc[(sumstats['Part Name'] == str(parts[x])) & (sumstats['Stats'] == 'Total Path Length') & (sumstats['Adaptive Algorithm'] == 'Naive') & (sumstats['Statistical Method'] == 'None'),'Value'].iloc[0])

        #Response
            NaiveResponse = float(comparestats.loc[(comparestats['Part Name'] == str(parts[x])) & (comparestats['Adaptive Algorithm'] == 'Naive') & (comparestats['Statistical Method'] == 'None'),r].iloc[0])
            for y in treatset:
            #Time
                T.append((float(sumstats.loc[(sumstats['Part Name'] == str(parts[x])) & (sumstats['Stats'] == 'Total Path Time') & (sumstats['Adaptive Algorithm'] == str(y[0])) & (sumstats['Statistical Method'] == str(y[1])),'Value'].iloc[0])/NaiveTime-1)*100)

            #Distance
                D.append((float(sumstats.loc[(sumstats['Part Name'] == str(parts[x])) & (sumstats['Stats'] == 'Total Path Length') & (sumstats['Adaptive Algorithm'] == str(y[0])) & (sumstats['Statistical Method'] == str(y[1])),'Value'].iloc[0])/NaiveDistance-1)*100)

            #Response
                R.append(float(comparestats.loc[(comparestats['Part Name'] == str(parts[x])) & (comparestats['Adaptive Algorithm'] == str(y[0])) & (comparestats['Statistical Method'] == str(y[1])),r].iloc[0])-NaiveResponse)

                if y[0] == 'Distance': c.append('r')
                if y[0] == 'Both': c.append('b')
                if y[0] == 'Naive': c.append('g')

                if y[1] == 'Mean': m.append('*')
                if y[1] == 'Mode': m.append('o')
                if y[1] == 'Max': m.append('^')
                if y[1] == 'Min': m.append('v')
                if y[1] == 'None': m.append('s')


            if name != 'AllData':
                #Begin Plotting
                figname = destination+name+r+'vsTotalTimeDiff.png'
                title = r + ' vs Total Path Time Difference\n'+name
                for _m, _c, _x, _y in zip(m, c, T, R):
                    plt.scatter(_x, _y, marker=_m, c=_c)
                plt.title(title, fontsize=12)
                plt.xlabel('Total Path Time by Percent Difference')
                plt.ylabel('Actual Difference in '+r)
                plt.legend(handles=custom_legend,loc='best')
                plt.savefig(figname)
                #plt.show()
                plt.close()

                figname = destination+name+r+'vsTotalLengthDiff.png'
                title = r + ' vs Total Path Length Difference\n'+name 
                for _m, _c, _x, _y in zip(m, c, D, R):
                    plt.scatter(_x, _y, marker=_m, c=_c)
                plt.title(title, fontsize=12)
                plt.xlabel('Total Path Length by Percent Difference')
                plt.ylabel('Actual Difference in '+r)
                plt.legend(handles=custom_legend,loc='best')
                plt.savefig(figname)
                #plt.show()
                plt.close()

                #stacked test
                figname = destination+name+r+'ScatterDiff.png'
                f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
                for _m, _c, _x, _y in zip(m, c, T, R):
                    ax1.scatter(_x, _y, marker=_m, c=_c)
                ax1.set_title('vs Total Path Time Difference')
                for _m, _c, _x, _y in zip(m, c, D, R):
                    ax2.scatter(_x, _y, marker=_m, c=_c)
                ax2.set_title('vs Total Path Length Difference')
                f.suptitle(name + ' ' + r)
                plt.ylabel('Actual Difference in '+r)
                #f.legend(handles=custom_legend,loc='best')
                plt.savefig(figname)
                #plt.show()
                plt.close()


        if name == 'AllData':
            #Begin Plotting
            figname = destination+name+r+'vsTotalTimeDiff.png'
            title = r + ' vs Total Path Time Difference\n'+name
            for _m, _c, _x, _y in zip(m, c, T, R):
                plt.scatter(_x, _y, marker=_m, c=_c)
            plt.title(title, fontsize=12)
            plt.xlabel('Total Path Time Difference in Seconds')
            plt.ylabel('Difference in '+r)
            plt.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()



            figname = destination+name+r+'vsTotalLengthDiff.png'
            title = r + ' vs Total Path Length Difference\n'+name 
            for _m, _c, _x, _y in zip(m, c, D, R):
                plt.scatter(_x, _y, marker=_m, c=_c)
            plt.title(title, fontsize=12)
            plt.xlabel('Total Path Length Difference')
            plt.ylabel('Difference in '+r)
            plt.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()


            #stacked test
            figname = destination+name+r+'ScatterDiff.png'
            f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
            for _m, _c, _x, _y in zip(m, c, T, R):
                ax1.scatter(_x, _y, marker=_m, c=_c)
            ax1.set_title('vs Total Path Time')
            for _m, _c, _x, _y in zip(m, c, D, R):
                ax2.scatter(_x, _y, marker=_m, c=_c)
            ax2.set_title('vs Total Path Length')
            f.suptitle(name + ' ' + r + 'Difference')
            plt.ylabel('Difference in '+r)
            #f.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()


#versus plots for treatments
def value_plots(sumstats,comparestats,name):
    global destination, directory      

    if name == 'AllData':
        destination = directory+'/'
        parts = list(sumstats['Part Name'].unique())

#uncomment after rearrangement 
    if name == '':
        parts = list(sumstats['Part Name'].unique())
        #print uniquecheck
        if len(parts) == 1:
            name+=str(parts[0])
        else:
            name+="Multiple Parts"

    treatset = [['Distance','Mean'],['Distance','Mode'],['Distance','Max'],['Distance','Min'],['Both','Mean'],['Both','Mode'],['Both','Max'],['Both','Min'],['Naive','None']] #['Time','Mean'],['Time','Mode'],['Time','Max'],['Time','Min'],

    responseset = ['Bin Metric','Mean'] # 'Data Skew',
    #print 'parts',parts    
    T = []
    D = []
    R = []
    c = []
    m = []


    #custom legend building
    custom_legend = [Line2D([], [], color='k', marker='*', label='Mean'),
                    Line2D([], [], color='k', marker='o', label='Mode'),
                    Line2D([], [], color='k', marker='^', label='Max'),
                    Line2D([], [], color='k', marker='v', label='Min'),
                    Line2D([], [], color='r', lw=4, label='Distance'),
                    Line2D([], [], color='b', lw=4, label='Both'),
                    Line2D([], [], color='g', marker='s', markersize=12, label='Naive')]

    if name == 'AllDataSummed':
        for r in responseset:  
            T = []
            D = []
            R = []
            c = []
            m = []

            for row in comparestats.itertuples():
            #Time
                T.append(row[12])

            #Distance
                D.append(row[13])

            #Response
                if r == 'Bin Metric':
                    R.append(row[11])
                if r == 'Data Skew':
                    R.append(row[10])
                if r == 'Mean':
                    R.append(row[2])

                if row[0][0] == 'Distance': c.append('r')
                if row[0][0] == 'Both': c.append('b')
                if row[0][0] == 'Naive': c.append('g')


                if row[0][1] == 'Mean': m.append('*')
                if row[0][1] == 'Mode': m.append('o')
                if row[0][1] == 'Max': m.append('^')
                if row[0][1] == 'Min': m.append('v')
                if row[0][1] == 'None': m.append('s')

            

            #Begin Plotting
            figname = destination+name+r+'vsTotalTime.png'
            title = r + ' vs Total Path Time\n'+name
            for _m, _c, _x, _y in zip(m, c, T, R):
                plt.scatter(_x, _y, marker=_m, c=_c)
            plt.title(title, fontsize=12)
            plt.xlabel('Total Path Time in Seconds')
            plt.ylabel(r)
            plt.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()

            figname = destination+name+r+'vsTotalLength.png'
            title = r + ' vs Total Path Length\n'+name 
            for _m, _c, _x, _y in zip(m, c, D, R):
                plt.scatter(_x, _y, marker=_m, c=_c)
            plt.title(title, fontsize=12)
            plt.xlabel('Total Path Length')
            plt.ylabel(r)
            plt.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()

            #stacked test
            figname = destination+name+r+'Scatter.png'
            f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
            for _m, _c, _x, _y in zip(m, c, T, R):
                ax1.scatter(_x, _y, marker=_m, c=_c)
            ax1.set_title('vs Total Path Time')
            for _m, _c, _x, _y in zip(m, c, D, R):
                ax2.scatter(_x, _y, marker=_m, c=_c)
            ax2.set_title('vs Total Path Length')
            f.suptitle(name + ' ' + r)
            plt.ylabel(r)
            #f.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()  

        return


    for r in responseset:            
        T = []
        D = []
        R = []
        c = []
        m = []

        for x in range(len(parts)):
            for y in treatset:
            #Time
                T.append(float(sumstats.loc[(sumstats['Part Name'] == str(parts[x])) & (sumstats['Stats'] == 'Total Path Time') & (sumstats['Adaptive Algorithm'] == str(y[0])) & (sumstats['Statistical Method'] == str(y[1])),'Value'].iloc[0]))

            #Distance
                D.append(float(sumstats.loc[(sumstats['Part Name'] == str(parts[x])) & (sumstats['Stats'] == 'Total Path Length') & (sumstats['Adaptive Algorithm'] == str(y[0])) & (sumstats['Statistical Method'] == str(y[1])),'Value'].iloc[0]))

            #Response
                R.append(float(comparestats.loc[(comparestats['Part Name'] == str(parts[x])) & (comparestats['Adaptive Algorithm'] == str(y[0])) & (comparestats['Statistical Method'] == str(y[1])),r].iloc[0]))

                if y[0] == 'Distance': c.append('r')
                if y[0] == 'Both': c.append('b')
                if y[0] == 'Naive': c.append('g')

                if y[1] == 'Mean': m.append('*')
                if y[1] == 'Mode': m.append('o')
                if y[1] == 'Max': m.append('^')
                if y[1] == 'Min': m.append('v')
                if y[1] == 'None': m.append('s')


            if name != 'AllData':
                #Begin Plotting
                figname = destination+name+r+'vsTotalTime.png'
                title = r + ' vs Total Path Time\n'+name
                for _m, _c, _x, _y in zip(m, c, T, R):
                    plt.scatter(_x, _y, marker=_m, c=_c)
                plt.title(title, fontsize=12)
                plt.xlabel('Total Path Time in Seconds')
                plt.ylabel(r)
                plt.legend(handles=custom_legend,loc='best')
                plt.savefig(figname)
                #plt.show()
                plt.close()



                figname = destination+name+r+'vsTotalLength.png'
                title = r + ' vs Total Path Length\n'+name 
                for _m, _c, _x, _y in zip(m, c, D, R):
                    plt.scatter(_x, _y, marker=_m, c=_c)
                plt.title(title, fontsize=12)
                plt.xlabel('Total Path Length')
                plt.ylabel(r)
                plt.legend(handles=custom_legend,loc='best')
                plt.savefig(figname)
                #plt.show()
                plt.close()


                #stacked test
                figname = destination+name+r+'Scatter.png'
                f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
                for _m, _c, _x, _y in zip(m, c, T, R):
                    ax1.scatter(_x, _y, marker=_m, c=_c)
                ax1.set_title('vs Total Path Time')
                for _m, _c, _x, _y in zip(m, c, D, R):
                    ax2.scatter(_x, _y, marker=_m, c=_c)
                ax2.set_title('vs Total Path Length')
                f.suptitle(name + ' ' + r)
                plt.ylabel(r)
                #f.legend(handles=custom_legend,loc='best')
                plt.savefig(figname)
                #plt.show()
                plt.close()


        if name == 'AllData':
            #Begin Plotting
            figname = destination+name+r+'vsTotalTime.png'
            title = r + ' vs Total Path Time\n'+name
            for _m, _c, _x, _y in zip(m, c, T, R):
                plt.scatter(_x, _y, marker=_m, c=_c)
            plt.title(title, fontsize=12)
            plt.xlabel('Total Path Time in Seconds')
            plt.ylabel(r)
            plt.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()



            figname = destination+name+r+'vsTotalLength.png'
            title = r + ' vs Total Path Length\n'+name 
            for _m, _c, _x, _y in zip(m, c, D, R):
                plt.scatter(_x, _y, marker=_m, c=_c)
            plt.title(title, fontsize=12)
            plt.xlabel('Total Path Length')
            plt.ylabel(r)
            plt.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()


            #stacked test
            figname = destination+name+r+'Scatter.png'
            f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
            for _m, _c, _x, _y in zip(m, c, T, R):
                ax1.scatter(_x, _y, marker=_m, c=_c)
            ax1.set_title('vs Total Path Time')
            for _m, _c, _x, _y in zip(m, c, D, R):
                ax2.scatter(_x, _y, marker=_m, c=_c)
            ax2.set_title('vs Total Path Length')
            f.suptitle(name + ' ' + r)
            plt.ylabel(r)
            #f.legend(handles=custom_legend,loc='best')
            plt.savefig(figname)
            #plt.show()
            plt.close()

#plots the bin metric values as a bar chart of each treatment and part grouped by part
def bin_metric_chart(fullcompare):
    #colors only work for up to 10 parts
    data = fullcompare.groupby(['Part Name','Adaptive Algorithm']).agg('mean')
    #print data
    data.reset_index(level=['Part Name','Adaptive Algorithm'],inplace=True)    
    data = data[['Part Name','Adaptive Algorithm','Bin Metric']]
    #print data   
    figname = directory + '/AllDataBinMetric.png'

    c = ['C0','C1','C2','C3','C4','C5','C6','C7','C8','C9']

    bardata = []
    pos = []
    barwidth = 0.2

    parts = sorted(list(data['Part Name'].unique()))
    alg = ['Distance','Both','Naive']

    for x in range(len(alg)):
        algval = []
        for y in range(len(parts)):
            algval.append(float(data.loc[(data['Part Name'] == str(parts[y])) & (data['Adaptive Algorithm'] == str(alg[x])),'Bin Metric'].iloc[0])/float(data.loc[(data['Part Name'] == str(parts[y])) & (data['Adaptive Algorithm'] == 'Naive'),'Bin Metric'].iloc[0]))
        bardata.append(algval)
        if len(pos) == 0:
            pos.append(np.arange(len(algval)))
        else:
            pos.append([i + barwidth for i in pos[x-1]])

    for x in range(len(alg)):
        plt.bar(pos[x], bardata[x], color=c[x], width=barwidth, edgecolor='white', label=alg[x])

    plt.xlabel('Sample Parts', fontweight='bold')
    plt.xticks([r + barwidth for r in range(len(parts))], parts)

    plt.ylabel('Bin Metric as % of Naive', fontweight='bold')
    plt.legend()
    plt.savefig(figname)
    plt.close()




#modify to dictaet where the program should look for the data
directory = HOME+'/RRAD/src/rrad_wash_cell/src/Test_Data_NoTime'

threshold = 0.5 #threshold for checking facet coverage

fulldata, fullstats,fullcompare = partloops(directory)


bin_metric_chart(fullcompare)

#compare_across_slice_width(fulldata,'AllData')

compare_across_stat_method(fulldata,'AllData')

compare_across_adapt_method(fulldata,'AllData')

value_plots(fullstats,fullcompare,'AllData')

diff_plots(fullstats,fullcompare,'AllData')

diff_compare_export(fullcompare)

fullcompare.to_csv(directory+'/FullComparison.csv',sep=',')

finalcomparestats = fullcompare.groupby(['Adaptive Algorithm', 'Statistical Method']).agg('mean')

value_plots(fullstats,finalcomparestats,'AllDataSummed')

diff_plots(fullstats,finalcomparestats,'AllDataSummed')

finalcomparestats.to_csv(directory+'/SummedComparison.csv',sep=',')

partstats = fullcompare.groupby(['Part Name']).agg('mean')

partstats.to_csv(directory+'/PartComparison.csv',sep=',')


#Current build does not include Data Skew, Legends, Stats, Summary Stats or Fitted Curves as images
#to return to standard, find the correct lines and uncomment
#for Data Skew, the commented line needs to be moved inside the list is comes after
#for legends, the line plt.legend needs to be uncommmented
#for stats, the line render_mpl_table needs to be uncommented in the getstats function
#for summary stats, the line render_mpl_table needs to be uncommented in the getdata function
#for fitted curves, the line plt.save needs to be uncommented in the fit_curves function












