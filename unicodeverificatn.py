# Copyright (c) 2005, Neil Harris
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the author nor the names of its contributors may be
#   used to endorse or promote products derived from this software without
#   specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Test program for analyzing IDNA spoofing using homographs
# Version 1.1, 8 Feb 2005

# Note the disclaimer above, and also note that at least the following issues
# are still unresolved:
# * what if the local script has/uses its own digits as well as ASCII ones?
# * what if the local script has/uses its own hyphen?
# * BiDi issues?

import string, unicodedata, encodings.idna

# These ranges were generated ad-hoc from available data;
# they need to be regenerated from authoritative data
ranges = [
	(0L, 127L, 'Basic Latin'),
	(128L, 255L, 'Latin-1 Supplement'),
	(256L, 383L, 'Latin Extended-A'),
	(384L, 591L, 'Latin Extended-B'),
	(592L, 687L, 'IPA Extensions'),
	(688L, 767L, 'Spacing Modifier Letters'),
	(768L, 879L, 'Combining Diacritical Marks'),
	(880L, 1023L, 'Greek and Coptic'),
	(1024L, 1279L, 'Cyrillic'),
	(1280L, 1327L, 'Cyrillic Supplement'),
	(1328L, 1423L, 'Armenian'),
	(1424L, 1535L, 'Hebrew'),
	(1536L, 1791L, 'Arabic'),
	(1792L, 1919L, 'Syriac'),
	(1920L, 2303L, 'Thaana'),
	(2304L, 2431L, 'Devanagari'),
	(2432L, 2559L, 'Bengali'),
	(2560L, 2687L, 'Gurmukhi'),
	(2688L, 2815L, 'Gujarati'),
	(2816L, 2943L, 'Oriya'),
	(2944L, 3071L, 'Tamil'),
	(3072L, 3199L, 'Telugu'),
	(3200L, 3327L, 'Kannada'),
	(3328L, 3455L, 'Malayalam'),
	(3456L, 3583L, 'Sinhala'),
	(3584L, 3711L, 'Thai'),
	(3712L, 3839L, 'Lao'),
	(3840L, 4095L, 'Tibetan'),
	(4096L, 4255L, 'Myanmar'),
	(4256L, 4351L, 'Georgian'),
	(4352L, 4607L, 'Hangul Jamo'),
	(4608L, 5023L, 'Ethiopic'),
	(5024L, 5119L, 'Cherokee'),
	(5120L, 5759L, 'Unified Canadian Aboriginal Syllabic'),
	(5760L, 5791L, 'Ogham'),
	(5792L, 5887L, 'Runic'),
	(5888L, 5919L, 'Tagalog'),
	(5920L, 5951L, 'Hanunoo'),
	(5952L, 5983L, 'Buhid'),
	(5984L, 6015L, 'Tagbanwa'),
	(6016L, 6143L, 'Khmer'),
	(6144L, 6399L, 'Mongolian'),
	(6400L, 6479L, 'Limbu'),
	(6480L, 6623L, 'Tai Le'),
	(6624L, 7423L, 'Khmer Symbols'),
	(7424L, 7679L, 'Phonetic Extensions'),
	(7680L, 7935L, 'Latin Extended Additional'),
	(7936L, 8191L, 'Greek Extended'),
	(8192L, 8303L, 'General Punctuation'),
	(8304L, 8351L, 'Superscripts and Subscripts'),
	(8352L, 8399L, 'Currency Symbols'),
	(8400L, 8447L, 'Combining Marks for Symbols'),
	(8448L, 8527L, 'Letterlike Symbols'),
	(8528L, 8591L, 'Number Forms'),
	(8592L, 8703L, 'Arrows'),
	(8704L, 8959L, 'Mathematical Operators'),
	(8960L, 9215L, 'Miscellaneous Technical'),
	(9216L, 9279L, 'Control Pictures'),
	(9280L, 9311L, 'Optical Character Recognition'),
	(9312L, 9471L, 'Enclosed Alphanumerics'),
	(9472L, 9599L, 'Box Drawing'),
	(9600L, 9631L, 'Block Elements'),
	(9632L, 9727L, 'Geometric Shapes'),
	(9728L, 9983L, 'Miscellaneous Symbols'),
	(9984L, 10191L, 'Dingbats'),
	(10192L, 10223L, 'Miscellaneous Mathematical Symbols-A'),
	(10224L, 10239L, 'Supplemental Arrows-A'),
	(10240L, 10495L, 'Braille Patterns'),
	(10496L, 10623L, 'Supplemental Arrows-B'),
	(10624L, 10751L, 'Miscellaneous Mathematical Symbols-B'),
	(10752L, 11007L, 'Supplemental Mathematical Operators'),
	(11008L, 11903L, 'Miscellaneous Symbols and Arrows'),
	(11904L, 12031L, 'CJK Radicals Supplement'),
	(12032L, 12271L, 'Kangxi Radicals'),
	(12272L, 12287L, 'Ideographic Description Characters'),
	(12288L, 12351L, 'CJK Symbols and Punctuation'),
	(12352L, 12447L, 'Hiragana'),
	(12448L, 12543L, 'Katakana'),
	(12544L, 12591L, 'Bopomofo'),
	(12592L, 12687L, 'Hangul Compatibility Jamo'),
	(12688L, 12703L, 'Kanbun'),
	(12704L, 12783L, 'Bopomofo Extended'),
	(12784L, 12799L, 'Katakana Phonetic Extensions'),
	(12800L, 13055L, 'Enclosed CJK Letters and Months'),
	(13056L, 13311L, 'CJK Compatibility'),
	(13312L, 19903L, 'CJK Unified Ideographs Extension A'),
	(19904L, 19967L, 'Yijing Hexagram Symbols'),
	(19968L, 40959L, 'CJK Unified Ideographs'),
	(40960L, 42127L, 'Yi Syllables'),
	(42128L, 44031L, 'Yi Radicals'),
	(44032L, 55295L, 'Hangul Syllables'),
	(55296L, 56319L, 'High Surrogates'),
	(56320L, 57343L, 'Low Surrogates'),
	(57344L, 63743L, 'Private Use Area'),
	(63744L, 64255L, 'CJK Compatibility Ideographs'),
	(64256L, 64335L, 'Alphabetic Presentation Forms'),
	(64336L, 65023L, 'Arabic Presentation Forms-A'),
	(65024L, 65055L, 'Variation Selectors'),
	(65056L, 65071L, 'Combining Half Marks'),
	(65072L, 65103L, 'CJK Compatibility Forms'),
	(65104L, 65135L, 'Small Form Variants'),
	(65136L, 65279L, 'Arabic Presentation Forms-B'),
	(65280L, 65519L, 'Halfwidth and Fullwidth Forms'),
	(65520L, 65535L, 'Specials'),
	(65536L, 65663L, 'Linear B Syllabary'),
	(65664L, 65791L, 'Linear B Ideograms'),
	(65792L, 66303L, 'Aegean Numbers'),
	(66304L, 66351L, 'Old Italic'),
	(66352L, 66431L, 'Gothic'),
	(66432L, 66559L, 'Ugaritic'),
	(66560L, 66639L, 'Deseret'),
	(66640L, 66687L, 'Shavian'),
	(66688L, 67583L, 'Osmanya'),
	(67584L, 118783L, 'Cypriot Syllabary'),
	(118784L, 119039L, 'Byzantine Musical Symbols'),
	(119040L, 119551L, 'Musical Symbols'),
	(119552L, 119807L, 'Tai Xuan Jing Symbols'),
	(119808L, 131071L, 'Mathematical Alphanumeric Symbols'),
	(131072L, 194559L, 'CJK Unified Ideographs Extension B'),
	(194560L, 917503L, 'CJK Compatibility Ideographs Supplement'),
	(917504L, 917759L, 'Tags'),
	(917760L, 983039L, 'Variation Selectors Supplement'),
	(983040L, 1048575L, 'Supplementary Private Use Area-A'),
	(1048576L, 4294967294L, 'Supplementary Private Use Area-B')
]

