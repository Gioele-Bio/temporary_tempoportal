import os
import subprocess
import pandas as pd
#For sending email
import smtplib
import datetime








# Get a list of all the temporary files that get made

def align_star(filename, reference_index, threads, zipped, temp_dir_list, input_directory, output_directory, mismatches = 2):
    print('Starting ', filename)
    
    # Get temporary name to make a directory (filename without extension)
    temp_name = filename.split('.')[0]
    # how is the temporary directory called
    temp_dir = f'temp_{temp_name}'


    # Make temporary directory if not already existing (main)
    if not os.path.exists(f'{output_directory}'):
        os.mkdir(fr'{output_directory}/')
    # make iteration specific dir  
    os.mkdir(fr'{output_directory}/{temp_dir}/')
    
    
    # append it to list of temporary directories
    temp_dir_list.append(temp_dir)

    # Copy fastq file in directory
    subprocess.Popen(f'cp "{input_directory}/{filename}" "{output_directory}/{temp_dir}"', shell=True).wait()
    # Move into temporary directory
    os.chdir(fr'{output_directory}/{temp_dir}')
    
    # Make GTF reference (script is in the folder alignment_scripts in gio's home)
    subprocess.Popen(f'python /home/gioele/alignment_scripts/makeGtf.py "{reference_index}" > input.gtf', shell=True).wait()

    # Make Hash Table
    subprocess.Popen(f'STAR --runMode genomeGenerate --runThreadN {threads} --genomeDir "{output_directory}/{temp_dir}/" --genomeFastaFiles "{reference_index}" --genomeSAindexNbases 4 --sjdbGTFfile input.gtf --sjdbGTFfeatureExon exon', shell=True).wait()

    # Run STAR alignment
    # This works on normal scripts but not on sh (bc of file flocking, just expanding the file)
    # _subprocess.Popen(f'STAR --genomeDir {input_directory}/{temp_dir}/ --readFilesIn {f"<(gunzip -c {input_directory}/{temp_dir}/{filename})" if zipped else filename} --runThreadN 8 --outSAMtype BAM SortedByCoordinate --scoreDelOpen -10000 --scoreInsOpen -10000 --outFilterMultimapNmax 1 --outFilterMismatchNmax 2 --outSAMunmapped Within --outFileNamePrefix {temp_name}' , shell=True)

    # Expand file with zcat if zipped
    if zipped:
        subprocess.Popen(f'zcat "{output_directory}/{temp_dir}/{filename}" > "{output_directory}/{temp_dir}/"{temp_name}.fastq', shell=True).wait()
        filename = f'{temp_name}.fastq'

    subprocess.Popen(f'STAR --genomeDir "{output_directory}/{temp_dir}/" --readFilesIn {filename} --runThreadN {threads} --outSAMtype BAM SortedByCoordinate --scoreDelOpen -10000 --scoreInsOpen -10000 --outFilterMultimapNmax 1 --outFilterMismatchNmax {mismatches} --outSAMunmapped Within --outFileNamePrefix {temp_name}' , shell=True).wait()
    

    print('Alignment complete for file ', filename)

    # Produce count table
    subprocess.Popen(f'featureCounts -a input.gtf -o read_count.txt {temp_name}Aligned.sortedByCoord.out.bam', shell=True).wait() 
    # Last argument indicates the bam file

    # Remove everything but read_count.txt
    # Get file list
    file_list = os.listdir()
    #Remove read_count.txt from file list

    file_list.remove('read_count.txt')

    # Remove all files but read_count.txt
    #subprocess.Popen(f'rm {" ".join(file_list)}').wait()
    subprocess.Popen(' '.join([f'rm {x};' for x in file_list]), shell=True).wait() # basically sends the command as rm file1; rm file2; ...
    print('Done ', filename)
    return temp_dir_list
    


