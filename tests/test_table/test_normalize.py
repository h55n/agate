from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase
from agate.type_tester import TypeTester


class TestNormalize(AgateTestCase):
    def setUp(self):
        self.rows = (
            (1, 'c', 4, 'a'),
            (2, 'e', 3, 'b'),
            (None, 'g', 2, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three', 'four']
        self.column_types = [self.number_type, self.text_type, self.number_type, self.text_type]

    def test_normalize(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize('one', 'three')

        normal_rows = (
            (1, 'three', 4),
            (2, 'three', 3),
            (None, 'three', 2)
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['one', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Number])

    def test_normalize_column_types(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize('one', 'three', column_types=[Text(), Text()])

        normal_rows = (
            (1, 'three', '4'),
            (2, 'three', '3'),
            (None, 'three', '2')
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['one', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Text])

    def test_normalize_column_type_tester(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize('one', 'three', column_types=TypeTester(force={'value': Text()}))

        normal_rows = (
            (1, 'three', '4'),
            (2, 'three', '3'),
            (None, 'three', '2')
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['one', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Text])

    def test_normalize_does_not_mutate_type_tester(self):
        forced_value_type = Text()
        tester = TypeTester(force={'value': forced_value_type})
        force = tester._force
        table = Table(self.rows, self.column_names, self.column_types)

        normalized = table.normalize('one', 'three', column_types=tester)

        self.assertColumnTypes(normalized, [Number, Text, Text])
        self.assertIs(tester._force, force)
        self.assertEqual(tester._force, {'value': forced_value_type})

    def test_normalize_reuses_type_tester_with_different_key_types(self):
        tester = TypeTester()
        text_table = Table([('10', 2)], ['key', 'amount'], [Text(), Number()])
        number_table = Table([(10, 2)], ['key', 'amount'], [Number(), Number()])

        text_result = text_table.normalize('key', 'amount', column_types=tester)
        number_result = number_table.normalize('key', 'amount', column_types=tester)

        self.assertColumnTypes(text_result, [Text, Text, Number])
        self.assertColumnTypes(number_result, [Number, Text, Number])
        self.assertRows(number_result, [(10, 'amount', 2)])

    def test_normalize_type_tester_key_override_takes_precedence(self):
        text_type = Text()
        tester = TypeTester(force={'one': text_type, 'value': text_type})
        table = Table(self.rows, self.column_names, self.column_types)

        normalized = table.normalize('one', 'three', column_types=tester)

        self.assertColumnTypes(normalized, [Text, Text, Text])
        self.assertEqual(tester._force, {'one': text_type, 'value': text_type})

    def test_normalize_preserves_type_tester_options(self):
        tester = TypeTester(limit=0)
        table = Table(self.rows, self.column_names, self.column_types)

        normalized = table.normalize('one', 'three', column_types=tester)

        self.assertColumnTypes(normalized, [Text, Text, Text])
        self.assertEqual(tester._limit, 0)
        self.assertEqual(tester._force, {})

    def test_normalize_multiple_fields(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize('one', ['three', 'four'])

        normal_rows = (
            (1, 'three', '4'),
            (1, 'four', 'a'),
            (2, 'three', '3'),
            (2, 'four', 'b'),
            (None, 'three', '2'),
            (None, 'four', 'c')
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['one', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Text])

    def test_normalize_multiple_keys(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize(['one', 'two'], ['three', 'four'])

        normal_rows = (
            (1, 'c', 'three', '4'),
            (1, 'c', 'four', 'a'),
            (2, 'e', 'three', '3'),
            (2, 'e', 'four', 'b'),
            (None, 'g', 'three', '2'),
            (None, 'g', 'four', 'c')
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['one', 'two', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Text, Text])

    def test_normalize_change_order(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize('three', ['one', 'four'])

        normal_rows = (
            (4, 'one', '1'),
            (4, 'four', 'a'),
            (3, 'one', '2'),
            (3, 'four', 'b'),
            (2, 'one', None),
            (2, 'four', 'c')
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['three', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Text])
