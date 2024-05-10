"""

tinyglbase

(c) 2024 Helixiome, forked from glbase3.

.


"""

import sys, os, csv, copy, pickle, gzip, functools
from operator import itemgetter
from .progress import progressbar

class UnRecognisedCSVFormatError(Exception):
    """
    Error
        The csv is not recognised, and produces an error somewhere inside
        _loadCSV(). Print a selection of output based on what glbase
        expects the CSV to look like, hopefully this explains what may be
        going wrong with the CSV.
    """
    def __init__(self, message, file_handle, format):
        """
        Format and ouput a series of messages so that I can see why the csv is not loading.
        """
        oh = open(file_handle, "rU")
        config.log.error("csv/tsv file did not pass the csv parser")
        config.log.error("Message: %s" % message)
        print("-----------------------")
        print("CSV Diagnostic:")
        if "skiplines" in format: # skip the lines.
            if format["skiplines"] != -1:
                for n in range(format["skiplines"]):
                    oh.readline().rstrip("\r\n")

        print("0:", oh.readline().rstrip("\r\n"))
        print("1:", oh.readline().rstrip("\r\n"))
        print("2:", oh.readline().rstrip("\r\n"))
        print("3:", oh.readline().rstrip("\r\n"))
        print("-----------------------")
        print("Format Specifier: %s" % (" ".join(["%s:%s\t" % (key, format[key]) for key in format])))
        print("Expected Format, based on the format specifier:")
        oh.close()

        # This is a safe-ish version of loadCSV() that intelligently fails.

        if "sniffer" not in format:
            oh = open(file_handle, "rU")
            if "dialect" in format:
                reader = csv.reader(oh, dialect=format["dialect"])
            else:
                reader = csv.reader(oh)

            try:
                if "skiplines" in format:
                    skiplines = format["skiplines"]
                else:
                    skiplines = 0 # skip any header row by default.
            except:
                print("Error: End of File") # premature end of file, skip out.
                print("-----------------------")
                print("Error: %s" % (message))
                return

            for index, column in enumerate(reader): # This is cryptically called column, when it is actually row.
                if index > skiplines:
                    if column: # list is empty, so omit.
                        if (not (column[0] in typical_headers)):
                            d = {}
                            for key in format:
                                if not (key in ignorekeys): # ignore these tags
                                    try:
                                        if not key in d:
                                            d[key] = {}
                                        if isinstance(format[key], dict) and "code" in format[key]:
                                            # a code block insertion goes here - any valid lib and one line python code fragment
                                            # store it as a dict with the key "code"
                                            d[key] = eval(format[key]["code"]) # this always fails for some reason...
                                        else:
                                            d[key] = str(column[format[key]])
                                    except:
                                        d[key] = "mangled"
                            print("%s" % (" ".join(["%s:%s" % (key, d[key]) for key in d])))
                            if index > 3:
                                break
        else:
            print("  No specified format (glbase will guess)")

        print("-----------------------")
        config.log.error("End of error output")