def align_bwa(filename, reference_index, threads, zipped, temp_dir_list, input_directory, output_directory):
    print('Starting', filename)

    # Get temporary name to make a directory (filename without extension)
    temp_name = filename.split('.')[0]
    # how is the temporary directory called
    temp_dir = f'temp_{temp_name}'

    # Make temporary directory if not already existing (main)
    if not os.path.exists(f'{output_directory}'):
        os.mkdir(fr'{output_directory}/')
    # make iteration specific dir  
    os.mkdir(fr'{output_directory}/{temp_dir}/')

    # append it to list of temporary directories
    temp_dir_list.append(temp_dir)


    # Copy fastq file in directory
    subprocess.Popen(f'cp "{input_directory}/{filename}" "{output_directory}/{temp_dir}"', shell=True).wait()

    # Move into temporary directory
    os.chdir(fr'{output_directory}/{temp_dir}')
    
    # Make GTF reference (script is in the folder alignment_scripts in gio's home)
    subprocess.Popen(f'python /home/gioele/alignment_scripts/makeGtf.py "{reference_index}" > "{output_directory}/{temp_dir}/"input.gtf', shell=True).wait()

    #make bwa index
    subprocess.Popen(f'bwa index "{reference_index}"', shell=True).wait()

    # Expand file with zcat if zipped
    if zipped:
        subprocess.Popen(f'zcat "{output_directory}/{temp_dir}/{filename}" > "{output_directory}/{temp_dir}/"{temp_name}.fastq', shell=True).wait()
        filename = f'{temp_name}.fastq'

    # Align with BWA
    subprocess.Popen(f'bwa mem -v 1 -c 2 -L 100 -t {threads} "{reference_index}" "{output_directory}/{temp_dir}/{filename}" > "{output_directory}/{temp_dir}/"alignment.sam', shell=True).wait()

    # Convert sam to bam
    subprocess.Popen(f'samtools view -bS "{output_directory}/{temp_dir}/alignment.sam" > "{output_directory}/{temp_dir}/"alignment.bam', shell=True).wait()

    print('Alignment complete for file ', filename)

    # Run feature counts
    subprocess.Popen(f'featureCounts -a "{output_directory}/{temp_dir}/input.gtf" -o "{output_directory}/{temp_dir}/"read_count.txt "{output_directory}/{temp_dir}/alignment.bam"', shell=True).wait()

    # Remove everything but read_count.txt
    # Get file list
    file_list = os.listdir()
    #Remove read_count.txt from file list
    file_list.remove('read_count.txt')

    # Remove all files but read_count.txt
    #subprocess.Popen(f'rm {" ".join(file_list)}').wait()
    subprocess.Popen(' '.join([f'rm {x};' for x in file_list]), shell=True).wait() # basically sends the command as rm file1; rm file2; ...
    print('Done ', filename)
    return temp_dir_list



def align_kallisto(filename, reference_index, threads, zipped, temp_dir_list, input_directory, output_directory):
    print('Starting', filename)

    # Get temporary name to make a directory (filename without extension)
    temp_name = filename.split('.')[0]
    # how is the temporary directory called
    temp_dir = f'temp_{temp_name}'

    # Make temporary directory if not already existing (main)
    if not os.path.exists(f'{output_directory}'):
        os.mkdir(fr'{output_directory}/')
    # make iteration specific dir  
    os.mkdir(fr'{output_directory}/{temp_dir}/')

    # append it to list of temporary directories
    temp_dir_list.append(temp_dir)
    
    
    # Copy fastq file in directory
    subprocess.Popen(f'cp "{input_directory}/{filename}" "{output_directory}/{temp_dir}"', shell=True).wait()
    
    # Move into temporary directory
    os.chdir(fr'{output_directory}/{temp_dir}')

    #Make kallisto index
    subprocess.Popen(f'kallisto index -i kallisto.index "{reference_index}"', shell=True).wait()

    # Expand file with zcat if zipped
    if zipped:
        subprocess.Popen(f'zcat "{output_directory}/{temp_dir}/{filename}" > "{output_directory}/{temp_dir}/"{temp_name}.fastq', shell=True).wait()
        filename = f'{temp_name}.fastq'

    # Run kallisto quantifier
    subprocess.Popen(f'kallisto quant --single -i kallisto.index -o "{output_directory}/{temp_dir}" -l 50 -s 1 -t {threads} --bias --single-overhang "{output_directory}/{temp_dir}/"{filename}', shell=True).wait()

    # Remove everything but read_count.txt
    # Get file list
    file_list = os.listdir()
    #Remove abundance.tsv from file list
    file_list.remove('abundance.tsv')

    # Remove all files but read_count.txt
    subprocess.Popen(' '.join([f'rm {x};' for x in file_list]), shell=True).wait() # basically sends the command as rm file1; rm file2; ...
    print('Done ', filename)
    return temp_dir_list








