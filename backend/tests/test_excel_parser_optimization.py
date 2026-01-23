
import sys
import os
import unittest

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.excel_parser import ExcelParser

class TestExcelParserOptimization(unittest.TestCase):
    def test_normalize_name(self):
        parser = ExcelParser("dummy.xlsx")

        test_cases = [
            ("ООО Рога и Копыта", "рога и копыта"),
            ("ЗАО 'Инновации'", "инновации"),
            ("ИП Иванов И.И.", "иванов и.и."),
            ("   Product Name   ", "product name"),
            ("Some Product LLC", "some product llc"),
            ("Mixed Case COMPANY", "mixed case company"),
            ("ООО 'Some Company' ООО", "some company"),
            ("Empty Name", "empty name"), # Not empty string, but string "Empty Name"
            ("", ""),
            ("Normal Name", "normal name"),
            ("ООО ЗАО Company", "company"), # Original logic: removes "ООО ", then "ЗАО "
            ("ЗАО ООО Company", "ооо company"), # Original logic: removes "ЗАО ", "ООО" remains because order matters
            ("'Quote'", "quote"),
            ('"Quote"', "quote"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                self.assertEqual(parser._normalize_name(input_name), expected)

if __name__ == '__main__':
    unittest.main()