# Again, this needs to be generated carefully on a case-by-case basis
blacklist = [
    'Box Drawing', 'Block Elements', 'Geometric Shapes',
    'Miscellaneous Symbols', 'Dingbats', 'Byzantine Musical Symbols',
    'Musical Symbols', 'Mathematical Alphanumeric Symbols',
    'Letterlike Symbols', 'Number Forms', 'Arrows',
    'Mathematical Operators', 'Miscellaneous Technical',
    'Spacing Modifier Letters', 'Combining Marks for Symbols',
    'Control Pictures', 'Optical Character Recognition',
    'Enclosed Alphanumerics', 'Miscellaneous Mathematical Symbols-A',
    'Supplemental Arrows-A', 'Supplemental Arrows-B',
    'Miscellaneous Mathematical Symbols-B',
    'Supplemental Mathematical Operators', 'Miscellaneous Symbols and Arrows',
    'High Surrogates', 'Low Surrogates', 'Private Use Area',
    'Alphabetic Presentation Forms', 'Small Form Variants',
    'Halfwidth and Fullwidth Forms', 'Variation Selectors',
    'Tags', 'Specials', 'Variation Selectors Supplement',
    'Supplementary Private Use Area-A',
    'Supplementary Private Use Area-B',
    'Superscripts and Subscripts', 'Currency Symbols',
    'Linear B Syllabary', 'Linear B Ideograms',
    'Shavian', 'Deseret', 'Ugaritic', 'Old Italic', 'Ogham', 'Runic',
    'General Punctuation', 'IPA Extensions', 'Phonetic Extensions',
    'Tai Xuan Jing Symbols', 'Alphabetic Presentation Forms',
    'Halfwidth and Fullwidth Forms',
    'BADRANGE'
]

