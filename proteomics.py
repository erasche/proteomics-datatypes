"""
Proteomics format classes
"""
import logging
import re
import binascii

from galaxy.datatypes import data
from galaxy.datatypes.data import Text
from galaxy.datatypes.xml import GenericXml
from galaxy.datatypes.binary import Binary
from galaxy.datatypes.tabular import Tabular

log = logging.getLogger(__name__)


class Wiff(Binary):
    """Class for wiff files."""
    file_ext = 'wiff'
    allow_datatype_change = False
    composite_type = 'auto_primary_file'

    def __init__(self, **kwd):
        Binary.__init__(self, **kwd)

        self.add_composite_file(
            'wiff',
            description='AB SCIEX files in .wiff format. This can contain all needed information or only metadata.',
            is_binary=True)

        self.add_composite_file(
            'wiff_scan',
            description='AB SCIEX spectra file (wiff.scan), if the corresponding .wiff file only contains metadata.',
            optional='True', is_binary=True)

    def generate_primary_file(self, dataset=None):
        rval = ['<html><head><title>Wiff Composite Dataset </title></head><p/>']
        rval.append('<div>This composite dataset is composed of the following files:<p/><ul>')
        for composite_name, composite_file in self.get_composite_files(dataset=dataset).iteritems():
            fn = composite_name
            opt_text = ''
            if composite_file.optional:
                opt_text = ' (optional)'
            if composite_file.get('description'):
                rval.append('<li><a href="%s" type="text/plain">%s (%s)</a>%s</li>' % (fn, fn, composite_file.get('description'), opt_text))
            else:
                rval.append('<li><a href="%s" type="text/plain">%s</a>%s</li>' % (fn, fn, opt_text))
        rval.append('</ul></div></html>')
        return "\n".join(rval)

if hasattr(Binary, 'register_unsniffable_binary_ext'):
    Binary.register_unsniffable_binary_ext('wiff')


class IdpDB(Binary):
    file_ext = "idpDB"

if hasattr(Binary, 'register_unsniffable_binary_ext'):
    Binary.register_unsniffable_binary_ext('idpDB')


class PepXmlReport(Tabular):
    """pepxml converted to tabular report"""
    file_ext = "tsv"

    def __init__(self, **kwd):
        Tabular.__init__(self, **kwd)
        self.column_names = ['Protein', 'Peptide', 'Assumed Charge', 'Neutral Pep Mass (calculated)', 'Neutral Mass', 'Retention Time', 'Start Scan', 'End Scan', 'Search Engine', 'PeptideProphet Probability', 'Interprophet Probabaility']

    def display_peek(self, dataset):
        """Returns formated html of peek"""
        return Tabular.make_html_table(self, dataset, column_names=self.column_names)


class ProtXmlReport(Tabular):
    """protxml converted to tabular report"""
    file_ext = "tsv"
    comment_lines = 1

    def __init__(self, **kwd):
        Tabular.__init__(self, **kwd)
        self.column_names = [
            "Entry Number", "Group Probability",
            "Protein", "Protein Link", "Protein Probability",
            "Percent Coverage", "Number of Unique Peptides",
            "Total Independent Spectra", "Percent Share of Spectrum ID's",
            "Description", "Protein Molecular Weight", "Protein Length",
            "Is Nondegenerate Evidence", "Weight", "Precursor Ion Charge",
            "Peptide sequence", "Peptide Link", "NSP Adjusted Probability",
            "Initial Probability", "Number of Total Termini",
            "Number of Sibling Peptides Bin", "Number of Instances",
            "Peptide Group Designator", "Is Evidence?"]

    def display_peek(self, dataset):
        """Returns formated html of peek"""
        return Tabular.make_html_table(self, dataset, column_names=self.column_names)


class ProteomicsXml(GenericXml):
    """ An enhanced XML datatype used to reuse code across several
    proteomic/mass-spec datatypes. """

    def sniff(self, filename):
        """ Determines whether the file is the correct XML type. """
        with open(filename, 'r') as contents:
            while True:
                line = contents.readline()
                if line is None or not line.startswith('<?'):
                    break
            # pattern match <root or <ns:root for any ns string
            pattern = '^<(\w*:)?%s' % self.root
            return line is not None and re.match(pattern, line) is not None

    def set_peek(self, dataset, is_multi_byte=False):
        """Set the peek and blurb text"""
        if not dataset.dataset.purged:
            dataset.peek = data.get_file_peek(dataset.file_name, is_multi_byte=is_multi_byte)
            dataset.blurb = self.blurb
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'