def append_to_df(append_to, df, aligner, filename = None):
    # IF append to df is empty
    if append_to.shape == (0,0):
        # append first row
        append_to['Geneid'] = df['Geneid']
    
    # Remove excess cols from df and rename it
    cols = df.columns
    # Get only cols of interest (first and last)
    cols = [cols[0], cols[-1]]
    # Get Df with cols of interest
    df = df[cols].copy()
    # If filename is not specified capture it from the DF last col
    if aligner == 'star':
        # Make mapping dict to rename cols (remove all that from last col name)
        rename_cols = {x:x.removesuffix('Aligned.sortedByCoord.out.bam') for x in cols}
        #remap col names
        df = df.rename(columns=rename_cols)
    elif aligner == 'bwa':
        # Rename columns! -> Given that columns are named as full path of bam file (ex /home/gioele/rat_fasta/cli/temp_first/alignment.bam)
        # Get new name from string.split('/')[-2].removeprefix('temp_') it 
        change_col = df.columns[-1]
        rename_cols = {change_col: change_col.split('/')[-2].removeprefix('temp_')}
        df = df.rename(columns=rename_cols)

    elif aligner == 'kallisto':
        # This is specific to kallisto
        # Cast col to integer (was float)
        df.est_counts = df.est_counts.astype(int)
        # Rename count column to name of file
        df = df.rename(columns={'est_counts': filename})
        
    # Merge dfs
    append_to = append_to.merge(df, how='outer', on='Geneid')

    return append_to



def send_email(recipient, output_name):
    body = 'Subject: Alignment complete \n\n' + f'Hello,\n\nYour alignment named {output_name} has completed!' + '\n\nRegards,\nBioSpyder Team'
    sender = 'tempo-portal@biospyder.com'

    # Initialise smtp objects
    try:
        smtpObj = smtplib.SMTP('smtp-mail.outlook.com', 587)  #smtp.office365.com
    except Exception as e:
        print(e)
        smtpObj = smtplib.SMTP_SSL('smtp-mail.outlook.com', 465)

    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login('tempo-portal@biospyder.com', '8nXiM7eTW-')
    smtpObj.sendmail(sender, recipient, body)
    smtpObj.quit()
    print(f'Email sent to {recipient}')



# need to: 
# get the total number of reads: zcat filename | wc -l  /4 -> bc 1 read every 4 lines 
# reads mapped: sum number of reads in count table
# unmapped: total - mapped
# percentage mapped mapped/total * 100#
# Need main file and read_count.txt
def get_report(input_directory, file_list, current_temp_dir, output_directory, append_to):
    # Get the total number of reads
    # from the file list, understand complete filename based on current temp dir
    print('starting')
    my_file = ''
    for file in file_list:
        if current_temp_dir.removeprefix('temp_') == file.split('.')[0]:
            my_file = file
            break
    if my_file == '':
        # append to df a col with values 0
        rows = [0,0,0,0]
        df = pd.DataFrame(rows, columns=['File_not_found'])
        append_to[col] = df[col]

        return append_to # need to modify this to let the user know something went wrong
    
    stdout = subprocess.check_output(f'zcat {input_directory}/{my_file} | wc -l', shell=True, encoding='utf-8')
    total_number_of_reads = int(int(stdout)/4)

    # Get the total number of reads in the count table (will be the ones mapped)
    # The directory is the output directory, the column is the current temp directory without temp_
    col = current_temp_dir.removeprefix('temp_')
    count_table = pd.read_csv(f'{output_directory}/{output_directory.split("/")[-1]}_count_table.csv')
    aligned_count = int(count_table[col].sum())


    # Get the number of unaligned reads
    unaligned_count = total_number_of_reads - aligned_count

    # Get percentage
    percentage_aligned = round((aligned_count / total_number_of_reads)*100, 2)


    #print(total_number_of_reads, aligned_count, unaligned_count, percentage_aligned, append_to)
    # JUST NEED TO COMPILE INTO DF AND MERGE TO INCOMING DF, REMEMBER TO CHECK IF DF IS EMPTY TO PUT FIRST Col IN
    
    # Make Df
    rows = [unaligned_count, aligned_count, total_number_of_reads, percentage_aligned]
    df = pd.DataFrame(rows, columns=[col])

    append_to[col] = df[col]

    return append_to







