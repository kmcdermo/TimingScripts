#!/usr/bin/python


#setup argument parser
import argparse

parser = argparse.ArgumentParser(description='A script to plot the path total  histograms for more than one path or more than one test. Default is to make one plot per path (i.e. test same path for one or more input files). To make it do more than one path on the same plot, pass the --pathTest flag. Makes an output file called PathTotal_<PathName>.pdf for default mode and PathTotal_PathComparison.pdf for --pathTest flag. Usage: python validation_plot.py --inputfiles INPUTFILES --runs RUNNUMBERS --processes PROCESSNAMES --nthreads NTHREADS --outdir OUTDIR --log')

parser.add_argument("--inputfiles", type=str, help='The list of input files, comma separated if more than one file',required=True,nargs=1)
parser.add_argument("--runs",type=str,help='the corresponding run numbers,comma separated if more than one file',required=True,nargs=1)
parser.add_argument("--nthreads",type=str,help='nThreads used when doing timing tests',required=True,nargs=1)
parser.add_argument("--processes",type=str,help='the corresponding process names,comma separated if more than one file',required=True,nargs=1)
parser.add_argument("--paths",type=str,help='the list of paths you would like to test separated by commas',required=True,nargs=1)
parser.add_argument("--log",dest='log',action='store_true',help='specify to set log scale on the plot')
parser.add_argument("--pathTest",dest='pathTest',action='store_true',help='specify to make the script compare paths rather than iput')
parser.add_argument("--outdir",type=str,help='optional outdir name',nargs=1)
args=parser.parse_args()


#import root libraries
from ROOT import gROOT, TCanvas, TH1F, TFile, TLegend, gStyle, TColor


files = args.inputfiles[0].split(",")
runs = args.runs[0].split(",")
nthreads = args.nthreads[0].split(",")
processes = args.processes[0].split(",")
paths = args.paths[0].split(",")
pathTest = args.pathTest
if len(files)!=len(runs) and len(files)!=len(processes):
    print "Misconfigured! number of runs and/or processes is not the same as the number of inputfiles. Exiting.."
    quit()

#remove stat box
gStyle.SetOptStat(False)

outdir=''
if args.outdir:
    outdir=args.outdir[0]+'/'

def plotPathComparison(f,run,process,paths):
    tHists = []
    tFile = TFile(f)
    for p in paths:
        hName = "DQMData/Run %s/HLT/Run summary/TimerService/Running %s processes/process %s/Paths/%s_total" % (run,nthreads[0],process,p)
        tHists.append(tFile.Get(hName))

    leg = TLegend(0.2,0.6,0.9,0.9,"")
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    color=1
    c = TCanvas()
    c.SetLogy(args.log)

    output = open(outdir+"pathtotal.txt","w")

    for h in tHists:
        h.SetLineColor(color)
        if color==1:
            h.Draw("hist")
            h.SetTitle("")
        else:
            h.Draw("same hist")

        legentry = paths[color-1] + " Mean: %f" % h.GetMean()
        leg.AddEntry(h,legentry,"l")

        textout = paths[color-1] + " %f %i \n" % (h.GetMean(),h.GetBinContent(h.GetNbinsX()+1))
        output.write(textout)

        color+=1
        

    leg.Draw("same")
    filename = 'PathTotal_PathComparison'
    if args.log:
        filename+='_log'
    c.Print(outdir+filename+'.pdf')

    output.close()

def plotInputComparison(files,runs,processes,path):

    #clear memory 
    gROOT.Reset()
#make canvas to save plots to
    c1 = TCanvas('c1')

    i=0
    Tfiles=[]
    while i<len(files):
        print "Adding file: %s to list of files to run with Run Number: %s and Process Name: %s" % (files[i],runs[i],processes[i])
        Tfiles.append(TFile(files[i]))
        i+=1

    j=0
    Thists=[]
    while j<len(Tfiles):
        dirname="DQMData/Run %s/HLT/Run summary/TimerService/Running %s processes/process %s/Paths/%s_total" % (runs[j],nthreads[0],processes[j],path)
        print dirname
        hist=Tfiles[j].Get(dirname)

        Thists.append(hist)
        j+=1

    k=0
    leg = TLegend(0.4,0.6,0.9,0.9,"")
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    while k< len(Thists):
        if k==0:
            print "Overflow: %i" % Thists[k].GetBinContent(Thists[k].GetNbinsX()+1)
            Thists[k].Scale( 1.0 / Thists[k].Integral() )
            Thists[k].GetYaxis().SetRangeUser(0.000008,0.2)
            Thists[k].SetLineWidth(2)
            Thists[k].SetLineColor(k+1)
            Thists[k].Draw()
        else:
            print "Overflow: %i" % Thists[k].GetBinContent(Thists[k].GetNbinsX()+1)
            Thists[k].Scale( 1.0 / Thists[k].Integral() )
            Thists[k].SetLineWidth(2)
            Thists[k].SetLineColor(k+1)
            Thists[k].Draw("same")
        #write name in full
        name = "Mean: %f" % Thists[k].GetMean()
        leg.AddEntry(Thists[k],name,"l")
        k+=1
        
    leg.Draw("same")

    filename='PathTotal_%s' %path
    if args.log:
        filename+='_log'
        c1.SetLogy(1)
    c1.Print(outdir+filename+'.pdf')


if pathTest:
    plotPathComparison(files[0],runs[0],processes[0],paths)
else:
    for path in paths:
        plotInputComparison(files,runs,processes,path)

