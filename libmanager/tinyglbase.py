#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins
#

import sys, os, csv, copy, pickle, gzip, functools, re
from operator import itemgetter
from .progress import progressbar
from . import logger

def qdeepcopy(anobject):
    return pickle.loads(pickle.dumps(anobject, -1))

ignorekeys = frozenset( # these are functional tags - so I should ignore them.
    ["dialect",
    "duplicates_key",
    "skiplines",
    "debug",
    "special",
    "skiptill",
    "force_tsv",
    "gtf_decorators",
    "endwith",
    "__description__",
    "commentlines",
    "keepifxin",
    '__column_must_be_used',
    '__ignore_empty_columns'
    ])

def glload(
    filename:str,
    name:str = False
    ):
    """
    **Purpose**
        Load a glbase binary file
        (Actually a Python pickle)

    **Arguments**
        filename (Required)
            the filename of the glbase binary file to load.

        name (Optional, default=False)
            Change the name of the loaded glb


    **Returns**
        The glbase object previously saved as a binary file
    """
    assert os.path.isfile(os.path.realpath(filename)), f"File '{filename}' not found"

    try:
        oh = open(os.path.realpath(filename), "rb")
        newl = pickle.load(oh)
        oh.close()
    except pickle.UnpicklingError:
        raise AssertionError(f'File "{filename}" bad binary file format')
    except FileNotFoundError:
        raise AssertionError(f'File "{filename}" changed whilst trying to read it')

    if name:
        newl.name = name

    return newl