class UnrecognisedFileFormatError(Exception):
    """
    Error
        File is not recognised, but not in loadCSV.
        Just print some diagnostic stuff, but not so fancy as
        UnRecognisedCSVFormatError
    """
    def __init__(self, message, file_handle, format):
        """
        Format and ouput a series of messages so that I can see why the csv is not loading.
        """
        oh = open(file_handle, "rU")
        config.log.critical("Unrecognised file format")
        print("-----------------------")
        print("Diagnostic:")
        print("0:", oh.readline().rstrip("\r\n"))
        print("1:", oh.readline().rstrip("\r\n"))
        print("2:", oh.readline().rstrip("\r\n"))
        print("3:", oh.readline().rstrip("\r\n"))
        if "sniffer" in format:
            print("Format Specifier: Sniffer (guess the file format)")
        else:
            print(
                "Format Specifier: %s"
                % " ".join("%s:%s" % (key, format[key]) for key in format)
            )

        print("-----------------------")
        config.log.critical("%s" % (message,))
        print()

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
        raise BadBinaryFileFormatError(filename)
    except FileNotFoundError:
        raise AsseritionError(f'File "{filename}" changed whilst trying to read it')

    try:
        cons = len(newl._conditions) # expression-like object
        config.log.info("Loaded '%s' binary file with %s items, %s conditions" % (filename, len(newl), cons))
    except AttributeError:
        config.log.info("Loaded '%s' binary file with %s items" % (filename, len(newl)))

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
    def __init__(self, filename=None, loadable_list=None, gzip=False, **kargs):
        self.linearData = []
        self.dataByChr = None # this is private, use get by loc.
        self.debug = False
        self.draw = draw(self)
        self.name = "Generic List"
        self.metadata = {} # container for various metadata's to extract figures from.
        self.__deathline = None # Error reporting in load_CSV()
        self.__deathindx = None

        format = sniffer
        if "format" in kargs:
            format = kargs["format"] # I expect a filename = is coming.

        if "force_tsv" in kargs and kargs["force_tsv"]:
            format["force_tsv"] = True

        if filename:
            if "format" in kargs:
                self.load(filename=filename, format=format, gzip=gzip)
            else:
                raise AssertionError('Due to excessive ambiguity the sniffing function of genelists has been removed and you now MUST provide a format argument, you can reenable this feature by specifying the sniffer: format=format.sniffer')

            config.log.info(f"genelist: loaded '{filename}' found {len(self.linearData):,} items")
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

        if format:
            if "special" in format: # special loads
                if format["special"] == "fasta":
                    self.linearData = utils.convertFASTAtoDict(filename=filename, gzip_input=gzip)
                    # See if I can parse names into a location?
                    try:
                        for item in self.linearData:
                            item["loc"] = location(loc=item["name"])
                    except Exception:
                        pass
                    self._optimiseData()
                    return True
                if format["special"] == "hmmer_tbl":
                    self.linearData = _load_hmmer_tbl(filename, gzip=gzip)
                    self._optimiseData()
                    return True
                elif format['special'] == 'hmmer_domtbl':
                    self.linearData = _load_hmmer_domtbl(filename, gzip=gzip)
                    self._optimiseData()
                    return True
        else:
            raise AssertionError('Due to excessive ambiguity the sniffing function of genelists has been removed and you now MUST provide a format argument')

        csv_headers = frozenset(["csv", "xls", "tsv", "txt", "bed"])
        if filename.split(".")[-1].lower() in csv_headers: # check the last one for a csv-like header
            self.loadCSV(filename=filename, format=format, gzip=gzip, **kargs)
        elif filename.split(".")[-1] in ["glb"]:
            self = glload(filename) # will this work?
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

        # decide whether to respect the force_tsv arg.
        if not format:
            if "force_tsv" in kargs and kargs["force_tsv"]:
                format = sniffer_tsv
            else:
                format = sniffer

        if "debug" in format and format["debug"]:
            print("--------")
            print("DEBUG load:")
            self._loadCSV(filename=self.fullfilename, format=format, **kargs)
        else:
            try:
                self._loadCSV(filename=self.fullfilename, format=format, **kargs)
            except Exception:
                # oh dear. Die.
                if self.__deathline:
                    config.log.error(f"Died on line: '{self.__deathline}'")
                raise UnRecognisedCSVFormatError("'%s' appears mangled, the file does not fit the format specifier" % self.fullfilename, self.fullfilename, format)

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

        if "sniffer" in format:
            # I need to construct my own format
            format = {}
            for top_line in reader:
                for index, key in enumerate(top_line): # get all the potential keys.
                    format[key] = index
                skiplines = -1 # if the sniffer is used then when it gets to the below
                # index will = 0 = skiplines causing the first line to be missed.
                break

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
            # This is cryptically called column, when it is actually row.\
            # there is a reason for that, it is so that in the formats it appears:
            # "refseq": column[1] # see :)
            #print(index, column) # debug for when all else fails!
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

            if "debug" in format and format["debug"]:
                debug_line += 1
                print(f"{index}:'{column}'")
                if isinstance(format["debug"], int) and debug_line > format["debug"]:
                    break # If an integer, collect that many items.

            if column[0] not in typical_headers:
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

    def _optimiseData(self):
        """
        (Internal)
        Call me after modifying the data to bin and build the internal tables.
        """
        self.dataByChr = None
        if not self.linearData: # list is empty, not possible to optimise anything...
            return False

        keys = self.keys()

        # Guess a loc key
        loc_key = None
        if "tss_loc" in keys: # always use tss_loc in preference of loc, if available
            loc_key = "tss_loc"
        elif "loc" in keys:
            loc_key = "loc" # Don't change this though. annotate() relies on the bucket system using tss_loc

        if "tss_loc" in keys and "loc" in keys:
            config.log.warning("List contains both 'tss_loc' and 'loc'. By default glbase will use 'tss_loc' for overlaps/collisions/annotations")

        self.dataByChr = {}
        self.dataByChrIndexLookBack = {}
        self.buckets = {}
        if loc_key:
            for n, item in enumerate(self.linearData): # build the chromosome quick search maps.
                chr = item[loc_key]["chr"]
                if chr not in self.dataByChr:
                    self.dataByChr[chr] = []
                    self.dataByChrIndexLookBack[chr] = []
                self.dataByChr[chr].append(item)
                self.dataByChrIndexLookBack[chr].append(n) # oh sweet, sweet dirty hack...
                # I can't remember what this look-back is for, but you
                # can use it to get the linearData index even though looking at the
                # dataByChr data It is not documented for a reason!

                if chr not in self.buckets:
                    self.buckets[chr] = {}
                # work out the bucket(s) for the location.
                # which bucket is left and right in?
                left_buck = (item[loc_key]["left"]//config.bucket_size)*config.bucket_size
                right_buck = ((item[loc_key]["right"]+config.bucket_size)//config.bucket_size)*config.bucket_size
                buckets_reqd = list(range(left_buck, right_buck, config.bucket_size))

                #print n, item[loc_key], buckets_reqd, left_buck, right_buck, len(buckets_reqd)

                for b in buckets_reqd:
                    if b not in self.buckets[chr]:
                        self.buckets[chr][b] = []
                    self.buckets[chr][b].append(n) # use index to maintain uniqueness.

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
                    # TODO: This is indeed present if the genelist is an expresion object;
                    # The item in unhashable and cannot be added to the qkeyfind
                    # This should be pretty rare if not impossible.
                    #config.log.error(f'!Unhashable key: {key} for qkeyfind system')
                    pass

                # Now to do a find you just go:
                # item_indeces = self.qkeyfind["name"]["Stat3"]

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
            return(newl)
        return None

    def index(self, key, value):
        """
        **Purpose**
            A bit like the Python index() but for key:value pairs

            NOTE: The method is lazy and finds the first index and returns that.

        **Arguments**
            Key (Required)
                the key to search in

            Value (Required)
                the value to find

        **Returns**
            The index of the list where the item is contained.
        """
        assert key, "index: must send key"
        assert value, "index: must send value"

        return min(self.qkeyfind[key][value])

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
            oh = open(filename, "w")

        if not self.linearData: # data is empty, fail graciously.
            config.log.error(f"csv file '{filename}' is empty, no file written")
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
        config.log.info(f"Saved '{filename}'")
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
        if len(self.linearData) > config.NUM_ITEMS_TO_PRINT:
            out = []
            # welcome to perl
            for index in range(config.NUM_ITEMS_TO_PRINT):
                out.append("%s: %s" % (index, ", ".join(["%s: %s" % (key, self.linearData[index][key]) for key in self.linearData[index]])))
            out = "%s\n... truncated, showing %s/%s" % ("\n".join(out), config.NUM_ITEMS_TO_PRINT, len(self.linearData))

            if config.PRINT_LAST_ITEM:
                out = "%s\n%s" % (out, "%s: %s" % (len(self.linearData), ", ".join(["%s: %s" % (key, self.linearData[-1][key]) for key in self.linearData[-1]])))

        elif len(self.linearData) == 0:
            out = "This list is empty"

        else: # just print first entry.
            out = []
            for index in range(len(self.linearData)):
                out.append("%s: %s" % (index, ", ".join(["%s: %s" % (key, self.linearData[index][key]) for key in self.linearData[index]])))
            out = "%s\nShowing %s/%s" % ("\n".join(out), len(self.linearData), len(self.linearData))

        return out

    def _collectIdenticalKeys(self, gene_list):
        """
        (Internal)
        returns a list of keys in common between this list and gene_list
        """
        return list(set(self.keys()) & set(gene_list.keys()))

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
        config.log.info("getColumns: got only the columns: %s" % ", ".join(return_keys))
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
                                newl.linearData.append(utils.qdeepcopy(item))
            else:
                for item in self.linearData:
                    for r in list_of_items:
                        if r.search(str(item[key])): # sometimes gene names accidentally get stored as numbers
                            newl.linearData.append(utils.qdeepcopy(item))
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
            if not silent: config.log.info("getRowsByKey: Found 0 items")
            return None

        if not silent: config.log.info(f"getRowsByKey: Found {len(newl)} items")

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
            config.log.info('filter_by_in: Removed {} entries'.format(len(self) - len(newl)))
        else:
            newl = [item for item in newgl.linearData if value in item[key]]
            config.log.info('filter_by_in: Kept {} matching entries'.format(len(self) - len(newl)))

        newgl.linearData = newl
        newgl._optimiseData()
        return newgl

    def filter_by_value(self, key=None, evaluator=None, value=None, **kargs):
        """
        **Purpose**
            Filter data based on a key with some numeric data.

            If you skip the keyword arguments you can write nice things like this:

            newdata = expn.filter_by_value("q-value", "<", 0.05)

        **Arguments**
            key (Required)
                The name of the key to use to filter the data on.
                or a name of a condition in the expression object to filter on.

            evaluator (Required, values=["gt", "lt", "gte", "lte", "equal"])
                The comparator.
                    gt = '>' greater than value
                    lt = '<' less than value
                    gte = '>=' greater than or equal to value
                    lte = '<=' less than or equal to value
                    equal = "==" equal to value

                    You can also send the > < >= <= or == as a string symbol as well.

            value (Required)
                The value of change required to pass the test.

        **Returns**
            A new genelist-like object containing only the items that pass.
        """
        assert key, "filter_by_value: 'key' argument is required"
        assert evaluator in ("gt", "lt", "gte", "lte", "equal", ">", "<", ">=", "<=", "=="), "filter_by_value: evaluator argument '%s' not recognised" % evaluator

        if self.__repr__() == "glbase.expression" and key in self._conditions:
            assert key in self._conditions, "filter_by_value:'%s' not found in this expression object" % key
            its_a_condition = True
        else:
            assert key in list(self.keys()), "filter_by_value: no key named '%s' found in this genelist object" % key
            its_a_condition = False

        new_expn = []

        conv_dict = {"gt": ">", "lt": "<", "gte": ">=", "lte": " <=", "equal": "=="}
        if evaluator in ("gt", "lt", "gte", "lte", "equal"):
            evaluator = conv_dict[evaluator]

        if its_a_condition:
            cond_index = self._conditions.index(key)
            for item in self.linearData:
                if eval("%s %s %s" % (item["conditions"][cond_index], evaluator, value)):
                    new_expn.append(item)
        else: # filter on a normal key.
            for item in self.linearData:
                if eval("%s %s %s" % (item[key], evaluator, value)):
                    new_expn.append(item)

        ret = self.shallowcopy()
        ret.load_list(new_expn) # In case I make optimisations to load_list()

        config.log.info("filter_by_value: Filtered expression for ['%s' %s %s], found: %s" % (key, evaluator, value, len(ret)))
        return ret

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
        for index, item in enumerate(gene_list):
            if greedy:
                results = self._findDataByKeyGreedy(map_key, item[map_key])
            else:
                results = self._findDataByKeyLazy(map_key, item[map_key])
                if results:
                    results = [results] # coerce to a single member list to simplify code below

            if results:
                if logic == "and":
                    for r in results:
                        new_entry = utils.qdeepcopy(r) # inherit from the right
                        new_entry.update(item) # Key items inherit from the right hand side

                        # add a special case for expression objects:
                        # test that both objects are actually expression objects with _conditions and ["conditions"]:
                        # Funky syntax in case I ever derive a descendent of expression:
                        if "conditions" in item and "conditions" in r: # See if conditions in both genelists:
                            # The below line will escape the rare occasions a genelist is sent that has "conditions" but no _conditions
                            if hasattr(self, '_conditions') and hasattr(gene_list, '_conditions'): # I think we can safely assume both are bonafide expression
                                if self._conditions != gene_list._conditions: # DONT do this if the conditions are identical.
                                    new_entry["conditions"] = item["conditions"] + r["conditions"]
                                    newl._conditions = gene_list._conditions + self._conditions # will update multiple times, whoops.

                                    # only look at the err keys if I am merging the conditions
                                    if "err" in item and "err" in r:
                                        if self._conditions != gene_list._conditions: # DONT do this if the conditions are identical.
                                            new_entry["err"] = item["err"] + r["err"]
                                    elif "err" in new_entry: # Only one list has an err key, output a warning and kill it.
                                        if not __warning_assymetric_errs:
                                            __warning_assymetric_errs = True
                                            config.log.warning("map: Only one of the two lists has an 'err' key, deleting it")
                                        del new_entry["err"]

                        newl.linearData.append(new_entry)
            elif logic == "notright":
                newl.linearData.append(utils.qdeepcopy(item)) # only inherit from the right, can't inheret from the left, as no matching map

            p.update(index)

        if not silent:
            if logic == "notright":
                config.log.info("map: '%s' vs '%s', using '%s' via '%s', kept: %s items" % (self.name, gene_list.name, map_key, logic, len(newl)))
            else:
                config.log.info("map: '%s' vs '%s', using '%s', found: %s items" % (self.name, gene_list.name, map_key, len(newl)))

        if len(newl.linearData):
            newl._optimiseData()
            return(newl)
        return None

    def addEmptyKey(self, key=None, value=None):
        """
        **Purpose**
            You need to add a empty key ot the list so that it becomes compatible with some downstream function.
            But you don't care what is in the key, or just want to set the key to a specific value for the entire list

            This is the one to use::

                gl = genelist("a_bed.bed", format=format.minimal_bed)

                print(gl)
                0: loc: chr1:1000-2000

                # Argh! I need a strand key for the downstream, but I don't actually care what's in strand!

                gl = gl.addEmptyKey("strand", "+")

                # Phew! That's better!

                print(gl)
                0: loc: chr1:1000-2000, strand: +

        **Arguments**
            key (Required)
                the key to name to add

            value (Optional, default=None)
                A value to fill into each new key.

        **Returns**
            A new genelist with the added key.
        """
        assert key , "You must specify a new key name"

        newl = self.deepcopy()
        for item in newl:
            item[key] = value

        newl._optimiseData()
        config.log.info("addEmptyKey: Added a new key '%s'" % key)
        return(newl)

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

            config.log.info("removeDuplicates: {} duplicates, list now {} items long".format(len(self)-len(newl), len(newl)))
            return newl

        else:
            assert key in list(self.keys()), f"the key '{key}' was not found in this genelist"

            newl = self.shallowcopy()
            newl.linearData = []
            count = 0

            for item in self.qkeyfind[key]:
                newl.linearData.append(self.linearData[min(self.qkeyfind[key][item])]) # grab first
                # Will only apply a single item (the earliest) even if there
                # IS only one of these items.

            newl._optimiseData()

            config.log.info("removeDuplicates: {} duplicates, list now {} items long".format(len(self) - len(newl), len(newl)))
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

        config.log.info("removeExactDuplicates: %s exact duplicates" % (len(self) - len(newl)))
        return newl

    def removeEmptyDataByKey(self, key=None):
        """
        **Purpose**
            remove any entry that has empty data within 'key'

            For example, consider this data::

                1: name: Nanog, annot: ,      score: 20
                2: name: Sox2,  annot: yep,   score: 30
                3: name: Stat3, annot: kinda, score:

            You can see some columns with empty data::

                data.removeEmptyDataByKey("annot")

            will result in::

                1: name: Nanog, annot: ,      score: 20
                2: name: Stat3, annot: kinda, score:

            Notice that although score is also empty, this function only considers
            data in the annot: key

            Similarly, using "score" will delete the Stat3 entry only::

                data.removeEmptyDataByKey("score")
                print data

                1: name: Nanog, annot: ,      score: 20
                2: name: Sox2,  annot: yep,   score: 30

        **Arguments**
            key
                The key in which to delete empty data

        **Returns**
            The new list with empty data in key removed
        """
        assert key, "No key specified"

        newl = self.deepcopy()
        oldl = newl.linearData # preserve the copies
        newl.linearData = []
        count = 0
        p = progressbar(len(self))

        for item in oldl:
            if item[key]:
                newl.linearData.append(item) # grab first
            # Will only apply a single item (the earliest) even if there
            # IS only one of these items.

        newl._optimiseData()

        config.log.info("Removed empty data in %s key: %s entries" % (key, len(self) - len(newl)))
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

        self.linearData = utils.qdeepcopy(list_to_load)

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

        newl = utils.qdeepcopy(self.linearData) # copy
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
        config.log.info("Renamed key '%s' to '%s'" % (old_key_name, new_key_name))
        return newgl

    def repairKey(self, key_to_repair, fill_in_key, **kargs):
        '''
        **Purpose**
            genelists will tolerate 'holes' (missing key:values) in individual entries.

            A specific example is loading things like a gtf file, which in that format will tolerate missing attirbute tags

            glbase is quite happy with this, but it may cause problems downstream if you try to grab a single key from a genelist

            This method will fill in the holes in 'key_to_repair' by dragging data from 'fill_in key'
        '''
        assert key_to_repair in list(self.keys()), 'key_to_repair: "%s" not found' % key_to_repair
        assert fill_in_key in list(self.keys()), 'fill_in_key: "%s" not found' % fill_in_key

        replaced = 0
        newl = self.deepcopy()
        for item in newl:
            if key_to_repair not in item or not item[key_to_repair]:
                item[key_to_repair] = item[fill_in_key]
                replaced += 1
        newl._optimiseData()

        config.log.info('repairKey: Repaired %s keys' % replaced)
        return newl

    def splitKeyValue(self, key, key_sep=" ", val_sep=":"):
        """
        **Purpose**
            split() the values of key into key:value pairs and add them back into the genelist

            An example is this:

            After loading a fasta  the entries are like this:

            0: name: ENSP00000451042 pep:known chromosome:GRCh37:14:22907539:22907546:1 gene:ENSG00000223997 transcript:ENST00000415118 gene_biotype:TR_D_gene transcript_biotype:TR_D_gene, seq: EIV

            Note that the name value contains the long string:

            "ENSP00000451042 pep:known chromosome:GRCh37:14:22907539:22907546:1 gene:ENSG00000223997 transcript:ENST00000415118 gene_biotype:TR_D_gene transcript_biotype:TR_D_gene"

            It would be more useful to split this up into key:value pairs so glbase can get at the values:

            fasta = fasta.splitKeyValue("name", " ", ":")

            Results in the more useful:

            0: seq: EIV, transcript_biotype: TR_D_gene, pep: known, gene_biotype: TR_D_gene, gene: ENSG00000223997, transcript: ENST00000415118, chromosome: GRCh37:14:22907539:22907546:1

            NOTE: This will work for a relatively simple example, but will fail in more complex versions.

            Notice how the first ENSP00000451042 is lost as it does not have a val_sep (:).

        **Arguments**
            key (Required)
                The key to split

            key_sep (Required, default=" ")
                the separator to discriminate key:value pairs

            val_sep (Required, default=",")
                the separator inbetween the key and value.

        **Returns**
            A new genelist
        """

        newl = self.shallowcopy()
        newl.linearData = []

        for row in self:
            newk = dict(row)
            kk = newk.pop(key)

            kvs = kk.split(key_sep)

            for i in kvs:
                if val_sep in i: # no val_sep so omit it;
                    t = i.split(val_sep) # potential error if more than one sep.
                    k = t[0]
                    v = val_sep.join(t[1:])

                    newk[k] = v

            newl.linearData.append(newk)

        newl._optimiseData()
        config.log.info("splitKeyValue: split '%s' into ~'%s'%s'%s' key value pairs" % (key, len(k), val_sep, len(v)))
        return newl

    def joinKey(self, new_key_name, formatter, keyA, keyB, keep_originals=False):
        """
        **Purpose**
            Perform a string formatting operation on two keys to jon them together.

            Does this:

            item[new_key_name] = formatter % (keyA, keyB)

        **Arguments**
            new_key_name (Required)
                The new key name.

            formatter (REquired)
                string format operation to perform.

            keyA, keyB (Required)
                the two keys to format.

            keep_originals (Optional, default=False)
                keep the original keys.

        **Returns**
            The new genelist
        """
        assert keyA in self.linearData[0], "keyA '%s' not found in this genelist" % keyA
        assert keyB in self.linearData[0], "keyB '%s' not found in this genelist" % keyB

        newl = self.deepcopy()

        for item in newl:
            item[new_key_name] = formatter.format(item[keyA], item[keyB])

            if not keep_originals:
                if new_key_name != keyA: # Don't delete if it is also the new key.
                    del item[keyA]
                if new_key_name != keyB:
                    del item[keyB]

        newl._optimiseData()
        return newl

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
        config.log.info("remove: removed %s items" % removed)
        return newl

genelist = Genelist # Hack alert! Basically used only in map() for some dodgy old code I do not want to refactor.
