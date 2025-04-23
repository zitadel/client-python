# mypy: allow-untyped-defs
from __future__ import annotations

import os
import platform
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timezone

import pytest
from _pytest import nodes, timing

# noinspection PyProtectedMember
# noinspection PyProtectedMember
from _pytest._code.code import ExceptionRepr, ReprFileLocation
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.junitxml import bin_xml_escape
from _pytest.reports import TestReport
from _pytest.stash import StashKey
from _pytest.terminal import TerminalReporter
from dotenv import load_dotenv

xml_key = StashKey["LogXML"]()


class _NodeReporter:
    def __init__(self, nodeid: str | TestReport, xml: LogXML) -> None:
        self.id = nodeid
        self.xml = xml
        self.add_stats = self.xml.add_stats
        self.duration = 0.0
        self.properties: list[tuple[str, str]] = []
        self.nodes: list[ET.Element] = []
        self.attrs: dict[str, str] = {}

    def append(self, node: ET.Element) -> None:
        self.xml.add_stats(node.tag)
        self.nodes.append(node)

    def add_property(self, name: str, value: object) -> None:
        self.properties.append((str(name), bin_xml_escape(value)))

    def add_attribute(self, name: str, value: object) -> None:
        self.attrs[str(name)] = bin_xml_escape(value)

    def make_properties_node(self) -> ET.Element | None:
        """Return a Junit node containing custom properties, if any."""
        if self.properties:
            properties = ET.Element("properties")
            for name, value in self.properties:
                properties.append(ET.Element("property", name=name, value=value))
            return properties
        return None

    def record_testreport(self, testreport: TestReport) -> None:
        names = mangle_test_address(testreport.nodeid)
        existing_attrs = self.attrs
        classnames = names[:-1]
        if self.xml.prefix:
            classnames.insert(0, self.xml.prefix)
        attrs: dict[str, str] = {
            "classname": ".".join(classnames),
            "name": bin_xml_escape(names[-1]),
            "file": testreport.location[0],
        }
        if testreport.location[1] is not None:
            attrs["line"] = str(testreport.location[1])
        if hasattr(testreport, "url"):
            attrs["url"] = testreport.url
        self.attrs = attrs
        self.attrs.update(existing_attrs)  # Restore any user-defined attributes.

    def to_xml(self) -> ET.Element:
        testcase = ET.Element("testcase", self.attrs, time=f"{self.duration:.3f}")
        properties = self.make_properties_node()
        if properties is not None:
            testcase.append(properties)
        testcase.extend(self.nodes)
        return testcase

    def _add_simple(self, tag: str, message: str, data: str | None = None) -> None:
        node = ET.Element(tag, message=message)
        node.text = bin_xml_escape(data)
        self.append(node)

    def write_captured_output(self, report: TestReport) -> None:
        if not self.xml.log_passing_tests and report.passed:
            return

        content_out = report.capstdout
        content_log = report.caplog
        content_err = report.capstderr
        if self.xml.logging == "no":
            return
        content_all = ""
        if self.xml.logging in ["log", "all"]:
            content_all = self._prepare_content(content_log, " Captured Log ")
        if self.xml.logging in ["system-out", "out-err", "all"]:
            content_all += self._prepare_content(content_out, " Captured Out ")
            self._write_content(report, content_all, "system-out")
            content_all = ""
        if self.xml.logging in ["system-err", "out-err", "all"]:
            content_all += self._prepare_content(content_err, " Captured Err ")
            self._write_content(report, content_all, "system-err")
            content_all = ""
        if content_all:
            self._write_content(report, content_all, "system-out")

    def _prepare_content(self, content: str, header: str) -> str:
        return "\n".join([header.center(80, "-"), content, ""])

    def _write_content(self, report: TestReport, content: str, jheader: str) -> None:
        tag = ET.Element(jheader)
        tag.text = bin_xml_escape(content)
        self.append(tag)

    def append_pass(self, report: TestReport) -> None:
        self.add_stats("passed")

    def append_failure(self, report: TestReport) -> None:
        # msg = str(report.longrepr.reprtraceback.extraline)
        if hasattr(report, "wasxfail"):
            self._add_simple("skipped", "xfail-marked test passes unexpectedly")
        else:
            assert report.longrepr is not None
            reprcrash: ReprFileLocation | None = getattr(report.longrepr, "reprcrash", None)
            if reprcrash is not None:
                message = reprcrash.message
            else:
                message = str(report.longrepr)
            message = bin_xml_escape(message)
            self._add_simple("failure", message, str(report.longrepr))

    def append_collect_error(self, report: TestReport) -> None:
        """
        Record a collection‑phase failure as a JUnit <error>.

        When pytest fails to collect a test (syntax errors, import errors),
        this method is invoked to write a single <error> element containing
        the representation of that exception.

        :param report: The TestReport instance for the failed collection.
        """
        assert report.longrepr is not None
        self._add_simple("error", "collection failure", str(report.longrepr))

    def append_collect_skipped(self, report: TestReport) -> None:
        """
        Record a collection‑phase skip as a JUnit <skipped>.

        If pytest skips a test before execution (e.g. via xdist
        deferred collection or import‑time skip markers), this writes
        a <skipped> element with the skip reason.

        :param report: The TestReport instance for the skipped collection.
        """
        self._add_simple("skipped", "collection skipped", str(report.longrepr))

    def append_error(self, report: TestReport) -> None:
        assert report.longrepr is not None
        reprcrash: ReprFileLocation | None = getattr(report.longrepr, "reprcrash", None)
        if reprcrash is not None:
            reason = reprcrash.message
        else:
            reason = str(report.longrepr)

        if report.when == "teardown":
            msg = f'failed on teardown with "{reason}"'
        else:
            msg = f'failed on setup with "{reason}"'
        self._add_simple("error", bin_xml_escape(msg), str(report.longrepr))

    def append_skipped(self, report: TestReport) -> None:
        if hasattr(report, "wasxfail"):
            xfailreason = report.wasxfail
            if xfailreason.startswith("reason: "):
                xfailreason = xfailreason[8:]
            xfailreason = bin_xml_escape(xfailreason)
            skipped = ET.Element("skipped", type="pytest.xfail", message=xfailreason)
            self.append(skipped)
        else:
            assert isinstance(report.longrepr, tuple)
            filename, lineno, skipreason = report.longrepr
            if skipreason.startswith("Skipped: "):
                skipreason = skipreason[9:]
            details = f"{filename}:{lineno}: {skipreason}"

            skipped = ET.Element("skipped", type="pytest.skip", message=bin_xml_escape(skipreason))
            skipped.text = bin_xml_escape(details)
            self.append(skipped)
            self.write_captured_output(report)

    def finalize(self) -> None:
        data = self.to_xml()
        # Preserve key attributes
        _id = self.id
        _stats = getattr(self, "stats", {})
        _duration = getattr(self, "duration", 0.0)

        # Clear everything else
        self.__dict__.clear()

        # Restore the preserved pieces
        self.id = _id
        self.stats = _stats
        self.duration = _duration

        # Freeze the XML output
        self.to_xml = lambda: data  # type: ignore[method-assign]