class Genelist(): # gets a special uppercase for some dodgy code in map() I don't dare refactor.
    """
    **Purpose**
        This is a class container for any arrangement of heterogenous data.

        it is good for dealing with csv/tsv files with arbitrary columns - arranging
        them by keys and then allowing cross-matching and data extraction.
        genelist is the generic implementation. Other derived classes are available for
        e.g. peaklists, genome annotations and microarray (or expression) based data.

    **Arguments**
        name (Optional)
            Will default to the name of the file if a file is loaded,
            otherwise name will be set to "Generic List" by default.
            us the name argument to give it a custom nam,e

        filename (Optional)
            the name of a file to attempt to load.

        force_tsv (Optional)
            if you specify a filename to load then
            setting this argument to True will force the file to be treated
            as a tsv (tab-separated) rather than the default csv (comma
            separated).

        loadable_list (Optional, default=None)
            If you supply a list of dicts then glbase will attempt to build a genelist out of it.

        gzip (Optional, default=False)
            The input file is gzipped

        format (Required, or use format.sniffer to let glbase guess)
            Format specifiers are a mini language that can describe any valid TSV file.

            They should be a dictionary, in the form:

            {'column_name1': 1,
            'column_name2': 2}

            where the key of the dictionary will be the key name, and the value will be the
            column number.

            location data is handled a little differently, as the values may be split across
            several columns. In this case glbase is looking for a special 'location' tag with a specific format.

            Suppose the chromosome was in column 3, the left coordinate was in column 4 and right in column 5,
            to add a genome location to our format, we would add a 'loc' key, containing this info:

            {'column_name1': 1,
            'column_name2': 2,
            "loc": "location(chr=column[3], left=column[3], right=column[5])"}

            To help deal with unusal syntax in TSV or CSV files there are a list of reserved
            key names that perform some special function:


            duplicates_key
                ?

            skiplines
                do not start loading from the file until you get to line number 'skiplines': value

            debug
                print out a debug load of the file, stopping at 'debug': X line numbers

            special
                ?

            skiptill
                do not start loading the file until you see a line starting with 'skiptill' and
                start loading the file from the next line.

            force_tsv
                forse the loader to assume the file is a TSV, rather than the defaul CSV

            gtf_decorators
                This specifies the column number that contains GTF decorators, which will be split into key:value and added to the genelist

            endwith
                Stop loading the file if you see a line that contains the value specified in endwith

            __description__
                ?

            commentlines
                Ignore lines that start with this string (e.g. 'commentlines': '#' is quite commont)

            keepifxin
                ?

            __column_must_be_used
                ?

            __ignore_empty_columns
                Ignore a column if there is no value in the column, this is for when TSVs/CSVs
                are incomplete and are missing columns on specific lines, but you don't want to have
                to sanitise the TSV/CSV, and would prefer to just fill in the blank with nothing.

            As an example, here is the full format for a complete BED file:

            {"loc": "location(chr=column[0], left=column[1], right=column[2])",
            "name": 3, "score": 4, "strand": 5, "thickStart": 6, "thickEnd": 7,
            "itemRgb": 8, "blockCount": 9, "blockSizes": 10, "blockStarts": 11,
            "force_tsv": True, "skiplines": -1, "commentlines": "#"}

            see also glbase/format.py for a list of already defined format specifiers
            that you can call using:

            gl = genelist(..., format=format.full_bed)

    """
    def __init__(self,
        filename=None,
        loadable_list=None,
        gzip=False,
        format:dict = None,
        force_tsv:bool = False,
        log=None,
        **kargs):

        assert format, 'You must provide a format'
        assert log, 'tinyglbase requires an external log'

        self.log = log
        self.linearData = []
        self.debug = False
        self.name = "Generic List"
        self.metadata = {} # container for various metadata's to extract figures from.
        self.__deathline = None # Error reporting in load_CSV()
        self.__deathindx = None

        if force_tsv:
            format["force_tsv"] = True

        if filename:
            self.load(filename=filename, format=format, gzip=gzip)
            self.log.info(f"genelist: loaded '{filename}' found {len(self.linearData):,} items")

        elif loadable_list:
            self.load_list(loadable_list)

        if "name" in kargs: # Here so it overrides anything above.
            self.name = kargs["name"]

    def load(self, filename=None, format=None, gzip=False, **kargs):
        """
        **Purpose**

        load a file into the genelist. load will attempt to load the file
        based on the filename, unless a format is specified.

        **Arguments**

        filename
            absolute filename (including path) to the actual file.
            can include path short cuts (e.g. "./", "../" etc)

        format (Optional, default = "sniffer" (ie. guess))
            format specifer, see format.py and the
            documentation on how to write a valid format specifier

        **Result**

        fills the genelist with the data from the file as specified by
        the format specifier.
        """
        assert filename, "No filename specified"
        assert os.path.isfile(os.path.realpath(filename)), f"File {filename} not found"

        self.path = os.path.split(os.path.realpath(filename))[0]
        self.filename = os.path.split(os.path.realpath(filename))[1]
        self.fullfilename = filename
        if self.filename.find(".") != -1:
            self.name = "".join(self.filename.split(".")[:-1])
        else:
            self.name = self.filename

        csv_headers = frozenset(["csv", "xls", "tsv", "txt", "bed"])
        if filename.split(".")[-1].lower() in csv_headers: # check the last one for a csv-like header
            self.loadCSV(filename=filename, format=format, gzip=gzip, **kargs)
        else:
            self.loadCSV(filename=filename, format=format, gzip=gzip, **kargs)

        return True  # must have made it to one - if it fails it should trigger

    def loadCSV(self, filename=None, format=None, **kargs):
        """
        **Purpose**

        load a CSV file into the genelist

        **Arguments**

        filename
            absolute filename (including path) to the actual file.
            can include path short cuts (e.g. "./", "../" etc)

        format (Optional, default = "sniffer" (ie. guess))
            format specifer, see format.py and helpers.py and the
            documentation on how to write a valid format specifier

        force_tsv (Optional, default=False)
            if you don't send a format specifier, but want to force the
            genelist to load as a tsv, you can set this flag to True.
            NOTE: If you send a format argument then this argument is ignored!

            As another option, you can use the sniffer_tsv format specifier

        name (Optional, Default = based on the filename)
            name of the genelist, used intermittently as labels in
            figures and the like.

        **Result**

        fills the genelist with the CSV table.
        """
        assert os.path.isfile(os.path.realpath(filename)), f"File {filename} not found"

        self.name = '.'.join(os.path.split(filename)[1].split(".")[:-1]) # Put here otherwise realpath will force name from the symbolic link, not from the actual link!
        self.path = os.path.split(os.path.realpath(filename))[0]
        self.filename = os.path.split(os.path.realpath(filename))[1]
        self.fullfilename = filename

        if "debug" in format and format["debug"]:
            print("--------")
            print("DEBUG load:")
            self._loadCSV(filename=self.fullfilename, format=format, **kargs)
        else:
            try:
                self._loadCSV(filename=self.fullfilename, format=format, **kargs)
            except Exception:
                raise AssertionError(f"'{self.fullfilename}' appears mangled, the file does not fit the format specifier")

    def _loadCSV(self, **kargs):
        """
        (Internal)

        Actual loadCSV()

        This is mainly so the try/except block above doesn't get completely out of control
        and allows debug code.
        """
        assert "filename" in kargs, "No filename specified"
        assert "format" in kargs, "_loadCSV requres a format specifier"
        assert os.path.isfile(kargs["filename"]), f"{kargs['filename']} file not found"

        filename = kargs["filename"]
        format = kargs["format"]

        temp_data = []
        if 'gzip' in kargs and kargs['gzip']:
            oh = gzip.open(filename, "rt")
        else:
            oh = open(filename, "rt")

        if "force_tsv" in kargs and kargs["force_tsv"]: # force_tsv takes priority
            reader = csv.reader(oh, dialect=csv.excel_tab)
        elif "force_tsv" in format and format["force_tsv"]:
            reader = csv.reader(oh, dialect=csv.excel_tab)
        elif "dialect" in format and format["dialect"]:
            reader = csv.reader(oh, dialect=format["dialect"])
        else:
            reader = csv.reader(oh)

        if "skiplines" in format:
            skiplines = format["skiplines"]
        else:
            skiplines = 0 # skip any header row by default.

        if "skiptill" in format and format["skiptill"]:
            skiptill = format["skiptill"]
        else:
            skiptill = "Done" # This is done as truth testing fails as format["skiptill"] != None

        debug_line = 0

        # sanitise format[key] data for security.
        newf = {}
        for k in format:
            if isinstance(format[k], dict) and "code" in format[k]:
                newf[k] = {"code": format[k]["code"].replace("__", "").replace(" sys,", "")} # Some security suggestions:, {"__builtins__":None, column, location}, {})
            elif isinstance(format[k], str) and "location" in format[k]:
                newf[k] = format[k].replace("__", "").replace(" sys,", "")
            else:
                newf[k] = format[k]
        format = newf

        for index, column in enumerate(reader):
            # This is cryptically called column, when it is actually row.
            self.__deathline = column # For debugging purposes
            self.__deathindx = index

            if not column: # if row is completely empty omit.
                continue

            if index <= skiplines or skiptill != "Done":
                if column and True in [skiptill in item for item in column]:
                    skiptill = "Done"
                continue

            if "__column_must_be_used" in format and format["__column_must_be_used"]:
                if not column[format["__column_must_be_used"]]:
                    continue # Omit data when this particular column is blank

            if "endwith" in format and format["endwith"]:
                if True in [format["endwith"] in item for item in column]:
                    break

            if "commentlines" in format and format["commentlines"]:
                if column[0][0] == format["commentlines"]:
                    continue

            # passed all the tests
            temp_data.append(self._processKey(format, column))

            #print(temp_data[-1]) # tells you what got loaded onto the list.
        oh.close()

        self.linearData = temp_data

        self._optimiseData()
        return True

    def _processKey(self, format, column):
        """
        (Internal)
        the inner part of _loadCSV() to determine what to do with the key.
        Better in here too for security.
        """

        d = {}
        for key in format:
            if key not in ignorekeys: # ignore these tags
                #if not key in d:
                #    d[key] = {}
                if '__ignore_empty_columns' in format and format['__ignore_empty_columns']:
                    # check the column exists, if not, pad in an empty value
                    try:
                        column[format[key]]
                    except IndexError:
                        d[key] = '' # Better than None for downstream compatability
                        continue

                if isinstance(format[key], dict) and "code" in format[key]:
                    # a code block insertion goes here - any valid lib and one line python code fragment
                    # store it as a dict with the key "code"
                    d[key] = eval(format[key]["code"])
                elif isinstance(format[key], str) and "location" in format[key]:
                    # locations are very common, add support for them out of the box:
                    d[key] = eval(format[key])
                else:
                    d[key] = self._guessDataType(column[format[key]])

        return d

    def __iter__(self):
        """
        (Override)
        make the genelist behave like a normal iterator (list)
        """
        return self.linearData.__iter__()

    def _guessDataType(self, value):
        """
        (Internal)

        Take a guess at the most reasonable datatype to store value as.
        returns the resulting data type based on a list of logical cooercions
        (explain as I fail each cooercion).
        Used internally in _loadCSV()
        I expect this will get larger and larger with new datatypes, so it's here as
        as a separate function.

        Datatype coercion preference:
        float > list > int > location > string
        """

        try: # see if the element is a float()
            if "." in value: # if no decimal point, prefer to save as a int.
                return float(value)
            elif 'e' in value: # See if we can coocere from scientific notation
                return float(value)
            else:
                raise ValueError
        except ValueError:
            try:
                # Potential error here if it is a list of strings?
                if '[' in value and ']' in value and ',' in value and '.' in value: # Probably a Python list of floats
                    return [float(i) for i in value.strip(']').strip('[').split(',')]
                elif '[' in value and ']' in value and ',' in value: # Probably a Python list of ints
                    return [int(i) for i in value.strip(']').strip('[').split(',')]
                else:
                    raise ValueError
            except ValueError:
                try: # see if it's actually an int?
                    return int(value)
                except ValueError:
                    # this is not working, just store it as a string
                    return str(value).strip()

        return "" # return an empty datatype.
        # I think it is possible to get here. If the exception at int() or float() returns something other than a
        # ValueError (Unlikely, Impossible?)

    def _optimiseData(self):
        """
        (Internal)
        Call me after modifying the data to bin and build the internal tables.
        """
        if not self.linearData: # list is empty, not possible to optimise anything...
            return False

        keys = self.keys()

        self.qkeyfind = {}
        for index, item in enumerate(self.linearData):
            for key in item:
                if key not in self.qkeyfind:
                    self.qkeyfind[key] = {}

                try:
                    if item[key] not in self.qkeyfind[key]:
                        self.qkeyfind[key][item[key]] = []
                    self.qkeyfind[key][item[key]].append(index)

                except TypeError:
                    pass

        return True

    def _findDataByKeyLazy(self, key, value):    # override????? surely find?
        """
        (Internal)

        find the first matching entry of key value pair

        This version is lazy, so I take the min() and return that item
        """
        if key in self.qkeyfind and value in self.qkeyfind[key]:
            return self.linearData[min(self.qkeyfind[key][value])]
        return None # not found;

    def _findDataByKeyGreedy(self, key, value):    # override????? surely finditer?
        """
        finds all - returns a list
        """
        ret = []
        item_indeces = None
        if key in self.qkeyfind and value in self.qkeyfind[key]:
            item_indeces = self.qkeyfind[key][value]

        if item_indeces:
            return([self.linearData[i] for i in item_indeces])
        return None

    def keys(self):
        """
        return a list of all the valid keys for this geneList
        """
        if not self.linearData: return [] # Match python dict default
        return [key for key in self.linearData[0]] # Not exhaustive

    def get(self, key, value, mode="greedy"):
        """
        **Purpose**
            get all items that match "value" in "key"
            you can also use find() to get the first matching item, or set mode to "lazy" to
            achieve the same effect

            get will always return a genelist, even if there is only 1 item

        **Arguments**
            key
                the key of the genelist to search in

            value
                the value to look for in key

            mode (Optional, default="greedy")
                the mode of search. "greedy" searches will
                find all examples, "lazy" searches will only find
                the first in the list. Most of the time you mean
                "greedy"

        **Returns**
            A new genelist or None
        """
        assert key in self.keys(), f'"{key}" key not found in this list'

        if mode == "greedy":
            r = self._findDataByKeyGreedy(key, value)
        elif mode == "lazy":
            r = self._findDataByKeyLazy(key, value) # lazy just returns a single dict
            if r:
                r = [r]
        else:
            raise AssertionError(f"mode '{mode}' for get() is not known")

        # The internal methods return vanilla lists for compatability with er... internal stuffs
        # repackage to a new gl.
        if r:
            newl = self.shallowcopy() # shallowcopy for once as we will load in our own list.
            newl.load_list(r)
            return newl
        return None

    def _findAllLabelsByKey(self, key):
        """
        (Internal)
        Returns a 1D list of all the values under Key.
        Most useful for things like geneList["Symbol"]
        geneList["entrez"]
        """
        return [x[key] for x in self.linearData]

    def _findByLabel(self, key, value):
        """
        (Internal)
        key is the key to search with
        toFind is some sort value to compare

        There is a subtle problem here if the user tries to find a list or other non-hashable
        object. But then It would be kind of wierd to do that...

        (This is used in at least draw._heatmap_and_plot())

        This version is deprectaed. The official internal methods are:
        _findDataByKeyLazy|Greedy()
        """
        return self._findDataByKeyLazy(key, value) # not found;

    def save(self, filename=None):
        """
        **Purpose**

            Save the genelist as a binary representation.
            This is guaranteed to be available for all geneList representations, with
            the only exception being the delayedlists. As that wouldn't
            make any sense as delayedlists are not copied into memory.

            You can use this method to cache the file. It's particularly useful for large files
            that get processed once but are then used a lot.

            loading the list back into memory is relatively quick.

            list = glload("path/to/filename.glb")

            I generally used extension is glb. Although you can use
            whatever you like.

        **Arguments**

            filename
                filename (and path, if you like) to save the file to

        **Result**

            returns None
            Saves a binary representation of the geneList

        """
        assert filename, "no filename specified"

        with open(filename, "wb") as oh:
            pickle.dump(self, oh, -1)
        self.log.info(f"Saved binary version: '{filename}'")

    def saveTSV(self, filename=None, **kargs):
        """
        **Purpose**
            save the geneList or similar object as a tsv
            Note: This is not always available.
            As the geneList becomes more complex it loses the ability to be
            expressed simply as a csv-file. In those cases you must use
            the save() method to save a binary representation.

            saveTSV is *generally* 'consistent' if you can succesfully save
            as a tsv then you can reload the same list as that particular
            type. Be careful though. Behaviour like this will work, but give
            unexpected results::

                rnaseq.saveTSV(filename="file.csv")
                anewlist = genelist(filename="file.csv")
                anewlist # this list is now a genelist and not an expression.
                         # You must load as an expression:
                rnaseq = expression(filename="file.csv")

        **Arguments**
            filename
                filename to save, including the full path.

            key_order (Optional, default=None)
                send a list, specifying the order you'd like to write the keys
                by default saveTSV() will write to the file in an essentially
                random order. But if you want to specify the order then
                send a list of key names and it will save them in that order.

                Also, you need only specify the left side of the column.
                Any unspecified columns will be appended to the right
                hand side in a random order.

                Note that saveTSV() always saves all columns of data.

            tsv (True|False)
                save as a tsv file see also saveCSV()

            no_header (Optional, default=False)
                Don't write the first line header for this file. Usually it's the list
                of keys, then the second line will be the data. If no_header is set to False
                then the first line of the file will begin with the data.

            gzip (Optional, default=False)
                save the TSV as a gzipped file. (Don't forget to add the .gz suffix!)

        **Result**
            returns None.
            saves a TSV representation of the genelist.
        """
        self.saveCSV(filename, tsv=True, **kargs)

    def saveCSV(self, filename=None, no_header=False, **kargs):
        """
        **Purpose**

            save the geneList or similar object as a csv
            Note: This is not always available.
            As the geneList becomes more complex it loses the ability to be
            expressed simply as a csv-file. In those cases you must use
            the save() method to save a binary representation.

            saveCSV is guaranted to be 'consistent' if you can succesfully save
            as a csv then you can reload the same list as that particular
            type. Be careful though. Behaviour like this will work fine::

                microarray.saveCSV(filename="file.csv")
                anewlist = genelist(filename="file.csv")
                anewlist # this list is now a genelist and not a microarray.
                         # You must load as a microarry:
                amicroarry = microarray(filename="file.csv")

            saving to a csv will will blank the history, and any other meta-
            data generated about the list.

        **Arguments**

            filename
                filename to save, including the full path.

            key_order (List)
                send a list, specifying the order you'd like to write the keys
                by default saveTSV() will write to the file in an essentially
                random order. But if you want to specify the order then
                send a list of key names and it will save them in that order.

                Also, you need only specify the left side of the column.
                Any unspecified columns will be appended to the right
                hand side in a random order.

                Note that saveTSV() always saves all columns of data.

            tsv (True|False)
                save as a tsv file see also saveTSV()

            no_header (Optional, default=False)
                Don't write the first line header for this file. Usually it's the list
                of keys, then the second line will be the data. If no_header is set to False
                then the first line of the file will begin with the data.

        **Result**
            returns None.
            saves a CSV representation of the geneList.
        """
        assert filename, "No filename specified"

        if 'gzip' in kargs and kargs['gzip']:
            oh = gzip.open(filename, "wt")
        else:
            oh = open(filename, "wt")

        if not self.linearData: # data is empty, fail graciously.
            self.log.error(f"csv file '{filename}' is empty, no file written")
            oh.close()
            return None

        if "tsv" in kargs and kargs["tsv"]:
            writer = csv.writer(oh, dialect=csv.excel_tab)
        else:
            writer = csv.writer(oh)

        # work out key order and the like:
        write_keys = []
        if "key_order" in kargs:
            write_keys = kargs["key_order"]
            # now add in any missing keys to the right side of the list:
            for item in list(self.keys()):
                if item not in write_keys:
                    write_keys.append(item)
        else:
            # just selece them all:
            write_keys = list(self.keys())

        if not no_header:
            writer.writerow(write_keys) # write the header row.

        for data in self.linearData:
            line = []
            for key in write_keys: # this preserves the order of the dict.
                if key in data:
                    line.append(data[key])
                else:
                    line.append("") # a blank key, fail gracefully.
            writer.writerow(line)
        oh.close()
        self.log.info(f"Saved '{filename}'")
        return None

    def sort(self, key=None, reverse=False):
        """
        Sort the data into a particular order based on key.
        This sorts the list in-place in the same style as Python.
        ie.

        ret = list.sort() - is True and not the sorted list

        list.sort() - now list contains the sorted list

        **Arguments**

        key
            the key to use to sort by.
            must be some sort of sortable item

        reverse (Optional, default=False)
            By default the list is sorted smallest to largest.
            reverse = True sorts largest to smallest.

        **Result**

        returns True if it completes.
        sorts the list IN PLACE.
        """
        assert key, "No such key '%s'" % key
        assert key in self.linearData[0], "Data does not have key '%s'" % key

        self.linearData = sorted(self.linearData, key=itemgetter(key))
        if reverse:
            self.linearData.reverse()
        self._optimiseData()
        return True

    def reverse(self):
        """
        reverse the order of the list, in place.

        **Arguments**

        None

        **Result**

        returns True if okay or false.
        """
        self.linearData.reverse()
        self._optimiseData() # just in case.
        return True

    #------------------------------ Overrides --------------------------

    def __contains__(self, item):
        """
        (Override)
        There may be some obscure failures with this item - to do with
        returned lists. IF you send a [ {} ... {} ] like object
        derived from a genelist then it will fail (but then it should?)
        but if you use slices it should be okay:
        a = genelist[0] # returns a single dict
        a = genelist[0:10] # returns a new genelist
        """
        if not self.linearData:
            return False

        return item in self.linearData[0]

    def __repr__(self):
        """
        (Override)
        report the underlying representation
        """
        return "glbase.genelist"

    def __str__(self):
        """
        (Override)
        give a sensible print out.
        """
        if len(self.linearData) > 3:
            out = []
            # welcome to perl
            for index in range(3):
                out.append("%s: %s" % (index, ", ".join(["%s: %s" % (key, self.linearData[index][key]) for key in self.linearData[index]])))
            out = "%s\n... truncated, showing %s/%s" % ("\n".join(out), 3, len(self.linearData))
            out = "%s\n%s" % (out, "%s: %s" % (len(self.linearData), ", ".join(["%s: %s" % (key, self.linearData[-1][key]) for key in self.linearData[-1]])))

        elif len(self.linearData) == 0:
            out = "This list is empty"

        else: # just print first entry.
            out = []
            for index in range(len(self.linearData)):
                out.append("%s: %s" % (index, ", ".join(["%s: %s" % (key, self.linearData[index][key]) for key in self.linearData[index]])))
            out = "%s\nShowing %s/%s" % ("\n".join(out), len(self.linearData), len(self.linearData))

        return out

    def __getitem__(self, index):
        """
        (Override)
        confers a = geneList[0] behaviour

        This is a very slow way to access the data, and may be a little inconsistent in the things
        it returns.

        NOTE:
        a = genelist[0] # returns a single dict
        a = genelist[0:10] # returns a new 10 item normal python list.
        a = genelist["name"] returns a python list containing a vertical slice of all of the "name" keys

        """
        newl = False
        if isinstance(index, int):
            # this should return a single dictionary.
            return self.linearData[index]
        elif isinstance(index, str):
            # returns all labels with that item.
            return self._findAllLabelsByKey(index)
        elif isinstance(index, slice):
            # returns a new genelist corresponding to the slice.
            newl = self.shallowcopy()
            newl.linearData = qdeepcopy(self.linearData[index]) # separate the data so it can be modified.
            newl._optimiseData()
        return newl # deep copy the slice.

    def __len__(self):
        """
        (Override)
        get the length of the list
        """
        return len(self.linearData)

    def __shallowcopy__(self):
        raise Exception("__shallowcopy__() is NOT supposrted for genelists, use gl.deepcopy() or gl.shallowcopy()")

    def __deepcopy__(self, fake_arg):
        raise Exception("__deepcopy__() is NOT supported for genelists, use gl.deepcopy() or gl.shallowcopy()")

    def deepcopy(self):
        """
        Confer copy to mean a deepcopy as opposed to a shallowcopy.

        This is required as genelists are compound lists.
        """
        return pickle.loads(pickle.dumps(self, -1)) # This is 2-3x faster and presumably uses less memory

    def shallowcopy(self):
        """
        (New)

        Some weird behaviour here, I know, this is so I can still get access to
        the shallow copy mechanism even though 90% of the operations are copies.
        """
        return copy.copy(self) # But doesnt this just call __copy__() anyway?

    def getColumns(self, return_keys=None):
        """
        **Purpose**
            return a new genelist only containing the columns specified in return _keys (a list)
        """
        assert isinstance(return_keys, list), "return_keys must have a list"

        newl = self.shallowcopy()
        newl.linearData = []

        for item in self.linearData:
            newl.linearData.append(dict((k, item[k]) for k in return_keys)) # hack for lack of dict comprehension
            # assumes all keys are in the dict

        newl._optimiseData()
        self.log.info("getColumns: got only the columns: %s" % ", ".join(return_keys))
        return newl

    def getRowsByKey(self, key=None, values=None, use_re=True, case_sensitive=True,
        silent=False, **kargs):
        """
        **Purpose**
            extract all rows from a genelist for which the values in key are in the
            list_of_items

            You can send regular expressions and they will be
            interpreted correctly.

            NOTE that getRowsByKey() is a SLOW look up.

            If you need speed use get(), which is basically a free lookup of the list
            (even for greedy searches) but does not support regular expressions

        **Arguments**
            values (Required)
                a list of items to collect

            key (Optional, default=None)
                the key to search in.
                If None, all keys are searched.

            case_sensitive (Optional, default=True)
                Set to True to make the search case sensitive. Only works if use_re=True

            use_re (Optional, default=True)
                Unset this if you want exact matches or are getting unexpected behaviour
                from the regular expressions.

        **Returns**
            A new genelist containing only those items.
        """
        assert values, "getRowsByKey: 'values' argument cannot be None"
        if not case_sensitive:
            assert use_re, 'use_re must be True if case_sensitive is False'

        if not isinstance(values, list):
            values = [values]

        # This should be made super fast with qkeyfind

        newl = self.shallowcopy()
        newl.linearData = []

        if use_re: # re-ise the items.
            if case_sensitive:
                list_of_items = [re.compile(i) for i in values]
            else:
                list_of_items = [re.compile(i, re.IGNORECASE) for i in values]

            if not key: # split here for clarity.
                for item in self.linearData:
                    for k in item: # no key specified, check all.
                        for r in list_of_items:
                            if r.search(str(item[k])):
                                newl.linearData.append(qdeepcopy(item))
            else:
                for item in self.linearData:
                    for r in list_of_items:
                        if r.search(str(item[key])): # sometimes gene names accidentally get stored as numbers
                            newl.linearData.append(qdeepcopy(item))
        else: # no re.
            if not key: # split here for clarity.
                for item in self.linearData:
                    for k in item: # no key specified, check all.
                        for r in values:
                            if r == item[k]:
                                newl.linearData.append(item.copy())
            else:
                for item in self.linearData:
                    for r in values:
                        if r == item[key]:
                            newl.linearData.append(item.copy())

        if newl:
            newl._optimiseData()
        else:
            if not silent: self.log.info("getRowsByKey: Found 0 items")
            return None

        if not silent: self.log.info(f"getRowsByKey: Found {len(newl)} items")

        return newl

    def filter_by_in(self, key=None, value=None, remove=True, **kargs):
        """
        **Purpose**
            filter the genelist, and

            if remove=True, then delete all matching entries:
            if <value> in <key> then remove

            if remove=False, then do the opposite and only keep entries that match
            if <value> in <key> then keep

        **Arguments**
            key (Required)
                key to search for '<value>' in

            value (Required)
                value to test in key.

            remove (Optional, default=True)
                if remove=True, then remove matching entries
                if remove=False, keep all entries that match

        **Returns**
            New genelist with the entries removed

        """
        assert key, 'You must specify a key'
        assert value, 'You must specify a value'
        assert key in self.keys(), f'{key} key not found in this genelist'
        assert remove in (True, False), 'You must specify True/False for the remove argument'

        newgl = self.deepcopy()

        if remove:
            newl = [item for item in newgl.linearData if value not in item[key]]
            self.log.info('filter_by_in: Removed {} entries'.format(len(self) - len(newl)))
        else:
            newl = [item for item in newgl.linearData if value in item[key]]
            self.log.info('filter_by_in: Kept {} matching entries'.format(len(self) - len(newl)))

        newgl.linearData = newl
        newgl._optimiseData()
        return newgl

    def map(self, genelist=None, peaklist=None, microarray=None, genome=None, key=None,
        greedy=True, logic="and", silent=False, **kargs):
        """
        **Purpose**
            map() merges two genelist-like objects and outputs a new genelist.

            It matches, by the key, each item that overlap in the two genelist and
            returns a new genelist only containing the matching items between the two lists.

            The new genelist will inherit from 'the right', for
            example if you have a expression-object you should perform the map in this
            order::

                result = gene_list.map(genelist=expn, key="refseq") # expn is an expresion object

            'result' will now be a expression object with all the appropriate
            methods.

            If however, you did this by mistake::

                result = expn.map(genelist=gene_list, key="refseq") # expn is an expression object

            It will still work fine, but now, trying::

                result.heatmap(filename="foo.png")

            will fail, because the result is a vanilla genelist rather than
            an expression-object as you might intend.

            Also note, this method is 'greedy' by default and and will take all matching
            entries it finds. This can be changed by setting greedy=False.

        **Arguments**
            genelist
                some sort of genelist-like object,
                examples inglude genelist, expression, genome, etc

            key
                a key in common between the two lists you can use to map
                them against each other.

            image_filename (Optional)
                save a venn diagram

            venn_proportional (Optional)
                enable experimental proportional venn diagrams.

                Note that for a proper venn, both lists should be unique for
                the key you are using to match. glbase does not check that this is
                the case. This can be useful to estimate the Venn overlap so glbase remains
                silent for non-unique lists, but can occasionally give bizarre results,
                such as negative numbers in a particular condition.

            title (Optional, default = None)
                title for the venn diagram.

            greedy (Optional, default=True)
                set to True to collect all matching entries, including duplicates. (The default
                behaviour)
                If set to False then the search finds the first matching entry only

            logic (Optional, default="and")
                a logic operator to apply to the map
                Accepted operators are:

                "and" = only keep the item if it appears in both lists
                "notright" = for each item in the right hand list, only keep it if it is NOT in the left hand list

                Be aware of the strange syntax of 'notright'. This tests the item in the right list
                and only keeps it if it is NOT in the left list.

        **Result**
            returns a new genelist-like object containing the overlapping
            objects, inheriting methods from the
            right hand side of the function.

        """
        assert logic in ("and", "notright"), "logic '%s' not supported" % logic

        if repr(genelist) == "glbase.delayedlist": # delayedlists will fail an assertion
            gene_list = genelist
        else:
            assert genome or genelist or peaklist or microarray, "map: No valid genelist specified"

        if genelist:
            gene_list = genelist
        if peaklist:
            gene_list = peaklist
        if microarray:
            gene_list = microarray
        if genome:
            gene_list = genome

        __warning_assymetric_errs = False

        assert key, "Must specify a 'key' to map the two lists"
        #assert key in gene_list.linearData[0], "'%s' key not found in provided genelist '%s'" % (key, self.name)
        #assert key in self.linearData[0], "'%s' key not found in self '%s'" % (key, self.name)
        map_key = key

        p = progressbar(len(gene_list)) # leave as len() for compatability with delayedlists
        # speed up with a triangular search?
        newl = gene_list.shallowcopy()
        if repr(genelist) == "glbase.delayedlist": # Special exception for delayedlists, need to convert to vanilla genelist:
            newl = Genelist()
            newl.name = gene_list.name

        newl.linearData = []
        for index, item in enumerate(gene_list.linearData):
            if greedy:
                results = self._findDataByKeyGreedy(map_key, item[map_key])
            else:
                results = self._findDataByKeyLazy(map_key, item[map_key])
                if results:
                    results = [results] # coerce to a single member list to simplify code below

            if results:
                if logic == "and":
                    for r in results:
                        new_entry = qdeepcopy(r) # inherit from the right
                        new_entry.update(item) # Key items inherit from the right hand side
                        newl.linearData.append(new_entry)
            elif logic == "notright":
                newl.linearData.append(qdeepcopy(item)) # only inherit from the right, can't inheret from the left, as no matching map

            p.update(index)

        if not silent:
            if logic == "notright":
                self.log.info("map: '%s' vs '%s', using '%s' via '%s', kept: %s items" % (self.name, gene_list.name, map_key, logic, len(newl)))
            else:
                self.log.info("map: '%s' vs '%s', using '%s', found: %s items" % (self.name, gene_list.name, map_key, len(newl)))

        if len(newl.linearData):
            newl._optimiseData()
            return newl
        return None

    def removeDuplicates(self, key=None):
        """
        **Purpose**
            remove the duplicates in the list and returns a new list;
            keeps the first example it finds

            This will only delete duplicates within the 'key'. For example,
            these three entries in a genelist:

            1: name: Stat3, score: 20, splicing: canonical
            2: name: Stat3, score: 30, splicing: alternate
            3: name: Nanog, score: 40, splicing: alternate

            gl = gl.removeDuplicates("name")

            will give:

            1: name: Stat3, score: 20, splicing: canonical
            3: name: Nanog, score: 40, splicing: alternate

            whilst

            gl = gl.removeDuplicates("splicing")

            will result in:

            1: name: Stat3, score: 20, splicing: canonical
            2: name: Stat3, score: 30, splicing: alternate

        **Arguments**
            key
                The key in which to make search for duplicates.

                Note that key can also be a list if you want to use 2 or more keys

        **Returns**
            The new list with the duplicates removed.
        """
        assert key, "No key(s) specified"

        if isinstance(key, list):
            for k in key:
                assert k in list(self.keys()), "the key '{}' was not found in this genelist".format(key)

            # Multiple keys path:
            # make a key, index dict:
            newl = self.deepcopy()
            new_data_to_load = []

            sorter = {}
            for idx, item in enumerate(newl.linearData):
                thisK = '-'.join([str(item[k]) for k in key])
                if thisK not in sorter:
                    sorter[thisK] = []
                sorter[thisK].append(idx) # always in order, lowest to highest.

            # Now just go through and pick the 0th entry;
            for k in sorter:
                new_data_to_load.append(newl.linearData[sorter[k][0]])

            newl.linearData = new_data_to_load
            newl._optimiseData()

            self.log.info("removeDuplicates: {} duplicates, list now {} items long".format(len(self)-len(newl), len(newl)))
            return newl

        assert key in list(self.keys()), f"the key '{key}' was not found in this genelist"

        newl = self.shallowcopy()
        newl.linearData = []
        count = 0

        for item in self.qkeyfind[key]:
            newl.linearData.append(self.linearData[min(self.qkeyfind[key][item])]) # grab first
            # Will only apply a single item (the earliest) even if there
            # IS only one of these items.

        newl._optimiseData()

        self.log.info("removeDuplicates: {} duplicates, list now {} items long".format(len(self) - len(newl), len(newl)))
        return newl

    def removeExactDuplicates(self):
        """
        **Purpose**
            removes exact duplicates where all of the keys match. Keeping the first
            found copy

        **Returns**
            The new list with the duplicates removed.
        """
        newl = self.shallowcopy()
        newl.linearData = []
        count = 0

        # TODO: Could be done with: list(map(dict, frozenset(frozenset(i.items()) for i in marked_for_deletion)))
        # Lazy at the moment, this function is very rarely used. Better to speed up *ByKey()
        unq = set()
        kord = list(self.linearData[0].keys())# fix the key order

        for item in self.linearData:
            valstr = "".join(str(item[k]) for k in kord)
            if valstr not in unq:
                unq.add(valstr)
                newl.linearData.append(item) # add first item found

        newl._optimiseData()

        self.log.info("removeExactDuplicates: %s exact duplicates" % (len(self) - len(newl)))
        return newl

    def load_list(self, list_to_load, name=False):
        """
        **Purpose**
            You've generated your own [{ ... }, { ...}] like list
            (A list of dicts) and you want to either reload it into
            a genelist-like object or load it into an empty genelist.
            This is the method to do that officially.

            This method should be used with great care. Some sanity
            checking is done. But not very much.

        **Arguments**
            list_to_load
                must be a list of dicts.

            name
                Allows you to change the name of the list. By default it will keep
                the previous name.

        **Returns**
            self
        """
        try:
            list_to_load[0]
            i = list_to_load.__iter__()
        except TypeError:
            raise AssertionError("Type Error, the list appears not to be actually a list")

        try:
            item = list_to_load[0]
            i = [item[k] for k in item]
        except Exception:
            raise AssertionError("Type Error, the list of items appears not to contain a dictionary item")

        self.linearData = qdeepcopy(list_to_load)

        if name: # Overwrite name if set
            self.name = name

        self._optimiseData()
        return self

    def find(self, value):
        """
        **Purpose**
            find value in any key in the genelist.
            Note that find is lazy and returns only the first matching item it finds.
            Use map() for more accurate mapping, or get to collect all

        **Arguments**
            value
                find this 'value' anywhere in the genelist (can be in any key). Can also be any value, number
                string etc.

        **Returns**
            either the first item it finds or False
        """
        for i in self:
            for k in i:
                if i[k] == value:
                    return i

        return False

    def renameKey(self, old_key_name, new_key_name, keep_old_key=False, replace_existing_key=False):
        """
        **Purpose**
            rename a key with a new name

        **Arguments**
            old_key_name, new_key_name
                the old and new key names

            keep_old_key (Optional, default = False)
                set to True if you want to keep the old key name and value

            replace_existing_key (Optional, default=False)
                Force renameKey() to replace a key with new_key_name.
                For example if your list already has a 'loc' key, and you do this::

                    newgl = nemgl.renameKey("other_loc", "loc")

                glbase will break with the critical error::

                    CRITICAL: new_key_name 'loc' is present in the list already!

                set replace_exisiting_key=True and glbase will no longer complain and will
                silently overwrite the old key

        **Returns**
            A new list with a renamed key
        """
        assert old_key_name, "you must specify an old key name"
        assert new_key_name, "you must specify a new key name"
        assert old_key_name in self.linearData[0], "old_key_name '%s' not found in the list" % old_key_name
        assert old_key_name != new_key_name, 'Cannot replace the old key with the same new key'
        if not replace_existing_key:
            assert new_key_name not in self.linearData[0], "new_key_name '%s' is present in the list already! You might want to set replace_existing_key=True if you are sure" % new_key_name

        newl = []

        newl = qdeepcopy(self.linearData) # copy
        [newitem.update({new_key_name: newitem[old_key_name]}) for newitem in newl] # in-place modify
        if not keep_old_key:
            [newitem.pop(old_key_name) for newitem in newl]

        """
        for item in self.linearData:
            newitem = item.copy()
            newitem[new_key_name] = newitem[old_key_name]
            if not keep_old_key:
                del newitem[old_key_name]
            newl.append(newitem)
        """

        newgl = self.shallowcopy()
        newgl.linearData = newl
        newgl._optimiseData()
        self.log.info("Renamed key '%s' to '%s'" % (old_key_name, new_key_name))
        return newgl

    def remove(self, key=None, value=None):
        """
        remove a particular item (or items) by key and value

        **Arguments**
            key (Required)
                The key to look for value in

            value (Required)
                if this value is found in key. Then remove the item
        **Retuns**
            A new genelist, with the item(s) removed
        """
        assert key, "remove: You must specify a key"
        assert value, "remove: You must specify a value"
        assert key in list(self.keys()), "remove: key '%s was not found in this genelist" % key

        newl = self.shallowcopy() # Just use a view as we are not really modifying the data.
        newl.linearData = [] # get a new view
        removed = 0

        for item in self.linearData:
            if not item[key] == value:
                newl.linearData.append(item)
            else:
                removed += 1

        newl._optimiseData()
        self.log.info("remove: removed %s items" % removed)
        return newl

genelist = Genelist # Hack alert! Basically used only in map() for some dodgy old code I do not want to refactor.
