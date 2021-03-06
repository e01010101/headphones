#  This file is part of Headphones.
#
#  Headphones is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Headphones is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Headphones.  If not, see <http://www.gnu.org/licenses/>.

import re
import urllib
from xml.dom import minidom
import htmlentitydefs

from headphones import logger

def getLyrics(artist, song):

    params = {  "artist": artist.encode('utf-8'),
                "song": song.encode('utf-8'),
                "fmt": 'xml'
                }
                
    searchURL = 'http://lyrics.wikia.com/api.php?' + urllib.urlencode(params)
    
    try:
        data = urllib.urlopen(searchURL).read()
    except Exception, e:
        logger.warn('Error opening: %s. Error: %s' % (searchURL, e))
        return
    
    try:
        parseddata = minidom.parseString(data)
    except Exception, e:
        logger.warn('Error parsing data from url: %s. Error: %s' % (searchURL, e))
        return
    
    url = parseddata.getElementsByTagName("url")
    
    if url:
        lyricsurl = url[0].firstChild.nodeValue
    else:
        logger.info('No lyrics found for %s - %s' % (artist, song))
        return
    
    try:    
        lyricspage = urllib.urlopen(lyricsurl).read()
    except Exception, e:
        logger.warn('Error fetching lyrics from: %s. Error: %s' % (lyricsurl, e))
        return
        
    m = re.compile('''<div class='lyricbox'><div class='rtMatcher'>.*?</div>(.*?)<!--''').search(lyricspage)
    
    if not m:
        m = re.compile('''<div class='lyricbox'><span style="padding:1em"><a href="/Category:Instrumental" title="Instrumental">''').search(lyricspage)
        if m:
            return u'(Instrumental)'
        else:
            logger.warn('Cannot find lyrics on: %s' % lyricsurl)
            return
        
    lyrics = convert_html_entities(m.group(1)).replace('<br />', '\n')
    lyrics = re.sub('<.*?>', '', lyrics)
    
    return lyrics

def convert_html_entities(s):
    matches = re.findall("&#\d+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
                name = hit[2:-1]
                try:
                        entnum = int(name)
                        s = s.replace(hit, unichr(entnum))
                except ValueError:
                        pass

    matches = re.findall("&\w+;", s)
    hits = set(matches)
    amp = "&amp;"
    if amp in hits:
        hits.remove(amp)
    for hit in hits:
        name = hit[1:-1]
        if htmlentitydefs.name2codepoint.has_key(name):
                s = s.replace(hit, unichr(htmlentitydefs.name2codepoint[name]))
    s = s.replace(amp, "&")
    return s