@pytest.fixture
def record_property(request: FixtureRequest) -> Callable[[str, object], None]:
    """Add extra properties to the calling test.

    User properties become part of the test report and are available to the
    configured reporters, like JUnit XML.

    The fixture is callable with ``name, value``. The value is automatically
    XML-encoded.

    Example::

        def test_function(record_property):
            record_property("example_key", 1)
    """

    def append_property(name: str, value: object) -> None:
        request.node.user_properties.append((name, value))

    return append_property


@pytest.fixture
def record_xml_attribute(request: FixtureRequest) -> Callable[[str, object], None]:
    """Add extra xml attributes to the tag for the calling test.

    The fixture is callable with ``name, value``. The value is
    automatically XML-encoded.
    """

    # Declare noop
    def add_attr_noop(name: str, value: object) -> None:
        pass

    attr_func = add_attr_noop

    xml = request.config.stash.get(xml_key, None)
    if xml is not None:
        node_reporter = xml.node_reporter(request.node.nodeid)
        attr_func = node_reporter.add_attribute

    return attr_func


def ensure_directory(path: str) -> str:
    """
    Expand ~/$VARS and create the directory (and parents) if missing.
    Returns the normalized absolute path.
    """
    p = os.path.expanduser(os.path.expandvars(path))
    os.makedirs(p, exist_ok=True)
    return os.path.normpath(os.path.abspath(p))


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("terminal reporting")
    group.addoption(
        "--xml-junit-dir",
        action="store",
        dest="xmldir",
        metavar="DIR",
        type=ensure_directory,
        default=None,
        help="Write split‑suite JUnit‑XML files into this directory (will be created)",
    )


