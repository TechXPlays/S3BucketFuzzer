import argparse
import os
import requests
import csv
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def check_public_bucket(bucket_name, results_text_file, results_csv_file):
    full_url = f"http://{bucket_name}.s3.amazonaws.com"

    try:
        response = requests.get(full_url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        if soup.find('listbucketresult'):
            print(f"Working bucket: {full_url}")
            with open(results_text_file, 'a') as text_file:
                text_file.write(f"Working Bucket: {full_url}\n")
            with open(results_csv_file, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([full_url, 'Working Bucket'])
        elif soup.find('error'):
            print(f"Bucket {full_url} does not exist or is not publicly accessible.")
            with open(results_text_file, 'a') as text_file:
                text_file.write(f"Non-existent or Private Bucket: {full_url}\n")
            with open(results_csv_file, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([full_url, 'Non-existent or Private Bucket'])
        else:
            print(f"Unable to determine the status of {full_url}.")
            with open(results_text_file, 'a') as text_file:
                text_file.write(f"Unknown Status: {full_url}\n")
            with open(results_csv_file, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([full_url, 'Unknown Status'])
    except requests.RequestException as e:
        print(f"Error checking bucket {full_url}: {e}")
        with open(results_text_file, 'a') as text_file:
            text_file.write(f"Error: {full_url}\n")
        with open(results_csv_file, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([full_url, 'Error'])
    finally:
        print(f"Result for {full_url} saved.")

def main():
    parser = argparse.ArgumentParser(description='Public S3 Bucket Scanner')
    parser.add_argument('--wordlist', default='wordlist.txt', help='Path to the wordlist file')
    parser.add_argument('--threads', type=int, default=5, help='Number of threads')

    args = parser.parse_args()
    wordlist_file = args.wordlist
    num_threads = args.threads

    if not os.path.isabs(wordlist_file):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        wordlist_file = os.path.join(script_directory, wordlist_file)

    wordlist_name = os.path.splitext(os.path.basename(wordlist_file))[0]
    
    results_text_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'Results-{wordlist_name}.txt')
    results_csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'Results-{wordlist_name}.csv')

    # Writing headers to the CSV file
    with open(results_csv_file, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Bucket URL', 'Result Type'])

    with open(wordlist_file, 'r') as file:
        wordlist = [line.strip() for line in file.readlines()]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(lambda bucket: check_public_bucket(bucket, results_text_file, results_csv_file), wordlist)

if __name__ == "__main__":
    main()