class PepXml(ProteomicsXml):
    """pepXML data"""
    file_ext = "pepxml"
    blurb = 'pepXML data'
    root = "msms_pipeline_analysis"


class MzML(ProteomicsXml):
    """mzML data"""
    file_ext = "mzml"
    edam_format = "format_3244"
    blurb = 'mzML Mass Spectrometry data'
    root = "(mzML|indexedmzML)"


class ProtXML(ProteomicsXml):
    """protXML data"""
    file_ext = "protxml"
    blurb = 'prot XML Search Results'
    root = "protein_summary"


class MzXML(ProteomicsXml):
    """mzXML data"""
    file_ext = "mzxml"
    blurb = "mzXML Mass Spectrometry data"
    root = "mzXML"


class MzIdentML(ProteomicsXml):
    file_ext = "mzid"
    edam_format = "format_3247"
    blurb = "XML identified peptides and proteins."
    root = "MzIdentML"


class TraML(ProteomicsXml):
    file_ext = "traml"
    edam_format = "format_3246"
    blurb = "TraML transition list"
    root = "TraML"


class MzQuantML(ProteomicsXml):
    file_ext = "mzq"
    edam_format = "format_3248"
    blurb = "XML quantification data"
    root = "MzQuantML"


class ConsensusXML(ProteomicsXml):
    file_ext = "consensusxml"
    blurb = "OpenMS multiple LC-MS map alignment file"
    root = "consensusXML"


class FeatureXML(ProteomicsXml):
    file_ext = "featurexml"
    blurb = "OpenMS feature file"
    root = "featureMap"


class IdXML(ProteomicsXml):
    file_ext = "idxml"
    blurb = "OpenMS identification file"
    root = "IdXML"


class TandemXML(ProteomicsXml):
    file_ext = "tandem"
    blurb = "X!Tandem search results file"
    root = "bioml"


class Mgf(Text):
    """Mascot Generic Format data"""
    file_ext = "mgf"

    def set_peek(self, dataset, is_multi_byte=False):
        """Set the peek and blurb text"""
        if not dataset.dataset.purged:
            dataset.peek = data.get_file_peek(dataset.file_name, is_multi_byte=is_multi_byte)
            dataset.blurb = 'mgf Mascot Generic Format'
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def sniff(self, filename):
        mgf_begin_ions = "BEGIN IONS"
        max_lines = 100

        with open(filename) as handle:
            for i, line in enumerate(handle):
                line = line.rstrip()
                if line == mgf_begin_ions:
                    return True
                if i > max_lines:
                    return False


class MascotDat(Text):
    """Mascot search results """
    file_ext = "mascotdat"

    def set_peek(self, dataset, is_multi_byte=False):
        """Set the peek and blurb text"""
        if not dataset.dataset.purged:
            dataset.peek = data.get_file_peek(dataset.file_name, is_multi_byte=is_multi_byte)
            dataset.blurb = 'mascotdat Mascot Search Results'
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def sniff(self, filename):
        mime_version = "MIME-Version: 1.0 (Generated by Mascot version 1.0)"
        max_lines = 10

        with open(filename) as handle:
            for i, line in enumerate(handle):
                line = line.rstrip()
                if line == mime_version:
                    return True
                if i > max_lines:
                    return False


class RAW(Binary):
    """Class describing a Thermo Finnigan binary RAW file"""
    file_ext = "raw"

    def sniff(self, filename):
        # Thermo Finnigan RAW format is proprietary and hence not well documented.
        # Files start with 2 bytes that seem to differ followed by F\0i\0n\0n\0i\0g\0a\0n
        # This combination represents 17 bytes, but to play safe we read 20 bytes from
        # the start of the file.
        try:
            header = open(filename).read(20)
            hexheader = binascii.b2a_hex(header)
            finnigan = binascii.hexlify('F\0i\0n\0n\0i\0g\0a\0n')
            if hexheader.find(finnigan) != -1:
                return True
            return False
        except:
            return False

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            dataset.peek = "Thermo Finnigan RAW file"
            dataset.blurb = data.nice_size(dataset.get_size())
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def display_peek(self, dataset):
        try:
            return dataset.peek
        except:
            return "Thermo Finnigan RAW file (%s)" % (data.nice_size(dataset.get_size()))


if hasattr(Binary, 'register_sniffable_binary_format'):
    Binary.register_sniffable_binary_format('raw', 'raw', RAW)