def pytest_configure(config: Config) -> None:
    """
    Configure the JUnit‑XML split‑suite plugin.

    Reads the `xmldir` option from pytest's configuration. If provided, and
    not running as a worker (e.g., under xdist), this hook creates a LogXML
    instance pointed at the given directory, stashes it for later retrieval,
    and registers it as a pytest plugin to capture test events.

    Ensures only the main process writes test reports.

    :param config: The pytest Config object containing CLI options and hooks.
    """
    xmldir = config.option.xmldir
    if xmldir and not hasattr(config, "workerinput"):
        config.stash[xml_key] = LogXML(xmldir)
        config.pluginmanager.register(config.stash[xml_key])


def pytest_unconfigure(config: Config) -> None:
    """
    Unconfigure the JUnit‑XML split‑suite plugin.

    Retrieves the stashed LogXML instance (if any), removes it from the stash,
    and unregisters it from the pytest plugin manager. Cleans up plugin
    registration after the session finishes to avoid side effects.

    :param config: The pytest Config object used during teardown.
    """
    xml = config.stash.get(xml_key, None)
    if xml:
        del config.stash[xml_key]
        config.pluginmanager.unregister(xml)


def mangle_test_address(address: str) -> list[str]:
    path, possible_open_bracket, params = address.partition("[")
    names = path.split("::")
    # Convert file path to dotted path.
    names[0] = names[0].replace(nodes.SEP, ".")
    names[0] = re.sub(r"\.py$", "", names[0])
    # Put any params back.
    names[-1] += possible_open_bracket + params
    return names


