import os
import csv
from pathos.multiprocessing import ProcessingPool as Pool
from pathos.multiprocessing import ProcessingPool as Pool
from cc import SearchResultsScraper
import matplotlib.pyplot as plt
import numpy as np

def run_scraper(cat):
    cc_types = {'Use_Share': 'fm'}
    file_path = os.path.join('queries', f'{cat}.txt')
    scraper = SearchResultsScraper(file_path, cc_types, cat)
    return scraper

def process_file(filename):
    if filename.endswith(".txt"):
        name_without_extension = filename[:-4]
        run_scraper(name_without_extension)

def main():
    directory = './data_by_cat'
    all_data_text = "category,norm_url,cc_url,query,CC_results,total_results,CC_percent\n"

    # List all files in the 'queries' directory and filter for .txt files
    files = [f for f in os.listdir("queries") if f.endswith(".txt")]

    # Create a processing pool with 5 processes
 #   with Pool(5) as pool:
  #      pool.map(process_file, files)

    # Concatenate CSV data from files
   # for filename in os.listdir(directory):
    #    if filename.endswith('.csv'):
     #       with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
      #          all_data_text += file.read() + "\n"

    # Output all data to a CSV file and rename it
    output_filepath = 'CC_data.txt'
    with open(output_filepath, 'w', encoding='utf-8') as file:
        file.write(all_data_text)
    os.rename(output_filepath, "CC_data.csv")

    # Filter rows with CC_percent != 0
    filename = "CC_data2.csv"
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader if float(row['CC_percent']) != 0]

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = rows[0].keys() if rows else []
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("Rows with CC_percent = 0.0 have been removed.")

    if not os.path.exists("graphs"):
        os.makedirs("graphs")


    filename = "CC_data.csv"
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)


    catly_avg = {}
    for row in rows:
        cat = row['catagory']
        cc_percent = float(row['CC_percent'])
        if cat in catly_avg:
            catly_avg[cat].append(cc_percent)
        else:
            catly_avg[cat] = [cc_percent]


    all_cats_avg = [item for sublist in catly_avg.values() for item in sublist]
    avg_cc_percent_all = sum(all_cats_avg) / len(all_cats_avg)
    other_percent_all = 100 - avg_cc_percent_all
    labels_all = ['Average CC_percent', 'Other results']
    sizes_all = [avg_cc_percent_all, other_percent_all]
    colors_all = ['blue', 'red']
    plt.figure()
    plt.pie(sizes_all, labels=labels_all, colors=colors_all, autopct='%1.1f%%', startangle=140)
    plt.title('All Catagory Queries')
    plt.savefig('graphs/pie_chart_all.png')
    plt.close()


    for cat, percentages in catly_avg.items():
        avg_cc_percent = sum(percentages) / len(percentages)
        other_percent = 100 - avg_cc_percent
        labels = ['Average CC_percent', 'Other results']
        sizes = [avg_cc_percent, other_percent]
        colors = ['blue', 'red']
        plt.figure()
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title(f'cat {cat}')
        plt.savefig(f'graphs/pie_chart_{cat}.png')
        plt.close()


    catly_data = {}
    for row in rows:
        cat = row['catagory']
        cc_percent = float(row['CC_percent'])
        cc_results = int(row['CC_results'])
        total_results = int(row['total_results'])
        other_results = total_results
        if cat in catly_data:
            catly_data[cat]['cc_percent'].append(cc_percent)
            catly_data[cat]['cc_results'].append(cc_results)
            catly_data[cat]['other_results'].append(other_results)
        else:
            catly_data[cat] = {'cc_percent': [cc_percent], 'cc_results': [cc_results], 'other_results': [other_results]}


    cats = sorted(catly_data.keys())
    avg_cc_percent = [sum(catly_data[cat]['cc_percent']) / len(catly_data[cat]['cc_percent']) for cat in cats]
    avg_cc_results = [sum(catly_data[cat]['cc_results']) / len(catly_data[cat]['cc_results']) for cat in cats]
    avg_other_results = [sum(catly_data[cat]['other_results']) / len(catly_data[cat]['other_results']) for cat in cats]


    fig, ax1 = plt.subplots(figsize=(12, 10))  


    color = 'tab:red'
    ax1.set_xlabel('Catagory', fontsize=12)
    ax1.set_ylabel('Average Percentage', color=color, fontsize=12)
    ax1.plot(cats, avg_cc_percent, color=color, marker='o', label='Average CC Percentage')
    ax1.tick_params(axis='y', labelcolor=color, labelsize=10)
    ax1.grid(True)



    ax1.set_xticks(cats)
    ax1.set_xticklabels(cats, rotation=45, fontsize=10)


    ax2 = ax1.twinx()


    color = 'tab:blue'
    ax2.set_ylabel('Results (Log Scale)', color=color, fontsize=12)  
    ax2.plot(cats, avg_cc_results, color=color, linestyle='--', marker='s', label='CC Results')
    ax2.plot(cats, avg_other_results, color='tab:blue', linestyle='-.', marker='^', label='Other Results')
    ax2.tick_params(axis='y', labelcolor=color, labelsize=10)


    max_results = max(max(avg_cc_results), max(avg_other_results))
    y_scale = 1000  
    ax2.set_ylim(0, (max_results // y_scale + 1) * y_scale)


    fig.legend(loc='upper right', bbox_to_anchor=(1, 1), fontsize=10)

    plt.title('Average Percentage and Results Over the cats', fontsize=14)
    plt.savefig('graphs/average_percentage_and_results_line_graph.png')
    plt.show()
    print("All cats have been processed and consolidated. Finished!")

if __name__ == "__main__":
    main()