special_cases = [
    ['Katakana', 'Hiragana', 'Bopomofo', 'Latin', 'CJK'], # Japanese
    ['Hangul', 'Latin', 'CJK'], # Korean
    ['Cyrillic', 'Cyrillic Supplement'], # Cyrillic family
    ['Greek and Coptic', 'Greek Extended'] # Greek
]

def codepoint_to_range(n):
    # The special case
    if n < 128 and chr(n) in "01234567890-":
        return "DNSRANGE"
    # A dumb linear search: there are only 124 ranges
    # Make this better if it becomes a problem
    for r in ranges:
        if n >= r[0] and n <= r[1]:
            return r[2]
    # otherwise
    return "BADRANGE"

# Same as above, but folds some ranges to be the same
def codepoint_to_approx_range(n):
    range = codepoint_to_range(n)
    if range[:4] == 'CJK ':
        return 'CJK'
    if range[:5] == 'Latin':
        return 'Latin'    
    return range

# This gives the Unicode category for a character
def unicat(code):
    return unicodedata.category(unichr(code))

def is_subset_of(a, b):
    for element in a:
        if element not in b:
            return 0
    return 1

# Takes a Unicoded label string, and checks it
def checklabel(ustr):
    # Nameprep, then generate a codepoint list
    codepoints = [ord(x) for x in encodings.idna.nameprep(ustr)]
    # Empty labels are bad 
    if len(codepoints) == 0:
        return "BAD:EMPTYLABEL"
    # Now check all codepoints to see if they are punctuation
    # other than the hyphen...
    for code in codepoints:
        if unichr(code) != "-":
            cat = unicat(code)
            if cat[0] == 'P': return "BAD:PUNCTUATION"
            if cat[0] == 'Z': return "BAD:SEPARATOR"
            if cat == 'Cc': return "BAD:CONTROLCHAR"
            if cat[0] == 'C':
                print code
                return "BAD:OTHERCONTROL"
    # Now check that the _first_ character is _not_ a mark,
    # as this would have no character to combine with,
    # and some implementations will render this as a single char,
    # possibly presenting a spoofing opportunity
    if unicat(codepoints[0])[0] == 'M':
        return "BAD:LEADINGMARK"
    # Compute the code-point ranges
    ranges = [codepoint_to_approx_range(x) for x in codepoints]
    # Use a temp dictionary to do a "uniq" operation
    ranges = {}.fromkeys(ranges, 1).keys()
    # Check against the blacklist  
    for r in ranges:
        if r in blacklist:
            return "BAD:BLACKLISTED"
    # Just one character range, plus optional DNSRANGE?
    ranges = [x for x in ranges if x != 'DNSRANGE']
    if len(ranges) <= 1:
        return "OK"
    # OK, now we need to check for special cases
    for case in special_cases:
        if is_subset_of(ranges, case):
            return "OK"
    # Otherwise, we have mixed writing-system/languages in this label
    return "BAD:MIXEDLANG"

# Check a FQDN
def check_name(name):
    for label in string.split(name, '.'):
        val = checklabel(label)
        if val != "OK":
            return val
    return "OK"

# These test vectors are Unicoded in this source file, to avoid transcoding
# problems when copying the source code.
# Note that several of these test vectors, taken from the test file
# attached earlier, contain characters which don't seem to be assigned
# at all... what's up?
test_vectors = [
    u"www.paypal.com", # real  
    u'www.p\u0430ypal.com',  # fake 'a': CYRILLIC SMALL LETTER A
    u'www.pa\u1091pal.com', # fake 'y'
    u"www.microsoft.com", # real
    u"www.micr\u1086soft.com", # fake 'o'
    u'www.google.com', # real
    u'www.googl\u1072.com', # fake 'e'
    u'www\u3002google.com', # fake '.': using IDEOGRAPHIC FULL STOP
    u'www\u05B4google.com', # another fake '.'
    u'www.google\u200C.com', # adding a ZWNJ: nameprep will strip this?
    u'www.google .com', # adding a space
    u'www.google..com'  # empty label
    ]

for vec in test_vectors:
    print 
    print vec
    print repr(vec)
    print repr(encodings.idna.nameprep(vec))
    print check_name(vec)