class LogXML:
    def __init__(  # type: ignore[no-untyped-def]
        self,
        output_dir,
        prefix: str | None = None,
        suite_name: str = "pytest",
        logging: str = "yes",
        report_duration: str = "total",
        log_passing_tests: bool = True,
    ) -> None:
        output_dir = os.path.expanduser(os.path.expandvars(output_dir))
        self.output_dir = os.path.normpath(os.path.abspath(output_dir))
        self.prefix = prefix
        self.suite_name = suite_name
        self.logging = logging
        self.log_passing_tests = log_passing_tests
        self.report_duration = report_duration
        self.stats: dict[str, int] = dict.fromkeys(["error", "passed", "failure", "skipped"], 0)
        self.node_reporters: dict[tuple[str | TestReport, object], _NodeReporter] = {}
        self.node_reporters_ordered: list[_NodeReporter] = []

        # List of reports that failed on call but teardown is pending.
        self.open_reports: list[TestReport] = []
        self.cnt_double_fail_tests = 0

    def finalize(self, report: TestReport) -> None:
        nodeid = getattr(report, "nodeid", report)
        # Local hack to handle xdist report order.
        workernode = getattr(report, "node", None)
        reporter = self.node_reporters.pop((nodeid, workernode))

        for propname, propvalue in report.user_properties:
            reporter.add_property(propname, str(propvalue))

        if reporter is not None:
            reporter.finalize()

    def node_reporter(self, report: TestReport | str) -> _NodeReporter:
        nodeid: str | TestReport = getattr(report, "nodeid", report)
        # Local hack to handle xdist report order.
        workernode = getattr(report, "node", None)

        key = nodeid, workernode

        if key in self.node_reporters:
            # TODO: breaks for --dist=each
            return self.node_reporters[key]

        reporter = _NodeReporter(nodeid, self)

        self.node_reporters[key] = reporter
        self.node_reporters_ordered.append(reporter)

        return reporter

    def add_stats(self, key: str) -> None:
        if key in self.stats:
            self.stats[key] += 1

    def _opentestcase(self, report: TestReport) -> _NodeReporter:
        reporter = self.node_reporter(report)
        reporter.record_testreport(report)
        return reporter

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        """Handle a setup/call/teardown report, generating the appropriate
        XML tags as necessary.

        Note: due to plugins like xdist, this hook may be called in interlaced
        order with reports from other nodes. For example:

        Usual call order:
            -> setup node1
            -> call node1
            -> teardown node1
            -> setup node2
            -> call node2
            -> teardown node2

        Possible call order in xdist:
            -> setup node1
            -> call node1
            -> setup node2
            -> call node2
            -> teardown node2
            -> teardown node1
        """
        close_report = None
        if report.passed:
            if report.when == "call":  # ignore setup/teardown
                reporter = self._opentestcase(report)
                reporter.append_pass(report)
        elif report.failed:
            if report.when == "teardown":
                # The following vars are needed when xdist plugin is used.
                report_wid = getattr(report, "worker_id", None)
                report_ii = getattr(report, "item_index", None)
                close_report = next(
                    (
                        rep
                        for rep in self.open_reports
                        if (
                            rep.nodeid == report.nodeid
                            and getattr(rep, "item_index", None) == report_ii
                            and getattr(rep, "worker_id", None) == report_wid
                        )
                    ),
                    None,
                )
                if close_report:
                    # We need to open new testcase in case we have failure in
                    # call and error in teardown in order to follow junit
                    # schema.
                    self.finalize(close_report)
                    self.cnt_double_fail_tests += 1
            reporter = self._opentestcase(report)
            if report.when == "call":
                reporter.append_failure(report)
                self.open_reports.append(report)
                if not self.log_passing_tests:
                    reporter.write_captured_output(report)
            else:
                reporter.append_error(report)
        elif report.skipped:
            reporter = self._opentestcase(report)
            reporter.append_skipped(report)
        self.update_testcase_duration(report)
        if report.when == "teardown":
            reporter = self._opentestcase(report)
            reporter.write_captured_output(report)

            self.finalize(report)
            report_wid = getattr(report, "worker_id", None)
            report_ii = getattr(report, "item_index", None)
            close_report = next(
                (
                    rep
                    for rep in self.open_reports
                    if (
                        rep.nodeid == report.nodeid
                        and getattr(rep, "item_index", None) == report_ii
                        and getattr(rep, "worker_id", None) == report_wid
                    )
                ),
                None,
            )
            if close_report:
                self.open_reports.remove(close_report)

    def update_testcase_duration(self, report: TestReport) -> None:
        """Accumulate total duration for nodeid from given report and update
        the Junit.testcase with the new total if already created."""
        if self.report_duration in {"total", report.when}:
            reporter = self.node_reporter(report)
            reporter.duration += getattr(report, "duration", 0.0)

    def pytest_collectreport(self, report: TestReport) -> None:
        """
        Handle collection-phase outcomes before any tests run.

        - If pytest fails to collect a test (syntax error, import error, etc.),
          we record it as a collection failure.
        - If pytest skips a collection (via xdist or other reasons), we record it
          as a collection‐skipped event.

        :param report: The TestReport object for the collection phase.
        """
        if not report.passed:
            reporter = self._opentestcase(report)
            if report.failed:
                reporter.append_collect_error(report)
            else:
                reporter.append_collect_skipped(report)

    # noinspection PyProtectedMember
    def pytest_internalerror(self, excrepr: ExceptionRepr) -> None:
        """
        Handle pytest’s own internal errors by emitting them as test errors.

        When pytest encounters an unexpected exception in its own machinery,
        this hook fires. We synthesize a “test” named 'internal' under the
        'pytest' suite so that CI systems still report the error cleanly.

        :param excrepr: The exception representation that pytest produced.
        """
        # Create (or fetch) a reporter for the synthetic 'internal' test
        reporter = self.node_reporter("internal")
        # Tag it as belonging to pytest itself
        reporter.attrs.update(classname="pytest", name="internal")
        # Record the exception as a standard JUnit <error> element
        reporter._add_simple("error", "internal error", str(excrepr))

    def pytest_sessionstart(self) -> None:
        """
        Called at the very start of the pytest session.

        Records the session start timestamp using pytest’s high-resolution timer.
        This timestamp is later used in pytest_sessionfinish to compute the total
        duration of the entire test run.
        """
        self.suite_start_time = timing.time()

    def pytest_sessionfinish(self) -> None:
        """
        After all tests complete, write a single JUnit XML file containing
        multiple <testsuite> elements grouped by test class.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        ts = datetime.fromtimestamp(self.suite_start_time, timezone.utc).astimezone().isoformat()

        root = ET.Element("testsuites")
        total_tests = total_failures = total_skipped = total_errors = total_time = 0.0

        # Group reporters by class
        groups: dict[str, list[_NodeReporter]] = defaultdict(list)
        for rpt in self.node_reporters_ordered:
            parts = rpt.id.split("::", 2)
            cls = parts[1] if len(parts) > 1 else parts[0]
            groups[cls].append(rpt)

        for cls_name, reps in groups.items():
            suite = ET.Element(
                "testsuite",
                {
                    "name": cls_name,
                    "file": reps[0].to_xml().get("file", ""),
                },
            )

            for r in reps:
                suite.append(r.to_xml())

            num_tests = len(reps)
            num_failures = len(suite.findall("testcase/failure"))
            num_skipped = len(suite.findall("testcase/skipped"))
            num_errors = len(suite.findall("testcase/error"))
            suite_time = sum(r.duration for r in reps)

            suite.set("tests", str(num_tests))
            suite.set("failures", str(num_failures))
            suite.set("skipped", str(num_skipped))
            suite.set("errors", str(num_errors))
            suite.set("time", f"{suite_time:.3f}")
            suite.set("timestamp", ts)
            suite.set("hostname", platform.node())

            root.append(suite)

            # Accumulate totals
            total_tests += num_tests
            total_failures += num_failures
            total_skipped += num_skipped
            total_errors += num_errors
            total_time += suite_time

        # Set attributes on <testsuites>
        root.set("tests", str(int(total_tests)))
        root.set("failures", str(int(total_failures)))
        root.set("skipped", str(int(total_skipped)))
        root.set("errors", str(int(total_errors)))
        root.set("time", f"{total_time:.3f}")
        root.set("timestamp", ts)
        root.set("hostname", platform.node())

        ET.indent(root, space="  ", level=0)
        path = os.path.join(self.output_dir, "report.xml")
        with open(path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>')
            f.write(ET.tostring(root, encoding="unicode"))

    def pytest_terminal_summary(self, terminalreporter: TerminalReporter) -> None:
        """
        Display a summary line after the entire test session.

        Writes a separator and a message pointing at the directory
        (or file) where your JUnit‑XML output was generated.

        If you’re in split‑suite mode, this directory will contain
        one XML per test class; otherwise it will be a single file.
        """
        terminalreporter.write_sep("-", f"generated xml files in: {self.output_dir}")


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    """Load the .env file for the entire test session."""
    load_dotenv()
