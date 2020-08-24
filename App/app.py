from flask import Flask, render_template, url_for, request
import numpy as np
import pandas as pd
import json
app = Flask(__name__)


Compute_Data={}
Overlaps={}

@app.route("/") #Main INDEX Page & Set the ZONE of your computation
def index_page():
    return render_template("index.html")

@app.route("/get_computes", methods=["GET"]) #Set the Computing Machine
def get_compute():
    zone = request.args["zone"]
    filename = "../Data/"+ zone+".txt"
    df = pd.read_csv(filename, delim_whitespace=True, names=["Compute Name","Instance UUID", "Instance Name", "Total CPUS", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24", "F25", "F26", "F27", "F28", "F29", "F30", "F31", "F32", "F33"])
    for i in range(len(df)):
        if "-" in df["F1"][i]:
            df.drop(i, inplace=True)
            print(i)
    df = df.reset_index(drop=True)

    headers = list(df)
    instance_entry=[]
    CPU_Data ={}
    Memory = []

    for row_idx in range(len(df)):
        CPU_Entry = []
        compute_name = df['Compute Name'][row_idx];
        cpu_col_idx = 3 #Total CPUs
        col_idx = cpu_col_idx + 1  #Initializing the iterating variable
        total_cpus = df[headers[cpu_col_idx]][row_idx] #Extract total CPUs for each row
        
        if "'" in df[headers[col_idx]][row_idx]: #Skipping over data which does not mention CPU sets and mislocated Memory Field
            for i in range(col_idx, total_cpus+ col_idx):
                entry = df[headers[i]][row_idx]
                entry = entry.replace("'", "")        
                CPU_Entry.append(int(entry))
            Memory.append(int(df[headers[total_cpus+col_idx]][row_idx]))
        else:
            Memory.append(int(df[headers[col_idx]][row_idx]))
        instance_entry.append([df['Instance Name'][row_idx], df['Instance UUID'][row_idx], CPU_Entry])
        if row_idx != len(df)-1:
            if compute_name != df['Compute Name'][row_idx+1]:
                CPU_Data[df['Compute Name'][row_idx]] = instance_entry
                instance_entry=[]
            else:
                CPU_Data[df['Compute Name'][row_idx]] = instance_entry
        
    compute_names = df["Compute Name"].unique()

    index = 4 #index of column "F1"
    for i in range(index, len(headers)):
        df.drop(headers[i], axis=1, inplace=True)
    df["Memory"] = Memory


    global Compute_Data
    Compute_Data={} 
    for compute in compute_names:
        data = df.loc[df["Compute Name"] == compute]
        data.drop(["Compute Name", "Instance UUID"], axis=1, inplace=True)
        Compute_Data[compute]= np.array(data).tolist()


    global Overlaps
    Overlaps={}
    for compute in CPU_Data:
        VM_Shares=[]
        if(len(CPU_Data[compute]) > 1):
            for i in range(len(CPU_Data[compute])-1):
                principle_set = CPU_Data[compute][i][2];
                for j in range(i+1, len(CPU_Data[compute])):
                    check_set = CPU_Data[compute][j][2]
                    intersection = list(set(principle_set) & set(check_set))
                    if intersection:
                        VM_Shares.append([CPU_Data[compute][i][0],
                                      CPU_Data[compute][j][0],
                                      CPU_Data[compute][i][1], CPU_Data[compute][j][1], intersection])
        Overlaps[compute] = VM_Shares
    
    Total_Overlaps = []
    overlap_lengths=[]
    for key, value in Overlaps.items():
        overlap_lengths.append(len(value))
        Total_Overlaps.append([key, value])

    return render_template("set_computes.html",len= len(compute_names), compute_names = compute_names, overlaps_len = len(Total_Overlaps), zone_overlaps= Total_Overlaps, overlap_lengths = overlap_lengths)

@app.route("/get_data", methods=["GET"])
def get_data():
    compute = request.args["compute"]
    data = Compute_Data[compute]
    overlap = Overlaps[compute] 
    mem =[]
    for i in range(len(Compute_Data[compute])):
        mem.append(Compute_Data[compute][i][2])
    minim = min(mem)
    maxim = max(mem)
    return render_template("visualize.html", len=len(data), data=data, overlap=overlap, overlap_len=len(overlap), compute=compute, minimum=minim-2000, maximum=maxim+2000)

if __name__ == "__main__":
    app.run(debug=True)