class Msp(Text):
    """ Output of NIST MS Search Program chemdata.nist.gov/mass-spc/ftp/mass-spc/PepLib.pdf """
    file_ext = "msp"

    @staticmethod
    def next_line_starts_with(contents, prefix):
        next_line = contents.readline()
        return next_line is not None and next_line.startswith(prefix)

    def sniff(self, filename):
        """ Determines whether the file is a NIST MSP output file.

        >>> fname = get_test_fname('test.msp')
        >>> Msp().sniff(fname)
        True
        >>> fname = get_test_fname('test.mzXML')
        >>> Msp().sniff(fname)
        False
        """
        with open(filename, 'r') as contents:
            return Msp.next_line_starts_with(contents, "Name:") and Msp.next_line_starts_with(contents, "MW:")

class SPLibNoIndex( Text ):
    """SPlib without index file """
    file_ext = "splib"

    def set_peek( self, dataset, is_multi_byte=False ):
        """Set the peek and blurb text"""
        if not dataset.dataset.purged:
            dataset.peek = data.get_file_peek( dataset.file_name, is_multi_byte=is_multi_byte )
            dataset.blurb = 'Spectral Library without index files'
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'


class SPLib(Msp):
    """SpectraST Spectral Library. Closely related to msp format"""
    file_ext = "splib"
    composite_type = 'auto_primary_file'

    def __init__(self, **kwd):
        Msp.__init__(self, **kwd)
        self.add_composite_file('library.splib',
                                description='Spectral Library. Contains actual library spectra',
                                is_binary=False)
        self.add_composite_file('library.spidx',
                                description='Spectrum index',  is_binary=False)
        self.add_composite_file('library.pepidx',
                                description='Peptide index', is_binary=False)

    def generate_primary_file(self, dataset=None):
        rval = ['<html><head><title>Spectral Library Composite Dataset </title></head><p/>']
        rval.append('<div>This composite dataset is composed of the following files:<p/><ul>')
        for composite_name, composite_file in self.get_composite_files(dataset=dataset).iteritems():
            fn = composite_name
            opt_text = ''
            if composite_file.optional:
                opt_text = ' (optional)'
            if composite_file.get('description'):
                rval.append('<li><a href="%s" type="text/plain">%s (%s)</a>%s</li>' % (fn, fn, composite_file.get('description'), opt_text))
            else:
                rval.append('<li><a href="%s" type="text/plain">%s</a>%s</li>' % (fn, fn, opt_text))
        rval.append('</ul></div></html>')
        return "\n".join(rval)

    def set_peek(self, dataset, is_multi_byte=False):
        """Set the peek and blurb text"""
        if not dataset.dataset.purged:
            dataset.peek = data.get_file_peek(dataset.file_name, is_multi_byte=is_multi_byte)
            dataset.blurb = 'splib Spectral Library Format'
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def sniff(self, filename):
        """ Determines whether the file is a SpectraST generated file.
        """
        with open(filename, 'r') as contents:
            return Msp.next_line_starts_with(contents, "Name:") and Msp.next_line_starts_with(contents, "LibID:")


class Ms2(Text):
    file_ext = "ms2"

    def sniff(self, filename):
        """ Determines whether the file is a valid ms2 file.

        >>> fname = get_test_fname('test.msp')
        >>> Ms2().sniff(fname)
        False
        >>> fname = get_test_fname('test.ms2')
        >>> Ms2().sniff(fname)
        True
        """

        with open(filename, 'r') as contents:
            header_lines = []
            while True:
                line = contents.readline()
                if line is None or len(line) == 0:
                    pass
                elif line.startswith('H\t'):
                    header_lines.append(line)
                else:
                    break

        for header_field in ['CreationDate', 'Extractor', 'ExtractorVersion', 'ExtractorOptions']:
            found_header = False
            for header_line in header_lines:
                if header_line.startswith('H\t%s' % (header_field)):
                    found_header = True
                    break
            if not found_header:
                return False

        return True


# unsniffable binary format, should do something about this
class XHunterAslFormat(Binary):
    """ Annotated Spectra in the HLF format http://www.thegpm.org/HUNTER/format_2006_09_15.html """
    file_ext = "hlf"

if hasattr(Binary, 'register_unsniffable_binary_ext'):
    Binary.register_unsniffable_binary_ext('hlf')


class Sf3(Binary):
    """Class describing a Scaffold SF3 files"""
    file_ext = "sf3"

if hasattr(Binary, 'register_unsniffable_binary_ext'):
    Binary.register_unsniffable_binary_ext('sf3')
