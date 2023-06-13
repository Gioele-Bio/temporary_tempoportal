## Setup


# CLI
import argparse

# workspace
import tempfile
import os
import shutil

# analysis, plots
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib.axes as ax
import plotly.express as px
import matplotlib
matplotlib.pyplot.switch_backend('Agg') 

# MDC api 
import requests
import json

# report
import docx
from docx.shared import Mm
from docx.shared import Pt
from docxtpl import DocxTemplate, InlineImage

# misc
import re
from datetime import date
from io import StringIO

 
# ### CLI

 
## argparse module used to write command-line interface. 

# # create parser object
# parser = argparse.ArgumentParser(prog="report_generation", description="This module receives input project number; gene counts table list; mapped unmapped file list; PCA flag; annotation file; and output folder to generate project report.")

# # add arguments to parser 
# parser.add_argument("-n", "--project", help="Project number for report")  
# parser.add_argument("-g", "--gene_counts_file", nargs="+", help="Path to gene_counts csv file(s)")  # nargs to accept 1 or more input files
# parser.add_argument("-m", "--mapped_unmapped_file", nargs="+", help="Path to mapped_unmapped csv file(s)") 
# parser.add_argument("-p", "--pca_required", action='store_true', default=False, help="Optional PCA plot input")  # stores a boolean, and does not except a parameter only it's presence
# parser.add_argument("-a", "--annotation_file", required=False, help="A csv file reporting in the first column the sample name and in the additional columns annotations, e.g. control/treatment, batch1/batch2, etc.")
# parser.add_argument("-o", "--output_folder", required=True, help="The output folder where the generated project report will be saved")
# parser.add_argument("-c", "--company", required=True, help="Option indicates whether to use bioclavis or biospyder report template")        

# # call parser .parse_args() method to return a namespace object 
# args = parser.parse_args()

# # assign properties inside 'args' namespace object using longform name (where included)
# project = args.project
# gene_count_files_list = args.gene_counts_file
# mapped_unmapped_files_list = args.mapped_unmapped_file
# output_folder = args.output_folder
# company = args.company

# # assign if pca_required is provided as input
# if  args.pca_required:  
#     pca_required = args.pca_required
# else:
#     pca_required = False

# # annotation file for pca is optional input
# if  args.annotation_file:  # A csv file reporting in the first column the sample name and in the additional columns annotations, e.g. control/treatment, batch1/batch2, etc.
#     annotation_file = args.annotation_file
# else:
#     annotation_file = None




 
# ### Data ingestion and transformation

 
## identify highest correlation coeff between two pos control (100 ng) from a gene_count df

def find_best_pos_corr_pair(input_df):  
    
    # filter gene_counts df for pos (C_) and neg (NC_) controls
    gene_counts_con_df = input_df.filter(regex='^C_|^NC_')
    
    # log2 transform and add pseudocount of 1 to each probe for each sample
    gene_counts_con_log2_df = np.log2(gene_counts_con_df+1)

    # filter log2 transformed counts for each type of positive control (e.g. BRR, URR)
    gene_counts_pos_con_log2_df = gene_counts_con_log2_df.filter(regex='^C_')    
    gene_counts_pos_con_log2_corr_df = gene_counts_pos_con_log2_df.corr()    
    
    # retain upper triangular values of correlation matrix and make Lower triangular values Null
    upper_gene_counts_pos_df_corr = gene_counts_pos_con_log2_corr_df.where(
        np.triu(np.ones(gene_counts_pos_con_log2_corr_df.shape), k=1).astype(bool))
    
    # convert to 1-D series and drop Null values
    unique_pos_corr_pairs = upper_gene_counts_pos_df_corr.unstack().dropna()

    # sort correlation pairs
    sorted_unique_pos_corr_pairs = unique_pos_corr_pairs.sort_values(ascending=False)
    highest_pos_corr_indices = sorted_unique_pos_corr_pairs.idxmax() 
    pos_corr_r_value = sorted_unique_pos_corr_pairs[0]

    return gene_counts_con_log2_df, highest_pos_corr_indices, pos_corr_r_value 


