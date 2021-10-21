# Python code to illustrate parsing of XML files 
# importing the required modules 


def xml2csv(xmlfile):
    import csv
    import os
    import xml.etree.ElementTree as ET 
    import pandas as pd
    tree=ET.parse(xmlfile)
    root=tree.getroot()
    k=len(root[2])
    X=[]
    for i in range(k):
        X.append(root[2][i].attrib)
        
    frame=[int(X[i]['frame']) for i in range(k)]

    xtl=[float(X[i]['xtl']) for i in range(k)]

    ytl=[float(X[i]['ytl']) for i in range(k)]
    
    xbr=[float(X[i]['xbr']) for i in range(k)]
    
    ybr=[float(X[i]['ybr']) for i in range(k)]
    
    data= pd.DataFrame({"frameno":frame,"left":xtl,
                        "top":ytl,"right":xbr,"bottom":ybr})
    
    data.to_csv("frame.csv",index=False)
