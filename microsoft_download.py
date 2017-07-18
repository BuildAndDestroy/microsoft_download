#!/usr/bin/env python

import cookielib
import itertools
import logging
import os
import re
import urllib2

import wget


class Microsoft(object):
    """
    Scrape Microsoft url for PDF downloads.
    """

    def __init__(self, url1):
        self.microsoft_url = url1
        self.cookie = cookielib.CookieJar()

    def proc_site(self):
        """Read website and spit it out."""

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))

        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')]

        url = {
            'url1': self.microsoft_url
        }

        request_html = urllib2.Request(url['url1'])
        response_query = urllib2.urlopen(request_html)

        contents = response_query.read().splitlines()
        return contents


def obtain_file_names(processed_site):
    """Take file names from the website's html."""
    pdf_file_name = '<td valign="top" width="673"><font size="2" face="Arial">'
    file_name_lines = (
        line for line in processed_site if pdf_file_name in line)
    regex = re.compile(
        r'^\D\w+\s\w+\D+673\D+\d\D\s\w+\W+\w+\W+(?P<pdf_file>.*)</font>')
    file_names = []
    for line in file_name_lines:
        match = re.search(regex, line)
        if not match:
            print '>>> No file names found!'
            return
        file_names.append(match.group('pdf_file'))
    return file_names


def obtain_urls(processed_site):
    """Take downloadable URLs from the website's html."""
    html_url_string = ('<td width="77"><a ', '<td width="77"><font size="2" face="Arial"><a ')
    url_lines = []
    for line in processed_site:
        if html_url_string[0] in line or html_url_string[1] in line:
            url_lines.append(line)
    # return url_lines
    regex = re.compile(
        r'(^\W\D{2}\s\D{5}\W{2}\d{2}\W{3}\w\s\w{4}\W{2}|^\W\D{2}\s\D{5}\W{2}\d{2}\W{3}\w+\s\w+\D+\d\D\s\w+\W+\w+\w+\W+\w\s\w+\W+)(?P<url>\w{4}\W{3}\w{6}\W\w{2}\W.{6,7})')
    urls = []
    for line in url_lines:
        match = re.search(regex, line)
        if not match:
            print '>>> No URL\'s found!'
            return
        urls.append(match.group('url'))
    return urls

def count_urls(url_downloads):
    """Used for testing, this helps with verifying how many URLs exist."""
    counter = 0
    if not url_downloads:
        print '>>> No URL\'s to count!'
        return
    for number in url_downloads:
        counter += 1
    return counter

def count_file_names(file_names):
    """Used for testing, this helps with verifying how many files exist."""
    counter = 0
    if not file_names:
        print '>>> No files to count!'
        return
    for number in file_names:
        counter += 1
    return counter

def download_pdf(url_downloads, file_names):
    """Final function to download all free PDF's."""
    for url, name in itertools.izip(url_downloads, file_names):
        # print url, name
        print '\r\n[*] Downloading {}'.format(url)
        try:
            wget.download(url)
        except:
            print '>>> Unable to download!'
        print '\r\n[*] Changing file name from {} to {}'.format(wget.filename_from_url(url), name)
        try:
            os.rename(wget.filename_from_url(url), '{}.pdf'.format(name))
        except:
            print '>>> No file name to change!'


def main():
    """Pull Microsoft's downloadable URLs and correct the file names."""
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    microsoft_request = Microsoft(
        'https://blogs.msdn.microsoft.com/mssmallbiz/2017/07/11/largest-free-microsoft-ebook-giveaway-im-giving-away-millions-of-free-microsoft-ebooks-again-including-windows-10-office-365-office-2016-power-bi-azure-windows-8-1-office-2013-sharepo/')
    logging.info('[*] Processing website.')
    processed_site = microsoft_request.proc_site()

    # print processed_site
    logging.info('[*] Obtaining URL\'s for download.')
    url_downloads = obtain_urls(processed_site)

    logging.info('[*] Obtainning PDF file names.')
    file_names = obtain_file_names(processed_site)

    logging.info('[*] Number of URLS:')
    counted_urls = count_urls(url_downloads)
    print counted_urls

    logging.info('[*] Number of File Names:')
    counted_names = count_file_names(file_names)
    print counted_names

    if counted_urls is not counted_names:
        print 'Download URL\'s does not equal the amount of file names.'
        return

    logging.info('[*] Downloading PDF Files.')
    download_pdf(url_downloads, file_names)


if __name__ == '__main__':
    main()
