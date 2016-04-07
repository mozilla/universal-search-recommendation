"""
Copied from
https://github.com/mozilla/testpilot/blob/master/testpilot/base/tests.py
"""
import json
import logging
import os
from unittest import TestCase

from testfixtures import LogCapture
import jsonschema

from recommendation.mozlog.formatter import MozLogFormatter

logger = logging.getLogger(__name__)


class TestMozLogFormatter(TestCase):

    def setUp(self):
        self.handler = LogCapture()
        self.logger_name = "TestingTestPilot"
        self.formatter = MozLogFormatter(logger_name=self.logger_name)

    def tearDown(self):
        self.handler.uninstall()

    def _fetchLastLog(self):
        self.assertEquals(len(self.handler.records), 1)
        details = json.loads(self.formatter.format(self.handler.records[0]))
        jsonschema.validate(details, JSON_LOGGING_SCHEMA)
        return details

    def test_basic_operation(self):
        """Ensure log formatter contains all the expected fields and values"""
        message_text = "simple test"
        logging.debug(message_text)
        details = self._fetchLastLog()

        expected_present = ["Timestamp", "Hostname"]
        for key in expected_present:
            self.assertTrue(key in details)

        expected_meta = {
            "Severity": 7,
            "Type": "root",
            "Pid": os.getpid(),
            "Logger": self.logger_name,
            "EnvVersion": self.formatter.LOGGING_FORMAT_VERSION
        }
        for key, value in expected_meta.items():
            self.assertEquals(value, details[key])

        self.assertEquals(details['Fields']['message'], message_text)

    def test_custom_paramters(self):
        """Ensure log formatter can handle custom parameters"""
        logger = logging.getLogger("mozsvc.test.test_logging")
        logger.warn("custom test %s", "one", extra={"more": "stuff"})
        details = self._fetchLastLog()

        self.assertEquals(details["Type"], "mozsvc.test.test_logging")
        self.assertEquals(details["Severity"], 4)

        fields = details['Fields']
        self.assertEquals(fields["message"], "custom test one")
        self.assertEquals(fields["more"], "stuff")

    def test_logging_error_tracebacks(self):
        """Ensure log formatter includes exception traceback information"""
        try:
            raise ValueError("\n")
        except Exception:
            logging.exception("there was an error")
        details = self._fetchLastLog()

        expected_meta = {
            "Severity": 3,
        }
        for key, value in expected_meta.items():
            self.assertEquals(value, details[key])

        fields = details['Fields']
        expected_fields = {
            'message': 'there was an error',
            'error': "ValueError('\\n',)"
        }
        for key, value in expected_fields.items():
            self.assertEquals(value, fields[key])

        self.assertTrue(fields['traceback'].startswith('Uncaught exception:'))
        self.assertTrue("<class 'ValueError'>" in fields['traceback'])


# https://mana.mozilla.org/wiki/pages/viewpage.action?pageId=42895640
JSON_LOGGING_SCHEMA = json.loads("""
{
    "type":"object",
    "required":["Timestamp"],
    "properties":{
        "Timestamp":{
            "type":"integer",
            "minimum":0
        },
        "Type":{
            "type":"string"
        },
        "Logger":{
            "type":"string"
        },
        "Hostname":{
            "type":"string",
            "format":"hostname"
        },
        "EnvVersion":{
            "type":"string",
            "pattern":"^\\d+(?:\\.\\d+){0,2}$"
        },
        "Severity":{
            "type":"integer",
            "minimum":0,
            "maximum":7
        },
        "Pid":{
            "type":"integer",
            "minimum":0
        },
        "Fields":{
            "type":"object",
            "minProperties":1,
            "additionalProperties":{
                "anyOf": [
                    { "$ref": "#/definitions/field_value"},
                    { "$ref": "#/definitions/field_array"},
                    { "$ref": "#/definitions/field_object"}
                ]
            }
        }
    },
    "definitions":{
        "field_value":{
            "type":["string", "number", "boolean"]
        },
        "field_array":{
            "type":"array",
            "minItems": 1,
            "oneOf": [
                    {"items": {"type":"string"}},
                    {"items": {"type":"number"}},
                    {"items": {"type":"boolean"}}
            ]
        },
        "field_object":{
            "type":"object",
            "required":["value"],
            "properties":{
                "value":{
                    "oneOf": [
                        { "$ref": "#/definitions/field_value" },
                        { "$ref": "#/definitions/field_array" }
                    ]
                },
                "representation":{"type":"string"}
            }
        }
    }
}
""".replace("\\", "\\\\"))  # HACK: Fix escaping for easy copy/paste
