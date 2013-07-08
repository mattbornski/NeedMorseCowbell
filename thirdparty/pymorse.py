# -*- coding: utf-8 -*-

'''The MIT License (MIT)

Copyright (c) 2013 Jochen Schnelle

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''


__author__ = "Jochen Schnelle <jochenschnelle@yahoo.de>"
__version__ = "20130704"
__licence__ = "MIT"


import logging

class MorseCodeError(Exception):

    def __init__(self, error_name, error_text):
        self.args = (error_name, error_text)
        self.error_name = error_name
        self.error_text = error_text

    def __str__(self):
        return repr('{0}: {1}'.format(self.error_name, self.error_text))


class MorseCode(object):
    '''The MorseCode class contains a number of functions to convert text into
    morse code and the other way round.
    The morse code follows strictly the commonly accepted and applied
    ITU-R M.1677-1 recommendation. Thus, any characters not contained within
    the ITU recommendation (e.g. the exclamation mark ! or special characters
    like German Umlauts) cannot be converted into morse code.

    Using the Morsecode class works as follows:

    >>> from pymorsecode import MorseCode
    >>> m = MorseCode()
    >>> m.to_morse('Hello')
    '.... . .-.. .-.. ---'
    >>> m.from_morse('. - .-')
    'ETA'

    The morse code is represented by the dot . and the minus sign - . These
    settings are strict and cannot be changed, other characters to represent
    the morse code are not allowed.

    By default, the MorseCode class uses three blank spaces to separate words
    within morse code and a single blank space to separate the characters
    within morse code:

    >>> m.to_morse('Hello World')
    '.... . .-.. .-.. ---   .-- --- .-. .-.. -..'

    The separators for words and characters are held in the class attributes
    "word_sep" and "char_sep".

    Say the pip sign | is used as a word separator within morse code:

    >>> m.word_sep = '|'
    >>> m.from_morse('.... . .-.. .-.. ---|.-- --- .-. .-.. -..')
    'HELLO WORLD'

    And this works of course, too, then translating to morse code:

    >>> m.to_morse('Hello World')
    '.... . .-.. .-.. ---|.-- --- .-. .-.. -..'

    In case invalid characters should be converted, an MorseCodeError is
    raised:

    >>> m.to_morse('abc%')
    ...
    pymorsecode.MorseCodeError: 'Invalid input text: Input text contains invalid characters: %'

    An MorseCodeError is raised as well when trying to convert invalid morse
    code sequences to text:

    m.from_morse('.------')
    ...
    pymorsecode.MorseCodeError: 'Illegal morse code sequence: Morse code contains a non-validcode sequence'

    In case translation should not be aborted by raising an exception, but a
    place holder for the invalid character respectively sequence should be
    used, set the class attribute "strict_mode" to False.

    >>> m.strict_mode = False
    
    As an alternative, an instance of the class can be created, providing
    an argument for the strict_mode:

    >>> m2 = MorseCode(strict_mode=False)
    >>> m2.to_morse('abc%')
    WARNING:MorseCode:Given text contains an invalid characters %. Will
    use ? as placeholder in output
    '.- -. . .  -.-.  ?'
    >>> m2.from_morse('. - .------')
    WARNING:MorseCode:Found illegal morse code sequence .------. Will use
    (Unknown Sequence) as place holder instead
    'ET(Unknown Sequence)'

    Furthermore, the MorseCode class has a method for checking the validity of
    the text:

    >>> m.find_invalid_characters('AB%&')
    '%, &'

    The method returns a string showing all invalid characters in the input
    text. In case no non-valid characters are in the text, False is returned.

    Finally, the MorseCode class has a method for checking if morse code
    contains only valid characters representing the morse code:

    >>> m.is_valid_morse_code('.--')
    ''
    >>> m.is_valid_morse_code('.-_')
    '_'

    Note that "is_valid_morse_code" does only check for the characters within
    the morse string, not if the given sequence is really existing! This is
    done only when calling "from_morse()".
    
    The warnings shown are generated by the logging module, which is used by
    the module. The logger is named "MorseCode", log level is set to "WARNING".
    
    And, finally: The text to translate into morse code can either be upper or
    lower letter. Internally, all letters are switched to upper-case letters
    anyway. Word and sentences translated from morse code to characters are
    always upper-case letters.

    '''

    CHAR_TO_MORSE = {
        'A': '.-',
        'B': '-. . . ',
        'C': '-.-. ',
        'D': '-..',
        'E': '.',
        'EA': '..-..',
        'F': '..-.',
        'G': '--.',
        'H': '....',
        'I': '..',
        'J': '.---',
        'K': '-.-',
        'L': '.-..',
        'M': '--',
        'N': '-.',
        'O': '---',
        'P': '.--.',
        'Q': '--.-',
        'R': '.-.',
        'S': '...',
        'T': '-',
        'U': '..-',
        'V': '...-',
        'W': '.--',
        'X': '-..-',
        'Y': '-.--',
        'Z': '--..',
        '1': '.----',
        '2': '..---',
        '3': '...--',
        '4': '....-',
        '5': '.....',
        '6': '-....',
        '7': '--...',
        '8': '--- ..',
        '9': '----.',
        '0': '-----',
        '.': '.-.-.-',
        ',': '--..--',
        ':': '---...',
        '?': '..--..',
        "'": '.----.',
        '-': '-....-',
        '/': '-..-.',
        '(': '-.--.',
        ')': '-.--.-',
        '"': '.-..-.',
        '=': '-...-',
        '+': '.-.-.',
        '@': '.--.-.',
    }

    MORSE_TO_CHAR = {
        '...---...': '(SOS)',
        '...-.': '(UNDERSTOOD)',
        '........': '(ERROR)',
        '-.-': '(INVITATION TO TRANSMIT)',
        '.-...': '(WAIT)',
        '...-.-': '(END OF WORK)',
        '-.-.-': '(START SIGNAL)',
        '-..-': 'x',  # morse code for multiplicator sign
        '..-..': 'E'  # morse code for "emphasized E"
    }

    # populate MORSE_TO_CHAR fully
    for k, v in CHAR_TO_MORSE.items():
        MORSE_TO_CHAR[v] = k
        
    # logging, used to give warnings when "strict_mode" of the MorseCode class
    # is set to False
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger('MorseCode')


    def __init__(self, strict_mode=True):
        '''args: strict_mode (optional, defaults to True)
        When creating an instance of the MorseCode class, the optional argument
        "strict_mode" can be passed, which is assigned to the class attribute
        "mode".

        The class has a number of attributes:

        * word_sep: holds the string containing the separator character
        separating the various words in the morse code. Defaults to "   "
        (=three blank spaces), as defined by the ITU recommendation.

        * char_sep: holds the string containing the separator character(s) to
        split the characters within a word in the morse code. Defaults to " "
        (a single blank space), as defined by the ITU recommendation.

        * strict_mode: Boolean value, defaults to True. "strict_mode" defines
        whether text containing non-valid characters respectively morse code
        defining non-valid sequences are anyway translated. When set to True,
        translation is aborted, raising an exception. When set to False,
        translation is done, replacing invalid characters / sequences with
        pre-defined place holders (see below).

        * missing_char_placeholder: string which is used to replace invalid
        characters in the text to translate text into morse code when
        strict_mode is set to False. Defaults to "?".

        * missing_morse_code_placeholder: string which is used to replace
        invalid morse code sequences in the morse code to translate into text
        when strict_mode is set to False. Defaults to "(Unknown Sequence) "

        The class has the following public functions:

        * to_morse(text): translates the text "text" into morse code

        * from_morse(morse_code): translates the morse code "morse_code" into
        text

        * find_invalid_characters(text): checks whether the text "text"
        contains only valid characters, which can be translated into morse code

        * is_valid_morse_code(morse_code): checks whether is morse code
        "morse_code" contains only valid morse_code sequences

        Furthermore, the class holds two global variables named CHAR_TO_MORSE
        and MORSE_TO_CHAR, both are dictionaries. CHAR_TO_MORSE contains the
        mapping of the characters to corresponding morse code sequences.
        MORSE_TO_CHAR contains the mapping of morse code sequences to
        characters. Please note that MORSE_TO_CHAR is mostly populated from
        CHAR_TO_MORSE when creating an instance of the Morse class.

        '''

        self.strict_mode = strict_mode
        self.char_sep = ' '
        self.word_sep = '   '
        self.missing_char_placeholder = '?'
        self.missing_morse_code_placeholder = '(Unknown Sequence)'

    def to_morse(self, text):
        '''args: text
        This function translates to given text "text" in a morse code sequence.
        Prior to translation, "to_morse" calls the function
        "find_invalid_characters()" to check the input text. In case
        "strict_mode" is set to True (the default), an exception is raised and
        nothing is translated. In case "strict_mode" is set to False, the text
        is translated, using the class attribute "missing_char_placeholder"
        for non-translatable characters.

        '''

        self._check_separators()
        text = text.upper()
        invalid_chars = self.find_invalid_characters(text)
        if invalid_chars:
            if self.strict_mode:
                raise MorseCodeError('Invalid input text',
                                     'Input text contains invalid characters: \
{0}'.format(invalid_chars))
            else:
                self.logger.warning('Given text contains an invalid characters\
 {0}. Will use {1} as placeholder in output'.format(invalid_chars,
                                            self.missing_char_placeholder))
        return self.word_sep.join(
                   self.char_sep.join(
                        self.CHAR_TO_MORSE.get(char,
                                               self.missing_char_placeholder)
                                               for char in word)
                       for word in text.split())

    def from_morse(self, morse_code):
        '''args: morse_code
        This function translates the given morse_code "morse_code" back to
        text. Prior to translation, the function "is_valid_morse_code" is
        called to check whether the morse code contains valid characters for
        code representation only.
        In case "strict_mode" is set to True (the default), an exception will
        be raised. In case it is set to False, the class attribute
        "missing_morse_code_placeholder" will be used in the translated text
        for non-translatable sequences of morse code.

        '''

        self._check_separators()
        #test on invalid characters in morse code
        if self.is_valid_morse_code(morse_code):
            raise MorseCodeError('Morse Code error',
                                 'Morse code contains invalid characters')
        get_char = self._char_from_morse_strict \
            if self.strict_mode \
            else self._char_from_morse_easy
        #decode morse code into characters
        return ' '.join(
                ''.join(map(get_char, word.split(self.char_sep)))
            for word in morse_code.split(self.word_sep))

    def is_valid_morse_code(self, morse_code):
        '''args: morse_code
        This function checks if the morse code "morse_code" contains valid
        characters only, namely the dot . , the minus sign - as well as the
        attributes "word_sep" and "char_sep".
        In case only valid characters are contained, an empty string is
        returned.
        In case an invalid character is contained, a string containing (the)
        invalid character(s) is returned.

        '''

        self._check_separators()
        return morse_code.replace(self.word_sep, '').\
                          replace(self.char_sep, '').\
                          replace('.', '').\
                          replace('-', '')

    def find_invalid_characters(self, text):
        '''args: text
        This function checks if the text "text", contains any characters,
        which can not be translated into morse code.
        In case all characters are valid, an empty string is returned.
        In case invalid characters are contained, a string containing all
        non-valid characters is returned.

        '''

        return ', '.join(set(text.upper())-set(self.CHAR_TO_MORSE)-set(' '))
    
    def _char_from_morse_strict(self, morsecode):
        '''args: morsecode
        Private auxiliary class which checks if the given morse code sequence
        "morsecode" for a character is available with in the MORSE_TO_CHAR
        dict. If so, the corresponding character is returned. If not, an
        exception is raised.

        '''

        try:
            return self.MORSE_TO_CHAR[morsecode]
        except KeyError:
            raise MorseCodeError('Illegal morse code sequence',
                                 'Morse code contains a non-valid code sequence')
                                 
    def _char_from_morse_easy(self, morsecode):
        '''args: morsecode
        Private auxiliary class which checks if the given morse code sequence
        "morsecode" for a character is available with in the MORSE_TO_CHAR
        dict. If so, the corresponding character is returned. If not, the
        placeholder as defined within the MorseCode class is returned.
        
        '''

        try:
            return self.MORSE_TO_CHAR[morsecode]
        except KeyError:
            self.logger.warning('Found illegal morse code sequence {0}. '
                'Will use {1} as place holder instead'.format(
                    morsecode, self.missing_morse_code_placeholder))
            return self.missing_morse_code_placeholder

    def _check_separators(self):
        '''Private auxiliary class, which tests if the attributes "char_sep"
        and "word_sep" do not contain the dot . or the minus sign -, as these
        characters exclusively represent the morse code.
        In case . or - are in the separators, a MorseCodeError will be raised.

        '''

        if set('.-') & set(self.char_sep):
            raise MorseCodeError('Forbidden value for attribute char_sep',
                                 'character separator cannot be . or -')
        if set('.-') & set(self.word_sep):
            raise MorseCodeError('Forbidden value for attribute word_sep',
                                 'character separator cannot be . or -')
