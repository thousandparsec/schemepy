"""
A benchmark tool.
"""

import os
import cStringIO

class Benchmark(object):

    def __init__(self, repeat=1000000, title="Benchmark", rehearsal=False):
        """\
         - repeat:    default number of times to run each measure.
         - title:     title of the benchmark.
         - rehearsal: set to True to enable a rehearsal pass of each
                      measure.
        """
        self._repeat = repeat
        self._title = title
        self._rehearsal = rehearsal
        self._measures = []

    def measure(self, title, func, *args):
        """\
        Add a measure to the benchmark. It is not run immediately,
        but lazily when the report is needed.

         - title:  the title of this measure
         - func:   the callable to run
         - args:   the arguments to fun
        """
        self._measures.append((func, args, title))

    def report(self):
        """\
        Generate the report.
        """
        rehearsal = None
        if self._rehearsal:
            rehearsal = self._measure_all()

        results = self._measure_all()
        return Report(self._title, results, rehearsal)

    def _measure_all(self):
        "Run all measures and return the result."
        results = []
        for measure in self._measures:
            func, args, title = measure
            try:
                t_start = os.times()
                for i in xrange(self._repeat):
                    func(*args)
                t_end = os.times()
                t_ms = [(t[1]-t[0])/self._repeat \
                        for t in zip(t_start, t_end)]
                t_ms = (t_ms[0], t_ms[1], t_ms[4])
                results.append((title, t_ms))
            except Exception, e:
                results.append((title, e))
            
        return results

class Report(object):
    """The benchmark report."""
    formatters = {}
    
    @classmethod
    def install_formatter(cls, name, formatter):
        """\
        install formatter as name. A formatter should be
        a callable object, which accept a Report as the
        first argument followed by any arbitrary user provided
        arguments and perform the formatting. It may or
        may not return the result.

        For example, a plain text formatter may format the
        result and return it as a string. But an image formatter
        may accept a keyword parameter of filename and write
        the result directly to that file.
        """
        cls.formatters[name] = formatter
    
    def __init__(self, title, results, rehearsal=None):
        self.title = title
        self.results = results
        self.rehearsal = rehearsal

    def format(self, type, *args, **kwargs):
        """\
        Format the report. Supported types

         - text
        """
        formatter = Report.formatters.get(type, None)
        if formatter is None:
            raise IndexError("No such formatter %s" % type)
        return formatter(self, *args, **kwargs) 
    
    def __str__(self):
        return self.format("text")


class TextFormatter(object):
    """\
    Format the report as plain text.
    """
    def __call__(self, report):
        io = cStringIO.StringIO()
        if report.rehearsal:
            print >>io, report.title, "(Rehearsal)", '-'*(67-len(report.title))
            self._print_times(io, report.rehearsal)
            print >>io
            
        print >>io, report.title, '-'*(79-len(report.title))
        self._print_times(io, report.results)

        return io.getvalue()

    def _print_times(self, io, results):
        title_len = max([len(rlt[0]) for rlt in results]) + 3
        print >>io, ' '*title_len + \
              "        user      system        real       total"
        for rlt in results:
            if isinstance(rlt[1], tuple):
                print >>io, "%s%12.6f%12.6f%12.6f%12.6f" % \
                      (rlt[0].ljust(title_len),
                       rlt[1][0],
                       rlt[1][1],
                       rlt[1][2],
                       sum(rlt[1]))
            else:                       # Error
                print >>io, "%s%s: %s" % \
                      (rlt[0].ljust(title_len), rlt[1].__class__.__name__, rlt[1])
    
Report.install_formatter("text", TextFormatter())