def run_aligner(aligner, reference_index, input_directory, file_list, output_name, output_directory, email=None, threads=8, mismatches = 2, comments=''):
    # User choices
    # reference_index
    # file_list
    # input_directory which is the directory where alignment files are

    is_zipped = lambda x: True if x.split('.')[-1] == 'gz' else False

    print('The following files will be included in the analysis: ', ', '.join(file_list))

    temp_output_directory = f'{output_directory}/{output_name}'

    temp_dir_list = []
    # For each file run alignment
    if aligner == 'star':
        for file in file_list:
            zipped = is_zipped(file)
            temp_dir_list = align_star(file, reference_index, threads, zipped, temp_dir_list, input_directory, temp_output_directory, mismatches=mismatches)
    elif aligner == 'bwa':
        for file in file_list:
            zipped = is_zipped(file)
            temp_dir_list = align_bwa(file, reference_index, threads, zipped, temp_dir_list, input_directory, temp_output_directory)
    elif aligner == 'kallisto':
        for file in file_list:
            zipped = is_zipped(file)
            temp_dir_list = align_kallisto(file, reference_index, threads, zipped, temp_dir_list, input_directory, temp_output_directory)
    else:
        raise Exception('Aligner not recognised')

    # Compile all read counts
    print('Starting compiling read count table')
    # For each temp folder, load df and append it to general one
    # declare empty df to append to
    append_to = pd.DataFrame()
    # For each temporary directory, create df and append cols of interest
    for dir in temp_dir_list:
        # if the aligner is kallisto, no need to skip first row, but need to skip last col
        if aligner == 'kallisto':
            df = pd.read_csv(f'{temp_output_directory}/{dir}/abundance.tsv', delimiter='\t')
            #remove last col + change first col name to Geneid
            df = df.iloc[:,:-1]
            df = df.rename(columns={'target_id': 'Geneid'})
            append_to = append_to_df(append_to, df, aligner, dir.removeprefix('temp_')) # Kallisto produces files differently from featureCount, so you need to adapt them to be the same
        else:
            df = pd.read_csv(f'{temp_output_directory}/{dir}/read_count.txt', delimiter='\t', skiprows=[0])
            append_to = append_to_df(append_to, df, aligner)


    # not in that one
    # If output directory not present, make it 
    if not os.path.exists(output_directory):
        os.mkdir(fr'{output_directory}')

    # Make directory specific to this experiment (named as the experiment)
    # This becomes the new output directory
    if not os.path.exists(fr'{output_directory}/{output_name}'):
        os.mkdir(fr'{output_directory}/{output_name}')
    output_directory = fr'{output_directory}/{output_name}'
    
    #Write created df to file !!!!!!!!!!!!!!! IF YOU WANT YOU CAN MAKE DIRECTORIES SPECIFIC TO THE OUTPUT NAME, MAYBE BEST
    outstring = f'{output_directory}/{output_name}_count_table.csv'
    append_to.to_csv(outstring, index=False)


    # Move file to desired directory (NOT anymore)
    #subprocess.Popen(f'mv {outstring} {output_directory}', shell=True).wait()  

    print('Wrote count table to ', output_directory)


    # Iterate through the folders and get the run stats!
    # Run stats = total reads, total reads mapped, total reads unmapped, percentage of mapped reads
    # For each temp folder
    # Declare df
    rows = ['Unmapped', 'Mapped', 'TotalReads', 'PercentMapped']
    mapped_unmapped = pd.DataFrame(rows, columns=[''])
    for dir in temp_dir_list:
        # need to: 
        # get the total number of reads: zcat filename | wc -l  /4 -> bc 1 read every 4 lines 
        # reads mapped: sum number of reads in count table
        # unmapped: total - mapped
        # percentage mapped mapped/total * 100#
        # Need main file and read_count.txt
        mapped_unmapped = get_report(input_directory, file_list, dir, output_directory, mapped_unmapped)


    mapped_unmapped_outstring = outstring = f'{output_directory}/{output_name}_mapped_unmapped.csv'
    mapped_unmapped.to_csv(mapped_unmapped_outstring, index=False)

    # Move out of the file-specific temp folders and go to general analysis temp folder
    os.chdir(fr'{temp_output_directory}')

    # Remove all file-specific temp folders 
    for dir in temp_dir_list:
        # Do it in 2 steps just in case
        subprocess.Popen(f'rm {temp_output_directory}/{dir}/{"read_count.txt" if aligner != "kallisto" else "abundance.tsv"}', shell=True).wait()
        subprocess.Popen(f'rmdir {temp_output_directory}/{dir}/', shell=True).wait()
        print('Removed temporary directory ', dir)
    
    # Remove main temp folder (to do so move one level above) (not done anymore as needed it for all output files)
    # print('Removing main temporary directory')
    # os.chdir(fr'{output_directory}')
    # subprocess.Popen(f'rmdir "{temp_output_directory}"', shell=True).wait()

    date = datetime.datetime.today().strftime('%Y-%m-%d')

    print('Writing report')
    report_string = f"""Alignment report
File prefix: {output_name},
Output directory: {output_directory},
Experiment of reference: {input_directory},
User's email: {email},
Reference genome: {reference_index},
Aligner: {aligner},
N of aligned files: {len(file_list)},
List of files: {', '.join(file_list)},
Date: {date},
Additional comments: {comments if comments != '' else 'None'}
"""

    # Write out log file
    with open(f'{output_directory}/{output_name}_run_log.txt', 'w') as outfile:
        outfile.write(report_string)

    print('Processes completed')

    #Send email to the user!
    if email != None:
        print('Sending email')
        send_email(email, output_name)
        