# In : project (project number) - gene counts (list) - mapped unmapped (list) - pca (boolean) - annotation file (file/false) - company
def get_report(project, gene_count_files_list, mapped_unmapped_files_list, company, pca_required=False, annotation_file=False):
    # create a temporary directory for working in
    temp_dir = tempfile.mkdtemp()

    # Get this script's dir
    file_path = os.path.dirname(__file__)

    # Declare output file (temporary)
    output_folder = os.path.join(file_path, 'temp_output')
    # print('OUTPUT FOLDER', output_folder)
    
    # compare input file lists content (length, position) and raise exception if lists not equal because because pairs of gene_counts and mapped_unmapped files are required  
    if len(gene_count_files_list) == len(mapped_unmapped_files_list):
        print("Input lists of gene_count_files_list and mapped_unmapped_files_list have equal content length and position")
    else:
        raise Exception("Input lists of gene_count_files_list and mapped_unmapped_files_list do not have equal content length and/or position; exiting program")    

    # create a master gene_counts df and set gene name col header
    # sort input list so that related gene_count and mapped_unmapped files are at the same position within respective lists and can be paired
    gene_count_files_list.sort()
    master_gene_counts_file = gene_count_files_list[0]   
    master_gene_counts_df = pd.read_csv(StringIO(master_gene_counts_file), header=0)   
    master_gene_counts_df.columns.values[0] = 'gene_id'  # rename col 'Unnamed: 0'
    master_gene_counts_df.index.name = 'gene_id'  # set df index

    # list master gene_counts sample names for checking that the corresponding mapped_unmapped file contains the same sample names
    gene_counts_sample_names = list(master_gene_counts_df.columns[1:])

    # list master probe names for checking that any additional gene count files relate to the same reference genome before merging files
    master_gene_counts_probe_names = list(master_gene_counts_df['gene_id'])

    # create master mapped_unmapped df and set metric col header
    # sort input list so that related gene_count and mapped_unmapped files are at the same position within respective lists and can be paired
    mapped_unmapped_files_list.sort()   
    master_mapped_unmapped_file = mapped_unmapped_files_list[0]   
    master_mapped_unmapped_df = pd.read_csv(StringIO(master_mapped_unmapped_file), header=0)
    master_mapped_unmapped_df.columns.values[0] = 'metric'  # rename col 'Unnamed: 0'
    master_mapped_unmapped_df.index.name = 'metric'  # set df index

    # list master mapped_unmapped sample names for checking that the corresponding gene_counts file contains the same sample names
    mapped_unmapped_sample_names = list(master_mapped_unmapped_df.columns[1:])               

    # initialise variables to be assessed for iterative assessment of highest correlation coeff between two pos controls (100 ng)
    best_correlation = 0.0
    best_correlation_df = ""
    best_correlation_indices = ""

    if len(gene_count_files_list) == 1:  
        
        # compare gene_counts_sample_names and mapped_unmapped_sample_names lists to check equal content is present at every index position
        if gene_counts_sample_names == mapped_unmapped_sample_names:
            #print("Sample lists from files " + str(master_gene_counts_file) + " and " + str(master_mapped_unmapped_file) + " pair are identical.")

            gene_counts_con_log2_df, highest_pos_corr_indices, pos_corr_r_value = find_best_pos_corr_pair(master_gene_counts_df)
            best_correlation_df = gene_counts_con_log2_df
            best_correlation = pos_corr_r_value
            best_correlation_indices = highest_pos_corr_indices

        else:          
            raise Exception("Sample lists from files " + str(master_gene_counts_file) + " and " + str(master_mapped_unmapped_file) + " pair are not identical. The difference is: " + str([x for x in gene_counts_sample_names if x not in set(mapped_unmapped_sample_names)]))        
            
    elif len(gene_count_files_list) > 1:    
        
        for gene_count_file, mapped_unmapped_file in zip(gene_count_files_list, mapped_unmapped_files_list)[1:]:               
                                
            # create df        
            gene_count_df = pd.read_csv(StringIO(gene_count_file), header=0)        
            gene_count_df.columns.values[0] = 'gene_id'  # rename col 'Unnamed: 0'
            gene_count_df.index.name = 'gene_id'  # set df index                      
            
            # list gene_counts sample names for checking that the corresponding mapped_unmapped file contains the same sample names
            gene_counts_sample_names = list(gene_count_df.columns[1:])            
                    
            # list probe names for checking that additional gene count files relate to the same reference genome in master before merging files
            gene_counts_probe_names = list(gene_count_df['gene_id'])
            
            # list mapped_unmapped df sample names  
            mapped_unmapped_df = pd.read_csv(StringIO(mapped_unmapped_file), header=0)
            mapped_unmapped_df.columns.values[0] = 'metric'  # rename col 'Unnamed: 0'
            mapped_unmapped_df.index.name = 'gene_id'  # set df index      
            mapped_unmapped_sample_names = list(mapped_unmapped_df.columns[1:])        

            # compare sample name lists -
            if gene_counts_sample_names == mapped_unmapped_sample_names and master_gene_counts_probe_names == gene_counts_probe_names:
                #print("Sample lists from files " + str(gene_count_file) + " and " + str(mapped_unmapped_file) + " pair are identical and tables will be joined.")                                 
                
                # assign values of highest correlation coeff between two pos control (100 ng) from additional gene_count df
                gene_counts_con_log2_df, highest_pos_corr_indices, pos_corr_r_value = find_best_pos_corr_pair(gene_count_df)
                
                # merge the columns of df into master_gene_counts_df 
                master_gene_counts_df = pd.merge(master_gene_counts_df, gene_count_df, on='gene_id') 
                
                # merge the columns of df into master_mapped_unmapped_df 
                master_mapped_unmapped_df = pd.merge(master_mapped_unmapped_df, mapped_unmapped_df, on='metric', suffixes=(False, False))

                # assess value of highest correlation coeff between two pos controls (100 ng) in current gene_count df and update variables, if required
                if pos_corr_r_value > best_correlation:
                    best_correlation = pos_corr_r_value
                    best_correlation_df = gene_counts_con_log2_df
                    best_correlation = pos_corr_r_value
                    best_correlation_indices = highest_pos_corr_indices

            else: 
                raise Exception("Sample lists from files " + str(gene_count_file) + " and " + str(mapped_unmapped_file) + " pair are not identical. Sample differences are: " + str([x for x in gene_counts_sample_names if x not in set(mapped_unmapped_sample_names)]))           



    
    # ## Data Quality Checks

    
    # check for missing values check in master_gene_counts_df and master_mapped_unmapped_df
    if master_gene_counts_df.isnull().values.any() or master_mapped_unmapped_df.isnull().values.any():    
        raise Exception("There are missing values in the input master_gene_counts_df and/or master_mapped_unmapped_df files")    
    else:
        print("No missing values in the input master_gene_counts_df and master_mapped_unmapped_df files")

    # check only integers in master_gene_counts_df
    master_gene_counts_nonnumeric_cols = master_gene_counts_df.select_dtypes(exclude=['int'])  # index col is non-numeric so should select only one col
    if master_gene_counts_nonnumeric_cols.shape[1] != 1:  
        raise Exception("Non-numeric columns are present in the master_gene_counts_df")
    else:
        print("Only numeric columns are present in the master_gene_counts_df")

    # check only numeric values in master_mapped_unmapped_df
    mapped_unmapped_nonnumeric_cols = master_mapped_unmapped_df.select_dtypes(exclude=['float', 'int'])  # index col is non-numeric so should select only one col
    if mapped_unmapped_nonnumeric_cols.shape[1] != 1:  
        raise Exception("Non-numeric columns are present in the master_mapped_unmapped_df")
    else:
        print("Only numeric columns are present in the master_mapped_unmapped_df")

    


    
    # # Analysis

    
    # ### Average Reads (mapped_unmapped)

    
    # average reads in expressed probes for each of the 100ng positive controls, then calculate the average across controls, 
    # for reads per expressed probe with counts >20.
    master_gene_counts_pos_100_df = master_gene_counts_df.filter(regex='C_[A-z]+100')
    avg_reads_probes_over_20 = master_gene_counts_pos_100_df[master_gene_counts_pos_100_df > 20].mean() 
    mean_avg_reads_probes_over_20 = int(avg_reads_probes_over_20.mean())

    # no. mapped reads in pos RNA controls (average)
    mapped_unmapped_pos_con_df = master_mapped_unmapped_df.filter(regex='^C_')
    avg_mapped_reads_pos_RNA = f"{mapped_unmapped_pos_con_df.mean(axis=1)[1].astype(int):,d}"  # formatted as str with commas between thousands

    # ‘Signal:noise ratio’ from the mapped_unmapped file
    avg_mapped_reads_pos = int(mapped_unmapped_pos_con_df.mean(axis=1)[1])

    # filter df for neg control cols
    mapped_unmapped_neg_df = master_mapped_unmapped_df.filter(regex='^NC_')

    # mean of mapped reads row
    avg_mapped_reads_neg = int(mapped_unmapped_neg_df.mean(axis=1)[1])

    # signal_noise_ratio
    signal_noise_ratio = int(avg_mapped_reads_pos / avg_mapped_reads_neg)

    # % of mapped reads in positive controls from the mapped_unmapped file
    avg_mapping_perc_pos = int(mapped_unmapped_pos_con_df.mean(axis=1)[3])


    
    # ### Scatter plots 

    
    ## Produce scatterplot between a pair of 100ng positive control

    # assign two pos controls with highest correlation coefficient for plotting #highest_pos_corr_indices = sorted_unique_pos_corr_pairs.idxmax()  
    pos_corr_pair_x = best_correlation_indices[0]
    pos_corr_pair_y = best_correlation_indices[1]

    # produce scatterplot
    sns.set(style='whitegrid')
    plot = sns.scatterplot(x=pos_corr_pair_x,
                        y=pos_corr_pair_y,
                        data=best_correlation_df)  # need to update this df ref

    # Annotate the statistics on the scatterplot
    plt.text(0, 19, f'R: {best_correlation:.2f}', ha='left')

    # Add title and rename the x and y axes
    plt.title('Positive Control', fontsize=15)
    plt.xlabel('Replicate 1, log2 counts')
    plt.ylabel('Replicate 2, log2 counts')

    plot.set_xlim(0, 20)
    plot.set_ylim(0, 20)

    plt.savefig(os.path.join(temp_dir, project + "_100ng_pos_controls_plot.png"), dpi=1000)
    plt.clf()


    
    ## identify highest correlation coefficient between two neg controls

    # filter df for neg control columns
    gene_counts_neg_df = gene_counts_con_log2_df.filter(regex='^NC_')

    # Use the log transformed counts to produce cross-correlation matrices for each type of negative control
    gene_counts_neg_df_corr = gene_counts_neg_df.corr()

    ## identify highest correlation coefficient between two neg controls

    # Retain upper triangular values of correlation matrix and make Lower triangular values Null
    upper_gene_counts_neg_df_corr = gene_counts_neg_df_corr.where(
        np.triu(np.ones(gene_counts_neg_df_corr.shape), k=1).astype(bool))
    
    # Convert to 1-D series and drop Null values
    unique_neg_corr_pairs = upper_gene_counts_neg_df_corr.unstack().dropna()

    # Sort correlation pairs
    sorted_unique_neg_corr_pairs = unique_neg_corr_pairs.sort_values(ascending=True)

    
    ## Produce scatterplot between a pair of neg controls

    # assign two neg controls with highest correlation coefficient for plotting
    highest_neg_corr_indices = sorted_unique_neg_corr_pairs.idxmax()
    neg_corr_pair_x = highest_neg_corr_indices[0]
    neg_corr_pair_y = highest_neg_corr_indices[1]
    pos_corr_r_value = sorted_unique_neg_corr_pairs[0]

    # produce scatterplot
    sns.set(style='whitegrid')
    plot = sns.scatterplot(x=neg_corr_pair_x,
                        y=neg_corr_pair_y,
                        data=gene_counts_neg_df)

    # Add title and rename the x and y axes
    plt.title('Negative Control', fontsize=15)
    plt.xlabel('Replicate 1, log2 counts')
    plt.ylabel('Replicate 2, log2 counts')

    plot.set_xlim(0, 20)
    plot.set_ylim(0, 20)

    plt.savefig(os.path.join(temp_dir, project + "_neg_controls_plot.png"), dpi=1000)
    plt.clf()

    
    # ### 9.3.7. Sample PCA Plot [optional]

    
    ## adapted PCA code block from pca_plot.py

    mapped_unmapped = master_mapped_unmapped_df.T

    # load annotation file if provided
    if not annotation_file == None:
        annotation_df = pd.read_csv(StringIO(annotation_file), header=0)
        annotation_df.set_index("Sample", inplace=True)

    # load count table and set index on the probe names
    master_gene_counts_df.set_index('gene_id',inplace=True)

    # log(CPM) transform the count table
    df_transform = pd.DataFrame(index = master_gene_counts_df.index)

    for sample in master_gene_counts_df.columns:
        df_transform[sample] = np.log2((master_gene_counts_df[sample]+1)/master_gene_counts_df[sample].sum()*1000000)

    # transpose the count table
    df_transform = df_transform.T

    # perform a PCA
    pca = PCA(n_components=2)
    principalComponents = pca.fit_transform(df_transform)
    principalDf = pd.DataFrame(data = principalComponents
                , columns = ['principal component 1', 'principal component 2'])
    principalDf['Sample'] = list(df_transform.index)
    principalDf.index = principalDf['Sample']

    # concatenate annotation if present
    if not annotation_file == None:  
        principalDf = pd.concat([principalDf,annotation_df], axis=1)
    #print(principalDf.head())

    # concatenate the mapped unmapped file 
    principalDf = pd.concat([principalDf,mapped_unmapped], axis=1)

    # produce scatterplot
    sns.set(style='whitegrid')
    sns.scatterplot(x='principal component 1',
                        y='principal component 2',
                        data=principalDf)

    # Remove gridlines
    plt.grid(False)

    # Add title and rename the x and y axes
    plt.title('PCA', fontsize=15)
    plt.xlabel('Principal component 1')
    plt.ylabel('Principal component 2')

    plt.savefig(os.path.join(temp_dir, project + "_pca_plot.png"), dpi=1000)
    plt.clf()
    plt.close()

    
    # ### Fetch MDC data

    
    if project.startswith("BIOS"):
        print("Project has BIOS and will not have an associated MDC Project Tracker board item")

    else:
        # if a non-BIOS project then BCL- prefix required to find project on MDC Project Tracker board
        print("Project is not BIOS and the MDC Project Tracker board data will be fetched")

        try:
            apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjIzNjg4MDE0OCwiYWFpIjoxMSwidWlkIjozMzUyMTg5OSwiaWFkIjoiMjAyMy0wMi0xM1QxNzowOToxMC4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjIzNTM1NiwicmduIjoidXNlMSJ9.rleGG0VUy3ATWW8vJY6cNB--00VoUjWxrXWO2JjTHos"  # available from MDC developer tab
            apiUrl = "https://api.monday.com/v2"
            headers = {"Authorization": apiKey}
            
            query = '{ boards(ids: 124841250) { items { id name column_values(ids:["name", "text31", "status4", "text36", "status1", "numbers0", "date3", "numbers", "sample____customer_", "status5", "do_v_", "sample____customer_", "numbers58"]) { title text } } } }'
            data = {'query': query}

            mdc_project_tracker_results = requests.post(url=apiUrl, json=data, headers=headers) 
            mdc_results_json = mdc_project_tracker_results.json()  
            print("Fetched MDC API data for " + str(project))        
        except:
            raise Exception("Unable to fetch MDC API data for " + str(project))        

    
    # var initiated as empty string and will be updated for BCL- projects only
    required_average_depth = ""
    samples_received_date = ""

    # check project name and add "BCL-" prefix if required for Project Tracker board query
    if project.startswith("BCL-"):
        print("Project name does not require formatting with prefix: BCL-")
        bcl_project_name = project
    else:
        bcl_project_name = "BCL-" + project    

    if project.startswith("BIOS"):
        print("No MDC results to parse for project: " + str(project))
    else:    
        bcl_project_mdc_item = False  

        for row in mdc_results_json['data']['boards'][0]['items']:  # for row in mdc board        

            if row['column_values'][0]['text'] == str(bcl_project_name):
                print("Found MDC board item for " + str(bcl_project_name))
                bcl_project_mdc_item = True
                customer_name = row['name']
                samples_received_date = str(row['column_values'][1]['text'])
                ref_gen_vers = str(row['column_values'][2]['text'] + ' ' + row['column_values'][3]['text'])            
                num_plates_slides = str(row['column_values'][4]['text']) #[number of plates/number of slides]
                num_samples_rec = str(row['column_values'][5]['text']) 
                num_samples_proc = str(row['column_values'][6]['text'])            
                reads_per_sample = str(row['column_values'][7]['text'])
                sample_type = str(row['column_values'][8]['text'])
                sample_submission = str(row['column_values'][9]['text'])            
                            
                if re.search(" v[0-9].[0-9] ", ref_gen_vers):
                    ref_gen_vers = re.sub(" v[0-9].[0-9] ", " v", ref_gen_vers)
                else:
                    ref_gen_vers = str(row['column_values'][2]['text'] + ' ' + row['column_values'][3]['text'])

                if re.search(" WT ", ref_gen_vers):
                    ref_gen_vers = re.sub(" WT ", " Whole Transcriptome ", ref_gen_vers)
                else:
                    ref_gen_vers = str(row['column_values'][2]['text'] + ' ' + row['column_values'][3]['text'])

                # logic to account for scenario where actual samples processed not updated on MDC board
                if row['column_values'][6]['text'] != "":
                    num_samples_proc = str(row['column_values'][6]['text']) 
                else:
                    num_samples_proc = int(row['column_values'][5]['text'])  # "Sample # Processed (Customer)" col     
                
                # if samples_received_date provided reformat for report
                if samples_received_date != "":            
                    date_list = samples_received_date.split("-")                        
                    reformat_date = str(date_list[2]+ "/" + date_list[1]+"/" + date_list[0])

                if re.search("well$", sample_submission):
                    sample_submission += " plate(s)"            
        
        if bcl_project_mdc_item == False:
            raise Exception("Did not find MDC board item for " + str(bcl_project_name))  # if MDC board does not contain project then this error will result        
                
                

    
    # # Report

    # template doc to modify assigned based on company and, for bioclavis, whether an optional PCA plot is required
    if company == "bioclavis":
        if pca_required == False:
            template_location = os.path.join(file_path, "project_report_template.docx")
        else:
            template_location = os.path.join(file_path, "project_report_template_w_PCA.docx")
    elif company == "biospyder":
        template_location = os.path.join(file_path, "biospyder_project_report_template.docx")
    else:
        print("Invalid company name input: must be either 'bioclavis' or 'biospyder'")     

    #print(template_location)
    doc = DocxTemplate(template_location)

    # figures
    pos_con_image = InlineImage(doc, image_descriptor=os.path.join(temp_dir, project + "_100ng_pos_controls_plot.png"), width=Mm(85), height=Mm(76))
    neg_con_image = InlineImage(doc, image_descriptor=os.path.join(temp_dir, project + "_neg_controls_plot.png"), width=Mm(85), height=Mm(76))
    pca_image = InlineImage(doc, image_descriptor=os.path.join(temp_dir, project + "_pca_plot.png"), width=Mm(85), height=Mm(76))

    # vars
    report_generation_date = date.today()
    #data_file = "Counts_per_gene_per_sample_raw_" + bcl_project_name + ".csv"

    # output maser df for customer
    data_file = "Counts_per_gene_per_sample_raw_" + bcl_project_name + ".csv"
    #master_gene_counts_df.to_csv(os.path.join(output_folder, data_file))

    #  jinja2-like tags for inserting context variables into doc (key is tag in doc and value is var name)
    context = { 'project' : project, 
    'sample_type' : sample_type, 
    'num_plates_slides' : num_plates_slides or '1', 
    'samples_received_date' : reformat_date,
    'num_samples_rec' : num_samples_rec,
    'num_samples_proc' : num_samples_proc,
    'ref_gen_vers' : ref_gen_vers,
    'bcl_project_name' : bcl_project_name,
    'avg_mapped_reads_pos_RNA' : avg_mapped_reads_pos_RNA,
    'reads_per_sample' : reads_per_sample,
    'signal_noise_ratio' : signal_noise_ratio,
    'avg_mapping_perc_pos' : avg_mapping_perc_pos,
    'mean_avg_reads_probes_over_20' : mean_avg_reads_probes_over_20,
    'data_file' : data_file,
    'report_generation_date' : report_generation_date,
    'customer_name' : customer_name,
    'sample_submission' : sample_submission,
    'pos_con_fig' : pos_con_image,
    'neg_con_fig' : neg_con_image,
    'pca_fig' : pca_image
    }

    if pca_required == False:
        context.pop('pca_fig')

    context_missing_values = {key:value if value != '' else 'Missing Value' for key,value in context.items()}

    if 'Missing Value' in context_missing_values.values():
        print('There are values missing from the report')   

    # create and output doc
    doc.render(context)
    #doc.save(os.path.join(output_folder, project + "_test_report_generation.docx"))
    
    
    # Cleanup workspace by manuallay removing the temporary directory and contents after files have been used
    shutil.rmtree(temp_dir)

    # master_gene_counts_df + doc
        
    return master_gene_counts_df, data_file, doc, project + "_test_report_generation.docx"