if __name__ == '__main__':
    # # Reference index path
    # # How many threads?
    # threads = 8
    # # User email
    # email = 'gioelemook97@gmail.com'
    # aligner = 'kallisto' #'star'
    # reference_genome = 'rat'
    # input_directory = '/home/gioele/rat_fasta/loop'
    # input_zipped = None
    # #This is derived from the input 
    # output_name = 'kallisto'
    # #Call aligner
    # #run_aligner(aligner, reference_genome, input_directory, output_name)
    # #send_email('gioelemook97@gmail.com')







    import argparse

    parser = argparse.ArgumentParser(description="Tool to align your TempoSeq sequences and extract a feature count table. It allows to alignment with star, bwa and kallisto. Version specific for TempoPortal")
    parser.add_argument('-i', '--input-directory', required=True, help='Directory where the fastq files are. Input "." for current directory, or the full directory path')
    parser.add_argument('-a', '--aligner', required=True, help='Select the required aligner, options: star, bwa, kallisto')
    parser.add_argument('-g', '--reference-genome', required=True, help='Select the required reference genome; give complete path to .fa file') # If you add here add to index_reference_dict
    parser.add_argument('-o', '--output-name', required=True, help='Prefix for output name')
    parser.add_argument('-f', '--file-list', required=True, help='A comma separated file list eg file1,file2,file3')
    parser.add_argument('-d', '--output-dir', required=True, help='Directory where redirect output')
    parser.add_argument('-e', '--email', required=True, help='User email')
    parser.add_argument('-t', '--threads', required=False, help='Number of thread used, default: 8')
    parser.add_argument('-m', '--mismatches', required=False, type=int, help='Select number of allowed mismatches (only applicable on STAR). Default: 2.')
    parser.add_argument('-c', '--comments', required=False, help='Any additional comment')


    args = vars(parser.parse_args())
    input_directory = args['input_directory']
    aligner = args['aligner']
    reference_genome = args['reference_genome']
    file_list = args['file_list']
    #unpack file list
    file_list = [x for x in file_list.split(',')]

    output_directory = args['output_dir']
    output_name = args['output_name']

    email = args['email']

    threads = args['threads'] or 8
    mismatches = args['mismatches'] or 2

    comments = args['comments'] or ''






    #print(f'Options: input directory {input_directory}, aligner {aligner}, reference genome {reference_genome}, output name {output_name}, threads {threads}, input zipped {input_zipped}, specific files {specific_files}, mismatches {mismatches} (only applied to STAR)')
    
    # python align_files_server.py -a {aligner} -g {genome} -i {complete_directory} -f {','.join(file_list)} -o {output_name} -d {output_directory} -e {email} -t {threads} -m {mismatches}

    # rows = ['Unmapped', 'Mapped', 'TotalReads', 'PercentMapped']
    # mapped_unmapped = pd.DataFrame(rows, columns=[''])

    # get_report('/home/gioele/tempo_portal_temp/users/gio/raw_reads/BIOS3030', ['first.fastq.gz'], 'temp_first', '/home/gioele/tempo_portal_temp/aligned/BIOS3030/to_study', mapped_unmapped)

    run_aligner(aligner, reference_genome, input_directory, file_list, output_name, output_directory, email, threads, mismatches, comments)
    #[aligner, genome, complete_directory, selected, output_name, output_directory, email, threads, mismatches]
